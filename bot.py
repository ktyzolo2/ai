import telebot
import boto3
import os

# Telegram Bot Token របស់អ្នក
TOKEN = '9114546888:AAHhpwshrkCSxbo1D27z28NeVDSwaBPgLHE'
bot = telebot.TeleBot(TOKEN)

# ព័ត៌មាន Cloudflare R2 S3 API
R2_ACCESS_KEY_ID = '37ed1b52b8518fbd2716947e71e4abe6'
R2_SECRET_ACCESS_KEY = '29ed133a63d3c2fea906c454ea16d47db553b7d2f6de810c079eb6f3e269fa44'
R2_BUCKET_NAME = 'dekmerl'
R2_ENDPOINT_URL = 'https://89c43899d62db25f2591bee0720cd7a9.r2.cloudflarestorage.com'
PUBLIC_DOMAIN = 'https://pub-70ba2b8a513b452594e3faead4c18d0d.r2.dev'

# ភ្ជាប់ទៅកាន់ Cloudflare R2 (នៅលើ Render ដំណើរការ SSL យ៉ាងស្ដង់ដារ)
s3_client = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name='auto'
)

@bot.message_handler(content_types=['video'])
def handle_video(message):
    sent_msg = bot.reply_to(message, "⏳ កំពុងទាញយក និង Upload វីដេអូចូល Cloudflare R2...")
    
    try:
        # 1. យក File ID ពី Telegram
        file_info = bot.get_file(message.video.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_name = f"video_{message.video.file_unique_id}.mp4"
        
        # 2. រក្សាទុកក្នុង Server បណ្តោះអាសន្ន
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        # 3. Upload ចូល R2 Bucket
        with open(file_name, 'rb') as f:
            s3_client.upload_fileobj(
                f, 
                R2_BUCKET_NAME, 
                file_name,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
            
        # 4. លុបហ្វាលបណ្តោះអាសន្នចេញពី Server
        if os.path.exists(file_name):
            os.remove(file_name)
        
        # 5. បង្កើតលីងសាធារណៈ r2.dev ផ្ញើជូនអ្នក
        video_url = f"{PUBLIC_DOMAIN}/{file_name}"
        
        response_text = (
            "✅ **Upload ជោគជ័យនៅលើ Cloud!**\n\n"
            f"🔗 **លីងវីដេអូសាធារណៈ:**\n{video_url}\n\n"
            "💻 **កូដ HTML សម្រាប់វេបសាយ:**\n"
            f'<video controls width="100%">\n  <source src="{video_url}" type="video/mp4">\n</video>'
        )
        bot.edit_message_text(response_text, message.chat.id, sent_msg.message_id, parse_mode='Markdown')
        
    except Exception as e:
        bot.edit_message_text(f"❌ មានបញ្ហាក្នុងការ Upload: {str(e)}", message.chat.id, sent_msg.message_id)

print("Render Telegram Bot is running...")
bot.polling(none_stop=True)
