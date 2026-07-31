AI Image Text Translator
An AI-based system that extracts text from images and translates it,
built on two neural networks:
EasyOCR — a deep learning OCR model (CNN feature extractor +
LSTM sequence model + CTC decoding) that detects and reads text
from an uploaded image.
MarianMT — a Transformer-based neural machine translation
model (Helsinki-NLP opus-mt-* checkpoints from HuggingFace) that
translates the extracted text into the target language.
Architecture
Code
Project structure
Code
Setup
Backend
Bash
The first request will download the EasyOCR and MarianMT model
weights automatically (requires internet access) and cache them
locally. The API then runs at http://localhost:5000.
Frontend
No build step required — it's plain HTML/CSS/JS.
Bash
Open http://localhost:8000 in a browser. Make sure
API_BASE_URL in script.js points at your running backend.
API
POST /api/translate-image
Form-data fields:
image (file, required)
source_lang (string, default en)
target_lang (string, default fr)
Response:
Json
GET /languages
Lists the currently configured source→target language pairs.
Extending
Add languages: add entries to MODEL_MAP in translator.py
with the matching Helsinki-NLP/opus-mt-<src>-<tgt> checkpoint
(browse available pairs on the HuggingFace Hub).
GPU acceleration: set gpu=True in easyocr.Reader(...) and
install a CUDA-enabled torch build for much faster OCR.
Draw translated text back onto the image: the box coordinates
returned per detection can be used with Pillow to overlay translated
text directly on the original image.
Swap in a different MT model: e.g. NLLB-200 or M2M100 for
broader multilingual coverage — same generate() pattern applies.
Notes
Running the backend requires enough disk/RAM to hold both model
families (a few hundred MB each) — first load per language pair
is slower since it downloads and initializes the model.
For production, put the Flask app behind gunicorn/uwsgi and
add request size limits + auth as needed.
