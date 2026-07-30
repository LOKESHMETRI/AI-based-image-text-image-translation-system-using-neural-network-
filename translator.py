"""
translator.py
--------------
Core AI logic for the Image Text Translation system.

Two neural networks are used:
1. EasyOCR       -> a CNN + LSTM + CTC based deep learning OCR model
                    that detects and reads text from images.
2. MarianMT      -> a Transformer-based neural machine translation
                    model (Helsinki-NLP/opus-mt-*) that translates
                    the extracted text into the target language.

Both models are downloaded automatically from their respective hubs
the first time they are used, and are cached afterward.
"""

import io
import threading
from functools import lru_cache

import easyocr
import numpy as np
from PIL import Image
from transformers import MarianMTModel, MarianTokenizer

# ---------------------------------------------------------------------------
# OCR (Neural Network #1)
# ---------------------------------------------------------------------------

# EasyOCR reader is expensive to construct (loads a deep learning model),
# so we build it once, lazily, and reuse it across requests.
_ocr_lock = threading.Lock()
_ocr_readers = {}


def get_ocr_reader(langs=("en",)):
    """Return a cached EasyOCR Reader for the given source language(s)."""
    key = tuple(sorted(langs))
    with _ocr_lock:
        if key not in _ocr_readers:
            # gpu=False for portability; set gpu=True if CUDA is available
            _ocr_readers[key] = easyocr.Reader(list(key), gpu=False)
        return _ocr_readers[key]


def extract_text(image_bytes: bytes, source_lang="en"):
    """
    Run the OCR neural network over an uploaded image.

    Returns a list of dicts: [{"text": str, "confidence": float, "box": [[x,y],...]}]
    """
    reader = get_ocr_reader((source_lang,))
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = reader.readtext(np.array(image))

    detections = []
    for box, text, confidence in results:
        detections.append(
            {
                "text": text,
                "confidence": round(float(confidence), 4),
                "box": [[float(x), float(y)] for x, y in box],
            }
        )
    return detections


# ---------------------------------------------------------------------------
# Translation (Neural Network #2)
# ---------------------------------------------------------------------------

# Maps simple language codes to the correct pretrained MarianMT checkpoint.
# Helsinki-NLP publishes hundreds of language-pair models on HuggingFace Hub;
# add more pairs here as needed.
MODEL_MAP = {
    ("en", "mr"): "Helsinki-NLP/opus-mt-en-mr",
    ("en", "kn"): "Helsinki-NLP/opus-mt-en-dra",
    ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
    ("mr", "en"): "Helsinki-NLP/opus-mt-mr-en",
    ("kn", "en"): "Helsinki-NLP/opus-mt-kn-en",

}
LANGUAGE_TAGS = { ("en", "kn"): ">>kan<<" }

_model_lock = threading.Lock()
_model_cache = {}


def _load_model(src: str, tgt: str):
    key = (src, tgt)
    if key not in MODEL_MAP:
        raise ValueError(
            f"No translation model configured for {src} -> {tgt}. "
            f"Add it to MODEL_MAP in translator.py."
        )
    checkpoint = MODEL_MAP[key]

    with _model_lock:
        if key not in _model_cache:
            tokenizer = MarianTokenizer.from_pretrained(checkpoint)
            model = MarianMTModel.from_pretrained(checkpoint)
            model.eval()
            _model_cache[key] = (tokenizer, model)
        return _model_cache[key]


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Run the MarianMT transformer neural network to translate text."""
    if not text.strip():
        return ""

    tokenizer, model = _load_model(source_lang, target_lang)
    batch = tokenizer([text], return_tensors="pt", padding=True, truncation=True)
    generated = model.generate(**batch, max_length=512)
    translated = tokenizer.batch_decode(generated, skip_special_tokens=True)
    return translated[0]


def translate_image(image_bytes: bytes, source_lang="en", target_lang="fr"):
    """
    Full pipeline: OCR the image, then translate every detected text region.
    Returns per-region results plus the full joined original/translated text.
    """
    detections = extract_text(image_bytes, source_lang=source_lang)

    for det in detections:
        det["translated_text"] = translate_text(det["text"], source_lang, target_lang)

    full_original = " ".join(d["text"] for d in detections)
    full_translated = translate_text(full_original, source_lang, target_lang) if full_original else ""

    return {
        "detections": detections,
        "full_original_text": full_original,
        "full_translated_text": full_translated,
    }