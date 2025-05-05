import openai
import telegram
import os
import asyncio
import re
from gtts import gTTS

# Load từ environment
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

WORDS_FILE = "sent_words.txt"  # File lưu từ đã gửi

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

async def send_text_to_telegram(message):
    bot = telegram.Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def send_voice_to_telegram(file_path):
    bot = telegram.Bot(token=BOT_TOKEN)
    with open(file_path, 'rb') as audio_file:
        await bot.send_voice(chat_id=CHAT_ID, voice=audio_file)

async def get_word_message():
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

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        max_tokens=400
    )
    text = response.choices[0].message.content.strip()
    return text

def extract_word(text):
    # Tìm dòng bắt đầu bằng "Word:" và lấy nội dung sau nó
    match = re.search(r"Word:\s*(\w+)", text)
    if match:
        word = match.group(1).strip().lower()
        return word
    return None

async def text_to_speech(text, output_path):
    tts = gTTS(text, lang='en')
    tts.save(output_path)

def load_sent_words():
    if not os.path.exists(WORDS_FILE):
        return set()
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f.readlines())

def save_word(word):
    with open(WORDS_FILE, "a", encoding="utf-8") as f:
        f.write(word + "\n")

if __name__ == '__main__':
    async def main():
        sent_words = load_sent_words()

        retries = 1000
        for _ in range(retries):
            word_message = await get_word_message()
            word = extract_word(word_message)

            if word and word not in sent_words:
                # Gửi text lên Telegram
                await send_text_to_telegram(word_message)

                # Gửi voice đọc Word
                audio_file = "word_voice.mp3"
                await text_to_speech(word, audio_file)
                await send_voice_to_telegram(audio_file)
                os.remove(audio_file)

                # Ghi vào danh sách đã gửi
                save_word(word)
                break
            else:
                print("Trùng từ, đang thử lại...")

        else:
            print("Không tìm được từ mới sau nhiều lần thử.")

    asyncio.run(main())