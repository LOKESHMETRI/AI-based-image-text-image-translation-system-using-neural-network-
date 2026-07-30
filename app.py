"""
app.py
------
Flask backend for the AI Image Text Translation system.

Endpoints:
  GET  /health              -> simple health check
  GET  /languages           -> supported language pairs
  POST /api/translate-image -> upload an image, get OCR + translated text back
"""

from flask import Flask, request, jsonify
from flask_cors import CORS

from translator import translate_image, MODEL_MAP

app = Flask(__name__)
CORS(app)  # allow the frontend (served separately) to call this API

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/languages", methods=["GET"])
def languages():
    pairs = [{"source": s, "target": t} for (s, t) in MODEL_MAP.keys()]
    return jsonify({"supported_pairs": pairs})


@app.route("/api/translate-image", methods=["POST"])
def translate_image_endpoint():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided (field name must be 'image')"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"Unsupported file type: {file.filename}"}), 400

    source_lang = request.form.get("source_lang", "en")
    target_lang = request.form.get("target_lang", "fr")

    try:
        image_bytes = file.read()
        result = translate_image(image_bytes, source_lang=source_lang, target_lang=target_lang)
        return jsonify(result)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": f"Internal error: {e}"}), 500


if __name__ == "__main__":
    # In production, run behind gunicorn/uwsgi instead of the dev server.
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)