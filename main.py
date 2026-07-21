import os
import threading
from flask import Flask
import telebot
from google import genai

# 1. Dummy Web Server (Render එක Timed out වීම වැළැක්වීමට)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Environment Variables වලින් Tokens ලබාගැනීම
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini Client සහ Telegram Bot Setup කිරීම (Updated SDK)
client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# /start Command එකට උත්තර දීම
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! 🇱🇰\nමම රැකියා විස්තර Post එකක් බවට පත්කරන Bot කෙනෙක්. මට Job එකේ Details එවන්න!")

# සාමාන්‍ය Messages සඳහා (Gemini AI මගින් Job Post එකක් සෑදීම)
@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def process_job_details(message):
    try:
        user_text = message.text
        bot.send_message(message.chat.id, "⏳ කරුණාකර රැඳී සිටින්න, Job Post එක නිර්මාණය වෙමින් පවතී...")

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

        # අලුත් SDK එකෙන් Gemini 2.5/1.5 Models කතා කිරීම
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        ai_reply = response.text

        bot.reply_to(message, ai_reply, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ අසාර්ථක විය: {str(e)}")

if __name__ == "__main__":
    print("Starting Web Server...")
    threading.Thread(target=run_web_server, daemon=True).start()
    
    print("Starting Telegram Bot...")
    bot.infinity_polling()
