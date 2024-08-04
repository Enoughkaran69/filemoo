import os
import requests
from telegram import Update, Bot
from telegram.ext import Updater, Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests
import os
# Replace these with your actual tokens
TELEGRAM_BOT_TOKEN = '6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g'
DOODSTREAM_API_KEY = '54845tb4kbkj7svvyig18'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send me a video file and I will upload it to DoodStream.')

def upload_to_doodstream(file_path: str) -> str:
    url = 'https://filemoonapi.com/api/upload/server'
    params = {
        'key': DOODSTREAM_API_KEY
    }
    response = requests.get(url, params=params)
    upload_server = response.json()['result']['server']

    files = {
        'file': open(file_path, 'rb')
    }
    response = requests.post(f'{upload_server}/upload', files=files, data={'key': DOODSTREAM_API_KEY})
    return response.json()['result']['filecode']

def handle_video(update: Update, context: CallbackContext) -> None:
    video = update.message.video
    file_id = video.file_id
    file = context.bot.get_file(file_id)
    file_path = f'./{file_id}.mp4'
    file.download(file_path)

    try:
        video_link = upload_to_doodstream(file_path)
        update.message.reply_text(f'Here is your video link: {video_link}')
    finally:
        os.remove(file_path)

def set_webhook():
    webhook_url = 'https://filemoo.onrender.com'
    response = requests.get(f'https://api.telegram.org/bot6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g/setWebhook?url={webhook_url}')
    return response.json()

def main() -> None:
    application = Application.builder().token('6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(Filters.video, handle_video))
   

    set_webhook()  # Set webhook if not already set

    application.run_webhook(
        listen='0.0.0.0',
        port=8443,
        url_path='6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g',
        webhook_url=f'https://filemoo.onrender.com/6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g'
    )


if __name__ == '__main__':
    main()
