import easyocr
import unicodedata

# Utilizar únicamente español y desactivar GPU
reader = easyocr.Reader(["es"], gpu=False)


def extract_text_easy(path: str) -> str:
    """Extrae texto de una imagen usando EasyOCR."""

    result = reader.readtext(path, detail=0, paragraph=True)
    text = "\n".join(result)
    # Normalizar unicode para reducir caracteres extraños
    return unicodedata.normalize("NFKC", text)
