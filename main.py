import os
import threading
import requests
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

# 2. Telegram Bot Token එක ලබාගැනීම
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Free Open AI Text Generator Function (No API Key Required)
def generate_ai_response(user_text):
    prompt = f"""
    You are a professional Sinhala social media content creator.
    Convert the following job details into a clear, attractive Telegram post caption in Sinhala:

    Job Details:
    {user_text}

    Format Requirements:
    - Job Title (Sinhala & English)
    - Company / Institute Name
    - Closing Date
    - Key Requirements (Bullet points)
    - Relevant Hashtags
    """

    # Public Free API Endpoint
    url = f"https://text.pollinations.ai/{requests.utils.quote(prompt)}"
    
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"API Error Status: {response.status_code}")

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

        # Free AI එකෙන් Response එක ගැනීම
        ai_reply = generate_ai_response(user_text)

        bot.reply_to(message, ai_reply)

    except Exception as e:
        bot.reply_to(message, f"❌ අසාර්ථක විය: {str(e)}")

if __name__ == "__main__":
    print("Starting Web Server...")
    threading.Thread(target=run_web_server, daemon=True).start()
    
    print("Starting Telegram Bot...")
    bot.infinity_polling()
