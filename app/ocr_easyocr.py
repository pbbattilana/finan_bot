import easyocr
reader = easyocr.Reader(['en','es'])
def extract_text_easy(path):
    result = reader.readtext(path, detail=0)
    return "\n".join(result)
