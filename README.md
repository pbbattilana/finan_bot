# Finan Bot

Este proyecto implementa un bot de Telegram que recibe fotos de comprobantes de pago, realiza OCR para extraer la fecha, monto y número de comprobante y registra esa información en una base de datos PostgreSQL.

## Estructura del proyecto

- **Dockerfile**: construye la imagen basada en `python:3.11-slim`, instala Tesseract y define la ejecución de `receiver_downloader.py`.
- **docker-compose.yml**: levanta dos servicios: el bot y la base de datos Postgres. El código se monta en un volumen para facilitar el desarrollo.
- **app/**: contiene todo el código en Python.
  - `receiver_downloader.py`: arranca el bot y maneja la recepción de fotos. Utiliza `Updater` de `python-telegram-bot` v13. Aún mantiene un comentario residual ``":contentReference[oaicite:1]{index=1}`` en la inicialización.
  - `bot_handler.py`: coordina el flujo completo: preprocesa la imagen, ejecuta OCR, extrae los campos vía regex y guarda en la base de datos.
  - `ocr_preprocessor.py` y `ocr_easyocr.py`: realizan el tratamiento de la imagen con OpenCV y el OCR con EasyOCR.
  - `regex.py`: define las expresiones regulares para identificar fecha, monto y número de comprobante.
  - `bd_sqlalchemy.py`: configuración de SQLAlchemy y función `save_record` que persiste los pagos.
  - `requirements.txt`: dependencias de la aplicación.
  - `parser/`: paquete con parsers especializados por tipo de comprobante (pago, transferencia y servicio) de Ueno Bank.

## Ejecución rápida

1. Copia un archivo `.env` con las variables necesarias. Debe incluir al menos `TELEGRAM_TOKEN`, `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`.
2. Construye y ejecuta los contenedores:

```bash
docker compose up --build
```

3. Envía una foto del comprobante al bot. El bot descargará la imagen, aplicará OCR y, si encuentra los datos necesarios, almacenará el registro en la base de datos.

La base queda accesible en el puerto 5432 según la configuración de `docker-compose.yml`.

## Aspectos clave

- Preprocesamiento de imágenes y OCR se implementan con OpenCV y EasyOCR, como se ve en `ocr_preprocessor.py` y `ocr_easyocr.py`【F:app/ocr_preprocessor.py†L1-L12】【F:app/ocr_easyocr.py†L1-L5】.
- Las expresiones regulares que extraen fecha, monto y cuenta están definidas en `regex.py`【F:app/regex.py†L3-L35】.
- La conexión con PostgreSQL se maneja mediante SQLAlchemy en `bd_sqlalchemy.py`【F:app/bd_sqlalchemy.py†L1-L33】.
- La inicialización del bot muestra la cadena residual en `receiver_downloader.py`【F:app/receiver_downloader.py†L17-L18】.
