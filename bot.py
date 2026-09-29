from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8901819842:AAGkS60nKbLRuWWD4WBzPBpAkUZaW97kxM4"

FILES = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        file_key = context.args[0]

        if file_key in FILES:
            await update.message.reply_document(
                document=FILES[file_key],
                caption="📁 فایل شما آماده است."
            )
        else:
            await update.message.reply_text("❌ فایل پیدا نشد.")
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

        file_key = f"file{len(FILES) + 1}"

        FILES[file_key] = file_id

        await message.reply_text(
            f"✅ فایل دریافت شد!\n\n"
            f"نام فایل: {file_name}\n"
            f"کد فایل: {file_key}\n\n"
            f"لینک دریافت فایل:\n"
            f"https://t.me/{context.bot.username}?start={file_key}"
        )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.Document.ALL, receive_file)
    )

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
