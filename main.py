import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

def extract_text_via_api(image_path):
    url = "https://api.ocr.space/parse/image"
    payload = {
        'isOverlayRequired': False,
        'apikey': 'helloworld', # អ្នកអាចប្តូរជា API Key ផ្ទាល់ខ្លួនរបស់អ្នកនៅពេលหลัง
        'language': 'chs'       # ភាសាអក្សរចិនសាមញ្ញ (Chinese Simplified)
    }
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, data=payload, files=files)
    
    result = response.json()
    if result.get('ParsedResults'):
        parsed_text = result['ParsedResults'][0]['ParsedText'].strip()
        if parsed_text:
            return parsed_text
            
    return ""

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # ពិនិត្យមើលថាតើមានរូបភាព ឬ File រូបភាពដែរឬទេ
    photo = message.photo
    document = message.document
    
    if not photo and not document:
        await message.reply_text("សូមផ្ញើមកជារូបភាព (Photo) ដើម្បីឱ្យខ្ញុំជួយអានអក្សរជូន!")
        return

    await message.reply_text("⏳ កំពុងអានអក្សរពីរូបភាព... សូមរង់ចាំបន្តិច។")
    
    # យក File ID របស់រូបភាពដែលមានគុណភាពខ្ពស់ជាងគេ
    if photo:
        file_obj = await context.bot.get_file(photo[-1].file_id)
    else:
        file_obj = await context.bot.get_file(document.file_id)
        
    image_path = "temp_image.jpg"
    await file_obj.download_to_drive(image_path)
    
    try:
        extracted_text = extract_text_via_api(image_path)
        
        if not extracted_text:
            extracted_text = "រកមិនឃើញអក្សរច្បាស់លាស់នៅក្នុងរូបភាពនេះទេ។"
            
        await message.reply_text(f"📄 **អក្សរដែលរកឃើញ៖**\n\n{extracted_text}")
        
    except Exception as e:
        await message.reply_text(f"⚠️ កំហុសឆ្គង: {str(e)}")
        
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == '__main__':
    TOKEN = "9186643956:AAGP-k8So23wqyApz12yCaMhGpLnYJCfw6k"
    
    app = ApplicationBuilder().token(TOKEN).build()
    # ដូរ Filter មកទទួលយករូបភាព និង Document រូបភាពវិញ
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, handle_image))
    
    print("🤖 Bot រូបភាពកំពុងដំណើរការ...")
    app.run_polling()
