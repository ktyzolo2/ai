import os
import cv2
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

def get_frame_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    success, image = cap.read()
    image_path = "temp_frame.jpg"
    if success:
        cv2.imwrite(image_path, image)
    cap.release()
    return image_path

def extract_text_via_api(image_path):
    url = "https://api.ocr.space/parse/image"
    payload = {
        'isOverlayRequired': False,
        'apikey': 'helloworld', 
        'language': 'eng'       
    }
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, data=payload, files=files)
    
    result = response.json()
    if result.get('ParsedResults'):
        return result['ParsedResults'][0]['ParsedText']
    return "រកមិនឃើញអក្សរទេ"

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    video = message.video or message.document
    
    if not video:
        await message.reply_text("សូមផ្ញើមកជាវីដេអូ ឬ Document ជាវីដេអូ!")
        return

    await message.reply_text("⏳ កំពុងទាញយក និងអានអក្សរពីវីដេអូ សូមរង់ចាំបន្តិច...")
    
    file = await context.bot.get_file(video.file_id)
    video_path = "temp_video.mp4"
    await file.download_to_drive(video_path)
    
    try:
        img_path = get_frame_from_video(video_path)
        extracted_text = extract_text_via_api(img_path)
        
        if not extracted_text.strip():
            extracted_text = "រកមិនឃើញអក្សរច្បាស់លាស់នៅក្នុងវីដេអូនេះទេ។"
            
        await message.reply_text(f"📄 **អក្សរដែលរកឃើញ៖**\n\n{extracted_text}")
        
        if os.path.exists(img_path):
            os.remove(img_path)
            
    except Exception as e:
        await message.reply_text(f"⚠️ កំហុសឆ្គង: {str(e)}")
        
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

if __name__ == '__main__':
    TOKEN = "9186643956:AAGP-k8So23wqyApz12yCaMhGpLnYJCfw6k"
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    
    print("🤖 Bot កំពុងដំណើរការ...")
    app.run_polling()
