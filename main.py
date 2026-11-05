import telebot
from telebot import types
import requests
import time

TOKEN = "9272421100:AAH9ZPd5qcepa5-TofEsZKA1dbhBvJYO_-o"
ADMINS = ["ktyofficial169", "rienml1"]
FIREBASE_DB_URL = "https://dekmerl-a5e6b-default-rtdb.firebaseio.com"

bot = telebot.TeleBot(TOKEN)

def is_admin(message_or_call):
    username = message_or_call.from_user.username
    if username and username.lower().strip() in ADMINS:
        return True
    return False

def get_admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_status = types.KeyboardButton("📊 ពិនិត្យប្រព័ន្ធវេបសាយ")
    btn_stats = types.KeyboardButton("📈 មើលស្ថិតិអ្នកប្រើប្រាស់")
    btn_vip = types.KeyboardButton("👑 បញ្ជីសមាជិក VIP")
    btn_movies = types.KeyboardButton("🎬 រឿងសរុបក្នុងប្រព័ន្ធ")
    btn_give_vip = types.KeyboardButton("💎 ផ្ដល់ VIP ឱ្យអតិថិជន")
    btn_admin_info = types.KeyboardButton("👨‍💻 អ្នកគ្រប់គ្រង (Admins)")
    btn_tokens_info = types.KeyboardButton("🔑 ព័ត៌មាន Bot Tokens & Keys")
    btn_web = types.KeyboardButton("🌐 បើកវេបសាយ DekMerl")
    markup.add(btn_status, btn_stats, btn_vip, btn_movies, btn_give_vip, btn_admin_info, btn_tokens_info, btn_web)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name or "ម្ចាស់គណនី"
    if not is_admin(message):
        bot.reply_to(message, f"សួស្ដី {user_name}!\n❌ សូមអភ័យទោស Bot នេះត្រូវបានកំណត់ឱ្យប្រើប្រាស់ដាច់ខាតសម្រាប់តែអ្នកគ្រប់គ្រងវេបសាយតែប៉ុណ្ណោះ។")
        return

    welcome_text = (
        f"សួស្ដីលោកម្ចាស់ {user_name} (@{message.from_user.username})!\n\n"
        f"Dek Check Bot ជំនួយការគ្រប់គ្រងវេបសាយ DekMerl របស់អ្នកបានតភ្ជាប់ជោគជ័យ។\n"
        f"ប៊ូតុងបញ្ជាទាំងអស់ត្រូវបានដាក់បង្ហាញនៅខាងក្រោមរួចរាល់ហើយ!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_admin_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    if not is_admin(message):
        bot.reply_to(message, "❌ អ្នកគ្មានសិទ្ធិប្រើប្រាស់ប្រព័ន្ធនេះទេ!")
        return

    text = message.text

    if text == "📊 ពិនិត្យប្រព័ន្ធវេបសាយ":
        try:
            r = requests.get("https://dekmerl.online", timeout=10)
            if r.status_code == 200:
                bot.reply_to(message, "ស្ថានភាពវេបសាយ (DekMerl): កំពុងដំណើរការធម្មតា (Online 100%)\nURL: https://dekmerl.online")
            else:
                bot.reply_to(message, f"ស្ថានភាពវេបសាយ: មានបញ្ហា (Status Code: {r.status_code})")
        except Exception as e:
            bot.reply_to(message, f"ស្ថានភាពវេបសាយ: មិនអាចតភ្ជាប់បាន (Offline)\nកំហុស: {str(e)}")

    elif text == "📈 មើលស្ថិតិអ្នកប្រើប្រាស់":
        try:
            visits_res = requests.get(f"{FIREBASE_DB_URL}/analytics/totalVisits.json").json() or 0
            users_res = requests.get(f"{FIREBASE_DB_URL}/users.json").json() or {}
            
            total_users = len(users_res)
            online_count = 0
            now = time.time() * 1000
            for u in users_res.values():
                if u.get('lastSeen') and (now - u.get('lastSeen') < 3 * 60 * 1000):
                    online_count += 1

            stats_msg = (
                f"ស្ថិតិប្រព័ន្ធវេបសាយ DekMerl៖\n\n"
                f"អ្នកចូលមើលសរុប: {visits_res} នាក់\n"
                f"អ្នកចុះឈ្មោះសរុប: {total_users} នាក់\n"
                f"កំពុងសកម្ម (Online ឥឡូវនេះ): {online_count} នាក់"
            )
            bot.reply_to(message, stats_msg)
        except Exception as e:
            bot.reply_to(message, f"មិនអាចទាញទិន្នន័យស្ថិតិពី Firebase បានទេ: {str(e)}")

    elif text == "👑 បញ្ជីសមាជិក VIP":
        send_vip_page(message.chat.id, page=0)

    elif text == "🎬 រឿងសរុបក្នុងប្រព័ន្ធ":
        try:
            videos_res = requests.get(f"{FIREBASE_DB_URL}/videos.json").json() or {}
            total_episodes = len(videos_res)
            series_set = set()
            for v in videos_res.values():
                if v.get('series'):
                    series_set.add(v.get('series'))

            msg = f"ទិន្នន័យវីដេអូរឿងក្នុងវេបសាយ៖\n\nរឿងដុំសរុប: {len(series_set)} រឿង\nភាគសរុប: {total_episodes} ភាគ"
            bot.reply_to(message, msg)
        except Exception as e:
            bot.reply_to(message, f"កំហុស៖ {str(e)}")

    elif text == "💎 ផ្ដល់ VIP ឱ្យអតិថិជន":
        bot.reply_to(message, "ដើម្បីផ្ដល់ VIP តាម Bot សូមផ្ញើសារមកតាមទម្រង់នេះ៖\n`/givevip @username ថ្ងៃ`\nឧទាហរណ៍៖ `/givevip @ktyofficial169 30`", parse_mode="Markdown")

    elif text == "👨‍💻 អ្នកគ្រប់គ្រង (Admins)":
        admin_msg = (
            "👨‍💻 **បញ្ជីឈ្មោះអ្នកគ្រប់គ្រងប្រព័ន្ធ (Admins)៖**\n\n"
            "1. 👤 **KTY (Developer / Main Admin)**\n"
            "   • Username: `@ktyofficial169`\n"
            "   • តួនាទី៖ ម្ចាស់គម្រោង និងជាអ្នកបង្កើតប្រព័ន្ធវេបសាយ និង Bot ទាំងមូល។\n\n"
            "2. 👤 **RIENML1 (Co-Admin)**\n"
            "   • Username: `@RIENML1`\n"
            "   • តួនាទី៖ អ្នកគ្រប់គ្រង និងសម្របសម្រួលការទិញលក់កញ្ចប់ VIP ជូនអតិថិជន។"
        )
        bot.reply_to(message, admin_msg, parse_mode="Markdown")

    elif text == "🔑 ព័ត៌មាន Bot Tokens & Keys":
        tokens_msg = (
            "🔑 **ព័ត៌មានលម្អិតអំពី Tokens, API Keys និង Group IDs ទាំងអស់ក្នុងប្រព័ន្ធ៖**\n\n"
            "1. 🤖 **Dek Check Bot (Admin Control):**\n"
            "   • Token: `9272421100:AAH9ZPd5qcepa5-TofEsZKA1dbhBvJYO_-o`\n"
            "   • Chat ID: `-1004357183059`\n"
            "   • **មុខងារ៖** Bot សម្រាប់ឱ្យ Admin ឆែកប្រព័ន្ធ ស្ថិតិ និងគ្រប់គ្រងសមាជិក VIP។\n\n"
            "2. 🔥 **Firebase Database:**\n"
            "   • URL: `https://dekmerl-a5e6b-default-rtdb.firebaseio.com`\n"
            "   • **មុខងារ៖** ប្រព័ន្ធផ្ទុកទិន្នន័យកណ្ដាល (រឿងភាគ, សមាជិក, ប្រវត្តិមើល និង VIP Expiry)។\n\n"
            "3. 📢 **Movie Instant Upload Bot:**\n"
            "   • Token: `9284674255:AAHP3kX9xipGvouXRXx4sZWcL_x_BnGnNaE`\n"
            "   • Group ID: `-1004381190574`\n"
            "   • **មុខងារ៖** ផ្ញើសារដំណឹងស្វ័យប្រវត្តិចូល Group ពេលមានការបង្ហោះរឿងថ្មីចូលវេបសាយភ្លាមៗ។\n\n"
            "4. ⏰ **Schedule Upload Bot:**\n"
            "   • Token: `9122037857:AAFWXSDTRuhVAu8D4TEDHUI3vFDGfRH0Mvg`\n"
            "   • Group ID: `-1004373607990`\n"
            "   • **មុខងារ៖** គ្រប់គ្រងការកំណត់ពេលបង្ហោះរឿងទុកមុន (Scheduled Post)។\n\n"
            "5. 👑 **VIP Bot:**\n"
            "   • Token: `9260453589:AAHTu0QrFkmoYugNuCGCOhD_lBTHM3N4qZs`\n"
            "   • Group ID: `-1004493438456`\n"
            "   • **មុខងារ៖** ផ្ញើសារនៅពេលមានអតិថិជនទិញកញ្ចប់ VIP ។\n\n"
            "6. ⚠️ **Expired VIP Bot:**\n"
            "   • Token: `9246036170:AAHb7bTyGetzB0hV5YwNAT-5-izAlogkBY0`\n"
            "   • Group ID: `-1004387202073`\n"
            "   • **មុខងារ៖** ផ្ញើសារនៅពេល VIP អស់សុពលភាព និងធ្លាក់មកជាសមាជិកធម្មតាវិញស្វ័យប្រវត្តិ។"
        )
        bot.reply_to(message, tokens_msg, parse_mode="Markdown")

    elif text == "🌐 បើកវេបសាយ DekMerl":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ចុចទីនេះដើម្បីបើកវេបសាយ", url="https://dekmerl.online"))
        bot.reply_to(message, "តំណភ្ជាប់វេបសាយរបស់អ្នក៖", reply_markup=markup)

    elif text.startswith("/givevip"):
        try:
            parts = text.split()
            target_user = parts[1].lower().strip()
            days = int(parts[2])
            
            clean_key = target_user.replace('@', '').replace('/', '')
            expiry_time = time.time() * 1000 + (days * 24 * 60 * 60 * 1000)

            requests.patch(f"{FIREBASE_DB_URL}/users/{clean_key}.json", json={
                "username": target_user if target_user.startswith('@') else '@' + target_user,
                "vipExpiry": expiry_time
            })

            bot.reply_to(message, f"បានផ្ដល់សិទ្ធិ VIP ជូន {target_user} ចំនួន {days} ថ្ងៃជោគជ័យហើយ!")
        except Exception as e:
            bot.reply_to(message, "ទម្រង់មិនត្រឹមត្រូវ! សូមប្រើប្រាស់៖ /givevip @username ចំនួនថ្ងៃ")

def send_vip_page(chat_id, page=0, message_id=None):
    try:
        users_res = requests.get(f"{FIREBASE_DB_URL}/users.json").json() or {}
        now = time.time() * 1000
        vip_list = []
        for u in users_res.values():
            if u.get('vipExpiry') and u.get('vipExpiry') > now:
                remaining_days = max(1, int((u.get('vipExpiry') - now) / (1000 * 60 * 60 * 24)))
                vip_list.append(f"• {u.get('username')} (សល់ {remaining_days} ថ្ងៃ)")

        if not vip_list:
            msg = "បច្ចុប្បន្នមិនមានសមាជិក VIP សកម្មទេក្នុងប្រព័ន្ធ。"
            if message_id:
                bot.edit_message_text(msg, chat_id, message_id)
            else:
                bot.send_message(chat_id, msg)
            return

        items_per_page = 15
        total_pages = (len(vip_list) + items_per_page - 1) // items_per_page
        page = max(0, min(page, total_pages - 1))

        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_items = vip_list[start_idx:end_idx]

        msg = f"👑 **បញ្ជីសមាជិក VIP សកម្ម (សរុប {len(vip_list)} នាក់)** — ទំព័រ {page + 1}/{total_pages}៖\n\n" + "\n".join(current_items)

        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        if page > 0:
            buttons.append(types.InlineKeyboardButton("⬅️ មុន", callback_data=f"vip_page_{page - 1}"))
        if page < total_pages - 1:
            buttons.append(types.InlineKeyboardButton("➡️ បន្ទាប់", callback_data=f"vip_page_{page + 1}"))
        
        if buttons:
            markup.add(*buttons)

        if message_id:
            bot.edit_message_text(msg, chat_id, message_id, reply_markup=markup)
        else:
            bot.send_message(chat_id, msg, reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, f"កំហុស៖ {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('vip_page_'))
def callback_vip_pagination(call):
    if not is_admin(call):
        bot.answer_callback_query(call.id, "❌ អ្នកគ្មានសិទ្ធិទេ!", show_alert=True)
        return
    
    page = int(call.data.split('_')[2])
    send_vip_page(call.message.chat.id, page=page, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)

print("Bot with complete Tokens and Group IDs info is running...")
bot.infinity_polling()
