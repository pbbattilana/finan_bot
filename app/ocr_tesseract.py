import pytesseract

def extract_text(path):
    # Asegúrate de tener tesseract instalado en tu sistema
    text = pytesseract.image_to_string(path, lang='eng+spa')
    return text
