import openai
import telegram
import os
import asyncio
from openai import AsyncOpenAI  # Thêm dòng này

# Load từ environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Tạo client mới
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def send_to_telegram(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def get_idiom():
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

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    text = response.choices[0].message.content.strip()
    return text

if __name__ == '__main__':
    async def main():
        idiom_message = await get_idiom()
        await send_to_telegram(idiom_message)

    asyncio.run(main())
