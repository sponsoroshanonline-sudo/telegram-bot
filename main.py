import os
import json
import threading
import requests
from flask import Flask
import telebot
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS

# 1. Web Server for Render Keep-Alive
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# AI Script & Text Extractor (OpenRouter Gemini Free)
def get_job_data(user_text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    පහත Job Details භාවිත කර මෙන්න මේ JSON Format එකෙන් පමණක් Output එක දෙන්න (වෙනත් කිසිදු Text එකක් ඇතුළත් නොකරන්න):

    {{
      "job_title_sinhala": "තනතුරේ නම සිංහලෙන් (කෙටියෙන්)",
      "job_title_english": "Designation in English",
      "company_name": "ආයතනයේ නම",
      "closing_date": "YYYY-MM-DD",
      "voice_script": "CapCut Voiceover එකට සුදුසු තත්පර 20ක ස්වාභාවික සිංහල විස්තරය",
      "telegram_caption": "Telegram Post එකට සුදුසු පැහැදිලි Caption එක"
    }}

    Details: {user_text}
    """

    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=25)
    if res.status_code == 200:
        content = res.json()['choices'][0]['message']['content']
        # Extract JSON
        clean_json = content[content.find('{'):content.rfind('}')+1]
        return json.loads(clean_json)
    else:
        raise Exception("AI API Error")

# 1:1 Image Generator (White & Navy Design)
def generate_1by1_image(data):
    img = Image.new('RGB', (1080, 1080), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Top Area Header Line
    draw.rectangle([(0, 0), (1080, 50)], fill=(9, 29, 66))
    
    # Middle Dark Navy Box
    draw.rectangle([(0, 540), (1080, 950)], fill=(9, 29, 66))
    
    # Red Separation Line
    draw.rectangle([(0, 530), (1080, 540)], fill=(220, 38, 38))

    # Red Closing Date Badge
    draw.rectangle([(290, 840), (790, 910)], fill=(220, 38, 38))

    # Basic Fonts (System Default / Basic Fallback)
    try:
        font_main = ImageFont.truetype("arial.ttf", 45)
    except:
        font_main = ImageFont.load_default()

    # Draw Text Content
    draw.text((540, 220), data.get('job_title_sinhala', ''), fill=(9, 29, 66), anchor="mm", font=font_main)
    draw.text((540, 320), data.get('job_title_english', ''), fill=(9, 29, 66), anchor="mm", font=font_main)
    draw.text((540, 680), data.get('company_name', ''), fill=(255, 255, 255), anchor="mm", font=font_main)
    draw.text((540, 875), f"CLOSING DATE: {data.get('closing_date', 'N/A')}", fill=(255, 255, 255), anchor="mm", font=font_main)

    path = "job_post.png"
    img.save(path)
    return path

# Voiceover MP3 Generator
def generate_voice(text):
    tts = gTTS(text=text, lang='si')
    path = "voice.mp3"
    tts.save(path)
    return path

# Bot Command / Messages
@bot.message_handler(commands=['start', 'help'])
def start_msg(msg):
    bot.reply_to(msg, "ආයුබෝවන්! 🇱🇰\nCapCut Short Video සෑදීමට අදාළ Image එක, Voiceover MP3 එක සහ Caption එක ලබාගැනීමට Job Details එවන්න!")

@bot.message_handler(func=lambda msg: not msg.text.startswith('/'))
def process_job(msg):
    try:
        bot.send_message(msg.chat.id, "⏳ කරුණාකර රැඳී සිටින්න, Image එක සහ Voiceover එක සෑදෙමින් පවතී...")
        
        # Get AI Extracted Data
        data = get_job_data(msg.text)
        
        # Generate Media
        img_path = generate_1by1_image(data)
        audio_path = generate_voice(data.get('voice_script', msg.text))
        
        # Send Photo with Caption
        with open(img_path, 'rb') as photo:
            bot.send_photo(msg.chat.id, photo, caption=data.get('telegram_caption', ''), parse_mode="Markdown")
            
        # Send Audio File
        with open(audio_path, 'rb') as audio:
            bot.send_audio(msg.chat.id, audio, caption="🎙️ CapCut සඳහා Sinhala Voiceover MP3 එක")

    except Exception as e:
        bot.reply_to(msg, f"❌ අසාර්ථක විය: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    bot.infinity_polling()
