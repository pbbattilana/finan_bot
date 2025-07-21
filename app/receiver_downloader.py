import os
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from bot_handler import process_image

TOKEN = os.environ["TELEGRAM_TOKEN"]    # <- lee del entorno

def handle_photo(update: Update, ctx: CallbackContext):
    photo = update.message.photo[-1]
    file  = photo.get_file()
    path  = f"downloads/{photo.file_id}.jpg"
    file.download(path)
    ctx.bot.send_message(chat_id=update.effective_chat.id,
                         text="Imagen recibida, procesando OCR…")
    process_image(path, update, ctx)

updater = Updater(TOKEN, use_context=True)  # v13.x usa Updater, no v20+. :contentReference[oaicite:1]{index=1}
updater.dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
updater.start_polling()
updater.idle()