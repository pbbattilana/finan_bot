import cv2

def preprocess(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    # Binarización adaptativa
    img = cv2.adaptiveThreshold(img, 255,
                                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 11, 2)
    # Denoising
    img = cv2.fastNlMeansDenoising(img, None, 30, 7, 21)
    cv2.imwrite(path.replace(".jpg", "_pre.jpg"), img)
    return path.replace(".jpg", "_pre.jpg")
