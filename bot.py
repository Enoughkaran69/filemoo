import os
import requests
from telegram import Update, Bot
from telegram.ext import Updater, Application, CommandHandler, MessageHandler, ContextTypes, filters, CallbackContext
import requests
import os
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace these with your actual tokens
TELEGRAM_BOT_TOKEN = '6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g'
DOODSTREAM_API_KEY = '54845tb4kbkj7svvyig18'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me a video file and I will upload it to DoodStream.')


def upload_to_doodstream(file_path: str) -> str:
    url = 'https://filemoonapi.com/api/upload/server'
params = {
    'key': DOODSTREAM_API_KEY
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    print("Response:", response.json())
    data = response.json()
    if 'result' in data:
        upload_server = data['result']
        print(upload_server)
except requests.exceptions.RequestException as e:
    print(f"HTTP Request failed: {e}")
       

 files = {
            'file': open(file_path, 'rb')
        }
        response = requests.post(upload_server, files=files, data={'key': DOODSTREAM_API_KEY})
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            print("Response content is not valid JSON")
            return None

        if 'result' not in data or 'filecode' not in data['result']:
            raise ValueError("Unexpected response format: " + str(data))

        return data['result']['filecode']
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None
    except ValueError as e:
        print(f"JSON decode failed: {e}")
        return None

    

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video = update.message.video
    file_id = video.file_id
    file = await context.bot.get_file(file_id)
    file_path = f'./{file_id}.mp4'
    await file.download_to_drive(file_path)

    try:
        video_link = upload_to_doodstream(file_path)
        if video_link:
            await update.message.reply_text(f'Here is your video link: {video_link}')
        else:
            await update.message.reply_text('Failed to upload the video to DoodStream.')
            await update.message.reply_text(upload_server)
    finally:
        os.remove(file_path)

def set_webhook():
    webhook_url = 'https://filemoo.onrender.com'
    response = requests.get(f'https://api.telegram.org/bot6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g/setWebhook?url={webhook_url}')
    return response.json()

def main() -> None:
    application = Application.builder().token('6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
   

    set_webhook()  # Set webhook if not already set

    application.run_webhook(
        listen='0.0.0.0',
        port=8443,
        url_path='6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g',
        webhook_url=f'https://filemoo.onrender.com/6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g'
    )


if __name__ == '__main__':
    main()
