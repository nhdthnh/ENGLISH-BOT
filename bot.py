import telegram
import openai
import os
import asyncio

from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# Lấy token và API key từ biến môi trường GitHub Secrets


# Cấu hình OpenAI
openai.api_key = OPENAI_API_KEY

async def send_to_telegram(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

def get_idiom():
    prompt = """
    Give me one random English idiom.
    For the idiom, provide:
    - The idiom phrase
    - A short meaning explanation (in Vietnamese)
    - One example sentence in English.

    Format the output clearly as:
    Idiom: <idiom>
    Meaning: <meaning in Vietnamese>
    Example: <example sentence in English>
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",   # Hoặc gpt-3.5-turbo nếu cần
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )

    text = response['choices'][0]['message']['content'].strip()
    return text

if __name__ == '__main__':
    idiom_message = get_idiom()
    asyncio.run(send_to_telegram(idiom_message))