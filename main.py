import os
import threading
import requests
import json
from flask import Flask
import telebot

# 1. Dummy Web Server (Render එක Timed out වීම වැළැක්වීමට)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Tokens ලබාගැනීම
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# OpenRouter Free Model API Request
def generate_job_post(user_text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
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

    payload = {
        "model": "google/gemini-2.5-flash:free",  # 100% Free OpenRouter Model
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"OpenRouter Error Status {response.status_code}: {response.text}")

# /start Command එකට උත්තර දීම
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! 🇱🇰\nමම රැකියා විස්තර Post එකක් බවට පත්කරන Bot කෙනෙක්. මට Job එකේ Details එවන්න!")

# සාමාන්‍ය Messages සඳහා Job Post එකක් සෑදීම
@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def process_job_details(message):
    try:
        user_text = message.text
        bot.send_message(message.chat.id, "⏳ කරුණාකර රැඳී සිටින්න, Job Post එක නිර්මාණය වෙමින් පවතී...")

        # OpenRouter AI මගින් Text එක සෑදීම
        ai_reply = generate_job_post(user_text)

        bot.reply_to(message, ai_reply, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"❌ අසාර්ථක විය: {str(e)}")

if __name__ == "__main__":
    print("Starting Web Server...")
    threading.Thread(target=run_web_server, daemon=True).start()
    
    print("Starting Telegram Bot...")
    bot.infinity_polling()
