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
    ## Vocabulary Builder Prompt (IELTS / TOEIC / Daily English)

    Pick a truly random but common English vocabulary word that is useful in IELTS, TOEIC, or daily communication, and different from previous ones.

    For each word, provide:

    Word: <word>

    Part of speech: <part of speech> (e.g., noun, verb, adjective, adverb)
    Word family: <related forms> (e.g., noun, verb, adjective, adverb variations)

    Synonyms: <common synonyms>
    Antonyms: <common antonyms>

    Meaning (English): <short meaning in easy English>
    Meaning (Vietnamese): <short meaning in Vietnamese>

    Example: <example sentence in English>

    ### Format example:

    Word: confident

    Part of speech: adjective
    Word family: confidence (noun), confidently (adverb)

    Synonyms: self-assured, positive, assertive
    Antonyms: insecure, doubtful, shy

    Meaning (English): feeling sure about yourself and your abilities
    Meaning (Vietnamese): cảm thấy chắc chắn về bản thân và khả năng của mình

    Example: She felt confident before the important presentation.

    
    Thực hiện xuống dòng theo format tôi đã đề ra để tin nhắn dễ nhìn hơn
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,   # <--- tăng lên
        max_tokens=300
    )
    text = response.choices[0].message.content.strip()
    return text


if __name__ == '__main__':
    async def main():
        idiom_message = await get_idiom()
        await send_to_telegram(idiom_message)

    asyncio.run(main())
