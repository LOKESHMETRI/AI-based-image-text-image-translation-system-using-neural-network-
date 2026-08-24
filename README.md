# Synapse — Neural Translation

A single-file HTML app that translates text and images between languages, with an animated encoder → attention → decoder visualization.

## Features

- **Text translation** — type or paste text, pick source/target languages, translate. Swap button flips source and target.
- **Image translation** — upload or drag-and-drop an image, select the language the text in the image is written in, and Synapse OCRs it and translates the result.
- **17+ languages** including English, Spanish, French, German, Hindi, Marathi, Kannada, Tamil, Telugu, Bengali, Gujarati, Arabic, Chinese, Japanese, Korean, Portuguese, Russian, Italian, Dutch, Polish, Turkish, Vietnamese, and Thai.
- Auto re-OCRs if you change the image's language after uploading.

## How it works

- **Text translation**: [MyMemory Translation API](https://mymemory.translated.net/) (free, no API key required).
- **Image OCR**: [Tesseract.js](https://tesseract.projectnaidu.com/) running entirely in-browser — no image data is uploaded anywhere.

## Usage

1. Open `synapse-translator.html` in any modern browser (no build step, no server needed).
2. **Text tab**: enter text, choose languages, click Translate.
3. **Image tab**: choose the image's text language, upload an image, wait for OCR to finish, then click "Translate extracted text."

## Notes / limitations

- Requires an internet connection (fetches the MyMemory API and downloads Tesseract language data on first use per language).
- OCR accuracy depends on image clarity — clean, high-contrast, non-handwritten text works best.
- "Detect language" in the Text tab currently falls back to English as the assumed source, since the MyMemory API requires an explicit source language.
- MyMemory's free tier has a modest daily character quota; for heavy use you'd want an API key or a paid translation provider.

## File

- `synapse-translator.html` — the entire app (HTML/CSS/JS in one file).
