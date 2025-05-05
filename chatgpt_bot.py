import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os
import asyncio
from threading import Timer

# Load environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Dictionary to store user messages and timers
user_messages = {}
user_timers = {}

# Function to handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text

    # Add message to user's message list
    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id].append(message_text)

    # Cancel any existing timer for the user
    if user_id in user_timers:
        user_timers[user_id].cancel()

    # Schedule a response after 30 seconds
    user_timers[user_id] = Timer(30.0, asyncio.run, [send_response(update, context)])
    user_timers[user_id].start()

# Function to send a response
async def send_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_messages:
        # Combine all messages into a single prompt
        prompt = "\n".join(user_messages[user_id])

        # Clear the user's message list
        user_messages[user_id] = []

        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )

        # Send the response back to the user
        await update.message.reply_text(response.choices[0].message.content.strip())

# Main function to start the bot
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()