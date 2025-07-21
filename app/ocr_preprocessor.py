import cv2


def preprocess(path: str) -> str:
    """Aplica un preprocesamiento básico para mejorar el OCR."""

    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    # Aumentar tamaño para facilitar el reconocimiento
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Binarización (Otsu)
    _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Filtros de ruido
    img = cv2.medianBlur(img, 3)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    out_path = path.replace(".jpg", "_pre.jpg")
    cv2.imwrite(out_path, img)
    return out_path
