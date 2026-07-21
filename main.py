import os
import telebot
import google.generativeai as genai

# Environment Variables වලින් Tokens ලබාගැනීම
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini සහ Telegram Bot Setup කිරීම
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# /start Command එකට උත්තර දීම
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! 🇱🇰\nමම රක්ෂියා විස්තර Post එකක් බවට පත්කරන Bot කෙනෙක්. මට Job එකේ Details එවන්න!")

# සාමාන්‍ය Messages සඳහා (Gemini AI මගින් Job Post එකක් සෑදීම)
@bot.message_handler(func=lambda message: True)
def process_job_details(message):
    try:
        user_text = message.text
        bot.send_message(message.chat.id, "⏳ කරුණාකර රැඳී සිටින්න, Job Post එක නිර්මාණය වෙමින් පවතී...")

        # Gemini Prompt එක
        prompt = f"""
        පහත දැක්වෙන රැකියා විස්තරය භාවිත කරල Telegram Channel එකකට සුදුසු පැහැදිලි Sinhala Job Caption එකක් සාදන්න:
        Details: {user_text}

        Format Requirements:
        - Job Title (Sinhala & English)
        - Company / Institute Name
        - Closing Date
        - Details & Requirements (Bullet points)
        - Relevant Hashtags
        """

        response = model.generate_content(prompt)
        ai_reply = response.text

        # Output එක Telegram එකට යැවීම
        bot.reply_to(message, ai_reply, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ අසාර්ථක විය: {str(e)}")

# Bot එක 24/7 Run කරවීම සඳහා Loop එක
if __name__ == "__main__":
    print("Bot is starting...")
    bot.infinity_polling()
