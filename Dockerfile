FROM python:3.11-slim

# Paquetes del sistema que necesita OpenCV y Tesseract
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr tesseract-ocr-spa libgl1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalación de requirements por separado
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# No se copia el código, se monta con volumen
CMD ["python", "receiver_downloader.py"]
