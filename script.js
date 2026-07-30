// Point this to wherever the Flask backend is running.
const API_BASE_URL = "http://localhost:5000";

const imageInput = document.getElementById("imageInput");
const dropZone = document.getElementById("dropZone");
const uploadText = document.getElementById("uploadText");
const previewImg = document.getElementById("previewImg");
const translateBtn = document.getElementById("translateBtn");
const sourceLang = document.getElementById("sourceLang");
const targetLang = document.getElementById("targetLang");
const originalTextEl = document.getElementById("originalText");
const translatedTextEl = document.getElementById("translatedText");
const statusEl = document.getElementById("status");

let selectedFile = null;

dropZone.addEventListener("click", () => imageInput.click());

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.style.borderColor = "#38bdf8";
});

dropZone.addEventListener("dragleave", () => {
  dropZone.style.borderColor = "#475569";
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.style.borderColor = "#475569";
  if (e.dataTransfer.files.length) {
    handleFile(e.dataTransfer.files[0]);
  }
});

imageInput.addEventListener("change", (e) => {
  if (e.target.files.length) {
    handleFile(e.target.files[0]);
  }
});

function handleFile(file) {
  if (!file.type.startsWith("image/")) {
    setStatus("Please choose an image file.");
    return;
  }
  selectedFile = file;
  uploadText.textContent = file.name;

  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    previewImg.style.display = "block";
  };
  reader.readAsDataURL(file);

  translateBtn.disabled = false;
  setStatus("");
}

translateBtn.addEventListener("click", async () => {
  if (!selectedFile) return;

  translateBtn.disabled = true;
  setStatus("Running OCR + translation models... this can take a moment on first run.");
  originalTextEl.textContent = "";
  translatedTextEl.textContent = "";

  const formData = new FormData();
  formData.append("image", selectedFile);
  formData.append("source_lang", sourceLang.value);
  formData.append("target_lang", targetLang.value);

  try {
    const res = await fetch(`${API_BASE_URL}/api/translate-image`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (!res.ok) {
      setStatus(data.error || "Something went wrong.");
      return;
    }

    originalTextEl.textContent = data.full_original_text || "(no text detected)";
    translatedTextEl.textContent = data.full_translated_text || "(no translation)";
    setStatus(`Detected ${data.detections.length} text region(s).`);
  } catch (err) {
    setStatus("Could not reach the backend. Is the Flask server running?");
    console.error(err);
  } finally {
    translateBtn.disabled = false;
  }
});

function setStatus(msg) {
  statusEl.textContent = msg;
}