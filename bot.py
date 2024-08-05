from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters, CallbackContext
import requests
import os
import logging
from time import time, sleep

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


DOODSTREAM_API_KEY = '54845tb4kbkj7svvyig18'
TELEGRAM_BOT_TOKEN = '6051397318:AAHxaVj81gfjjfxAcK2lE76EaAwvpwr7a2g'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Send me a video file and I will upload it to DoodStream.')



def upload_to_doodstream(file_path: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
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
            
            total_size = os.path.getsize(file_path)
            progress = 0
            start_time = time()
            last_update_time = start_time

            with open(file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(file_path), f, 'video/mp4')
                }
                response = requests.post(
                    upload_server,
                    files=files,
                    data={'key': DOODSTREAM_API_KEY}
                )
                response.raise_for_status()
                progress += len(f.read())
                percent_complete = (progress / total_size) * 100
                current_time = time()

                
                    
                
            data = response.json()
            print(data)
        if 'files' not in data or len(data['files']) == 0:
            raise ValueError("Unexpected response format: " + str(data))
        
        filecode = data['files'][0]['filecode']
        return filecode

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")

    except ValueError as e:
        logger.error(f"JSON decode failed: {e}")

    return None
    


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    video = update.message.video
    file_id = video.file_id
    file = await context.bot.get_file(file_id)
    file_path = f'./{file_id}.mp4'
    await file.download_to_drive(file_path)
    uploading_message = await update.message.reply_text('Uploading...')
    await update.message.reply_text(f'{file.file_path}')

    try:
        
        video_link = upload_to_doodstream(file_path, update, context)
        if video_link:
            await update.message.reply_text(f'{video_link}')
            
        else:
            
            retry_msg = await update.message.reply_text('Failed to upload the video to DoodStream.')

    finally:
        await uploading_message.delete()
        os.remove(file_path)

async def retry_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    file_id = query.data.split(':')[1]
    file = await context.bot.get_file(file_id)
    file_path = f'./{file_id}.mp4'
    await file.download_to_drive(file_path)
    await retry_msg.delete()
    uploading_message = await query.message.reply_text('Retrying upload...')
    

    try:
        video_link = upload_to_doodstream(file_path, query, context)
        if video_link:
            await query.message.reply_text(f'{video_link}')
        
        else:
            keyboard = [[InlineKeyboardButton("Try Again", callback_data=f"retry:{file_path}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            retry_msg = await query.message.reply_text('Failed to upload the video to DoodStream.', reply_markup=reply_markup)
    finally:
        await uploading_message.delete()
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
