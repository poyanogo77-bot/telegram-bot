import os
import threading
import asyncio
import json
import uuid
import urllib.request
import urllib.parse

from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")

FILES_TABLE = f"{SUPABASE_URL}/rest/v1/files"

web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Telegram Bot is running!"


def run_web():
    port = int(os.getenv("PORT", 10000))
    web_app.run(host="0.0.0.0", port=port)


def supabase_request(method, url, data=None):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=body,
        headers=headers,
        method=method,
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        content = response.read().decode("utf-8")

        if content:
            return json.loads(content)

        return None


def get_file(file_key):
    encoded_key = urllib.parse.quote(file_key, safe="")

    url = (
        f"{FILES_TABLE}"
        f"?select=file_id,file_name,file_key"
        f"&file_key=eq.{encoded_key}"
        f"&limit=1"
    )

    result = supabase_request("GET", url)

    if result and len(result) > 0:
        return result[0]

    return None


def save_file(file_key, file_id, file_name):
    data = {
        "id": str(uuid.uuid4()),
        "file_id": file_id,
        "file_name": file_name,
        "file_key": file_key,
    }

    return supabase_request("POST", FILES_TABLE, data)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        file_key = context.args[0]

        file_data = get_file(file_key)

        if file_data:
            await update.message.reply_document(
                document=file_data["file_id"],
                caption="📁 فایل شما آماده است."
            )
        else:
            await update.message.reply_text(
                "❌ فایل پیدا نشد."
            )
    else:
        await update.message.reply_text(
            "سلام 👋\n"
            "برای دریافت فایل، لینک مخصوص آن را باز کنید."
        )


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name or "file"

        file_key = "file_" + uuid.uuid4().hex[:12]

        try:
            save_file(
                file_key=file_key,
                file_id=file_id,
                file_name=file_name
            )

            bot_username = context.bot.username

            await message.reply_text(
                f"✅ فایل دریافت شد!\n\n"
                f"نام فایل: {file_name}\n"
                f"کد فایل: {file_key}\n\n"
                f"لینک دریافت فایل:\n"
                f"https://t.me/{bot_username}?start={file_key}"
            )

        except Exception as e:
            print("❌ DATABASE ERROR:", repr(e))

            await message.reply_text(
                "❌ ذخیره اطلاعات فایل انجام نشد."
            )


async def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(
            filters.Document.ALL,
            receive_file
        )
    )

    await app.initialize()
    print("✅ Telegram initialized")

    await app.start()
    print("✅ Telegram application started")

    await app.updater.start_polling()
    print("✅ Telegram polling started")

    await asyncio.Event().wait()


def main():
    print("🚀 Starting Telegram bot...")

    threading.Thread(
        target=run_web,
        daemon=True
    ).start()

    try:
        asyncio.run(run_bot())

    except Exception as e:
        print(
            "❌ TELEGRAM BOT ERROR:",
            repr(e)
        )
        raise


if __name__ == "__main__":
    main()
