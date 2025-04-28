import openai
import telegram
import os
import asyncio
import re

from openai import AsyncOpenAI

# Load từ environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

IDIOMS_FILE = "sent_idioms.txt"

# Tạo client
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def send_text_to_telegram(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def send_voice_to_telegram(file_path):
    bot = telegram.Bot(token=BOT_TOKEN)
    with open(file_path, 'rb') as audio_file:
        await bot.send_voice(chat_id=CHAT_ID, voice=audio_file)

def extract_idiom(text):
    match = re.search(r"Idiom:\s*(.+)", text)
    if match:
        idiom_phrase = match.group(1).strip()
        return idiom_phrase
    return None

async def text_to_speech(text, output_path):
    response = await openai_client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    with open(output_path, "wb") as f:
        f.write(response.content)

def load_sent_idioms():
    if not os.path.exists(IDIOMS_FILE):
        return set()
    with open(IDIOMS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_idiom(idiom):
    with open(IDIOMS_FILE, "a", encoding="utf-8") as f:
        f.write(idiom + "\n")

async def get_idiom():
    prompt = """
    Pick a truly random English idiom and different from previous one.
    For the idiom, provide:
    - The idiom phrase
    - A short meaning explanation (in Vietnamese)
    - One example sentence in English.

Format the output clearly:
Idiom: <idiom>
Meaning: <meaning in Vietnamese>
Example: <example sentence in English>
    """
    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        max_tokens=300
    )
    text = response.choices[0].message.content.strip()
    return text

async def main():
    sent_idioms = load_sent_idioms()

    retries = 5
    for _ in range(retries):
        idiom_message = await get_idiom()
        idiom_text = extract_idiom(idiom_message)

        if idiom_text and idiom_text not in sent_idioms:
            # Gửi Text
            await send_text_to_telegram(idiom_message)

            # Tạo audio và gửi
            audio_file = "idiom_voice.mp3"
            await text_to_speech(idiom_text, audio_file)
            await send_voice_to_telegram(audio_file)
            os.remove(audio_file)

            # Lưu idiom đã gửi
            save_idiom(idiom_text)
            break
        else:
            print("Trùng idiom, đang thử lại...")

    else:
        print("Không tìm được idiom mới sau nhiều lần thử.")

if __name__ == '__main__':
    asyncio.run(main())
