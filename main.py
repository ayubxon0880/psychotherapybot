import telebot
from telebot import types

TOKEN = "8416375443:AAHWwcRI_LeaRkgdyPXpmBFLK_3glLjCzCU"
bot = telebot.TeleBot(TOKEN)

GROUP_CHAT_ID = "-1002729050166"

user_language = {}
user_pending_question = {}

translations = {
    'uz': {
        'choose_language': "Iltimos, tilni tanlang:\n\n🇷🇺 Русский\n🇺🇸 English",
        'language_set': "🇺🇿 O'zbek tili tanlandi ✅",
        'welcome': "Assalomu alaykum, {}!\n\nSavolingizni yozib qoldiring, tez orada javob olasiz.",
        'question_sent': "✅ Savolingiz yuborildi. Tez orada javob olasiz.",
        'only_text_image': "⚠️ Faqat matn yoki rasm yuborish mumkin.",
        'send_phone': "📱 Iltimos, telefon raqamingizni yuboring:",
        'error': "⚠️ Xatolik yuz berdi. Keyinroq urinib ko‘ring."
    },
    'ru': {
        'choose_language': "Пожалуйста, выберите язык:\n\n🇺🇿 O'zbek\n🇺🇸 English",
        'language_set': "🇷🇺 Русский язык выбран ✅",
        'welcome': "Здравствуйте, {}!\n\nОтправьте свой вопрос, и вскоре получите ответ.",
        'question_sent': "✅ Ваш вопрос отправлен. Вскоре вы получите ответ.",
        'only_text_image': "⚠️ Можно отправлять только текст или изображение.",
        'send_phone': "📱 Пожалуйста, отправьте свой номер телефона:",
        'error': "⚠️ Произошла ошибка. Попробуйте позже."
    },
    'en': {
        'choose_language': "Please choose a language:\n\n🇺🇿 O'zbek\n🇷🇺 Русский",
        'language_set': "🇺🇸 English language selected ✅",
        'welcome': "Hello, {}!\n\nPlease send your question, and you will receive an answer shortly.",
        'question_sent': "✅ Your question has been sent. You will receive an answer soon.",
        'only_text_image': "⚠️ Only text or images can be sent.",
        'send_phone': "📱 Please send your phone number:",
        'error': "⚠️ An error occurred. Please try again later."
    }
}


def get_text(user_id, key, *args):
    lang = user_language.get(user_id, 'uz')
    text = translations[lang].get(key, key)
    return text.format(*args) if args else text


@bot.message_handler(commands=['start'])
def start_command(message):
    show_language_selection(message)


def show_language_selection(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_uz = types.KeyboardButton("🇺🇿 O'zbek")
    btn_ru = types.KeyboardButton("🇷🇺 Русский")
    btn_en = types.KeyboardButton("🇺🇸 English")
    markup.add(btn_uz, btn_ru, btn_en)

    bot.send_message(
        message.chat.id,
        "Iltimos, tilni tanlang:\n\nПожалуйста, выберите язык:\n\nPlease choose a language:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, handle_language_selection)


def handle_language_selection(message):
    user_id = message.chat.id
    text = message.text

    if text == "🇺🇿 O'zbek":
        user_language[user_id] = 'uz'
    elif text == "🇷🇺 Русский":
        user_language[user_id] = 'ru'
    elif text == "🇺🇸 English":
        user_language[user_id] = 'en'
    else:
        show_language_selection(message)
        return

    bot.send_message(user_id, get_text(user_id, 'language_set'), reply_markup=types.ReplyKeyboardRemove())

    name = message.from_user.first_name or "Foydalanuvchi"
    bot.send_message(user_id, get_text(user_id, 'welcome', name))
    bot.register_next_step_handler(message, handle_user_question)


def handle_user_question(message):
    user = message.from_user
    uid = user.id

    # foydalanuvchi yuborgan savolni saqlaymiz
    user_pending_question[uid] = message

    # raqam yuborish tugmasi
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    contact_button = types.KeyboardButton("📞 Raqamni yuborish", request_contact=True)
    markup.add(contact_button)

    bot.send_message(uid, get_text(uid, 'send_phone'), reply_markup=markup)
    bot.register_next_step_handler(message, handle_phone_number)


def handle_phone_number(message):
    user = message.from_user
    uid = user.id

    # foydalanuvchi raqamni yuborganini tekshiramiz
    if not message.contact:
        bot.send_message(uid, get_text(uid, 'send_phone'))
        bot.register_next_step_handler(message, handle_phone_number)
        return

    phone_number = message.contact.phone_number
    question_message = user_pending_question.get(uid)

    username = f"@{user.username}" if user.username else ""
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()

    header = (
        f"📩 *Yangi savol:*\n"
        f"*Ism:* {name}\n"
        f"*Username:* {username}\n"
        f"*ID:* `{uid}`\n"
        f"*Telefon:* {phone_number}\n\n"
    )

    try:
        if question_message.text:
            bot.send_message(
                int(GROUP_CHAT_ID),
                header + question_message.text,
                parse_mode="Markdown"
            )
        elif question_message.photo:
            bot.send_photo(
                int(GROUP_CHAT_ID),
                question_message.photo[-1].file_id,
                caption=header + (question_message.caption or ""),
                parse_mode="Markdown"
            )
        else:
            bot.send_message(uid, get_text(uid, 'only_text_image'))
            return

        bot.send_message(uid, get_text(uid, 'question_sent'), reply_markup=types.ReplyKeyboardRemove())

    except Exception as e:
        print(f"[ERROR] Guruhga yuborishda xato: {e}")
        bot.send_message(uid, get_text(uid, 'error'))


if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
