import telebot
import os

TOKEN = '9114546888:AAHhpwshrkCSxbo1D27z28NeVDSwaBPgLHE'
bot = telebot.TeleBot(TOKEN)

# ដែនសាធារណៈ R2.dev របស់អ្នក
PUBLIC_DOMAIN = 'https://pub-70ba2b8a513b452594e3faead4c18d0d.r2.dev'

@bot.message_handler(content_types=['video'])
def handle_video(message):
    sent_msg = bot.reply_to(message, "⏳ កំពុងបង្កើតលីងវីដេអូសាធារណៈ...")
    
    try:
        # បង្កើតឈ្មោះហ្វាលដោយផ្អែកលើ Telegram File Unique ID
        file_name = f"video_{message.video.file_unique_id}.mp4"
        
        # បង្កើតលីងសាធារណៈរហ័ស
        video_url = f"{PUBLIC_DOMAIN}/{file_name}"
        
        response_text = (
            "✅ **បង្កើតលីងបានជោគជ័យ!**\n\n"
            f"🔗 **លីងវីដេអូសាធារណៈ:**\n{video_url}\n\n"
            "💻 **កូដ HTML សម្រាប់វេបសាយ:**\n"
            f'<video controls width="100%">\n  <source src="{video_url}" type="video/mp4">\n</video>'
        )
        bot.edit_message_text(response_text, message.chat.id, sent_msg.message_id, parse_mode='Markdown')
        
    except Exception as e:
        bot.edit_message_text(f"❌ មានបញ្ហា: {str(e)}", message.chat.id, sent_msg.message_id)

print("Fast Cloud Bot is running...")
bot.polling(none_stop=True)
