import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🏰 Muzey yaratish",
            callback_data="create"
        )],
        [InlineKeyboardButton(
            "💝 Mening muzeyim",
            callback_data="my_museum"
        )],
        [InlineKeyboardButton(
            "❓ Yordam",
            callback_data="help"
        )],
    ]

    await update.message.reply_text(
        "🏰 Xush kelibsiz — Baxt Qasri!\n\n"
        "Surat va videolaringizdan unutilmas "
        "3D xotiralar olamini yaratamiz. 💝\n\n"
        "Boshlash uchun tugmani tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "create":
        context.user_data["creating"] = True
        await query.message.reply_text(
            "📸 Muzeyga qo‘shish uchun surat yoki "
            "video yuboring.\n\n"
            "Hozircha media qabul qilishni "
            "sinayapmiz."
        )
    elif query.data == "my_museum":
        await query.message.reply_text(
            "💝 Shaxsiy muzey havolasi funksiyasini "
            "keyingi bosqichda qo‘shamiz."
        )
    else:
        await query.message.reply_text(
            "📸 Muzey yaratish tugmasini bosing va "
            "surat yoki video yuboring."
        )


async def media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get("creating"):
        await update.message.reply_text(
            "Avval 🏰 Muzey yaratish tugmasini bosing."
        )
        return

    if update.message.photo:
        await update.message.reply_text(
            "✅ Surat qabul qilindi! Yana surat yoki "
            "video yuborishingiz mumkin."
        )
    elif update.message.video:
        await update.message.reply_text(
            "✅ Video qabul qilindi! Yana media yuborishingiz mumkin."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🏰 Baxt Qasri — shaxsiy xotiralar muzeyi.\n"
        "Muzey yaratish tugmasini bosing va media yuboring."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO,
            media
        )
    )

    print("Baxt Qasri ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🏰 Muzey yaratish",
            callback_data="create"
        )],
        [InlineKeyboardButton(
            "💝 Mening muzeyim",
            callback_data="my_museum"
        )],
        [InlineKeyboardButton(
            "❓ Yordam",
            callback_data="help"
        )],
    ]

    await update.message.reply_text(
        "🏰 Xush kelibsiz — Baxt Qasri!\n\n"
        "Surat va videolaringizdan unutilmas "
        "3D xotiralar olamini yaratamiz. 💝\n\n"
        "Boshlash uchun tugmani tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "create":
        context.user_data["creating"] = True
        await query.message.reply_text(
            "📸 Muzeyga qo‘shish uchun surat yoki "
            "video yuboring.\n\n"
            "Hozircha media qabul qilishni "
            "sinayapmiz."
        )
    elif query.data == "my_museum":
        await query.message.reply_text(
            "💝 Shaxsiy muzey havolasi funksiyasini "
            "keyingi bosqichda qo‘shamiz."
        )
    else:
        await query.message.reply_text(
            "📸 Muzey yaratish tugmasini bosing va "
            "surat yoki video yuboring."
        )


async def media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get("creating"):
        await update.message.reply_text(
            "Avval 🏰 Muzey yaratish tugmasini bosing."
        )
        return

    if update.message.photo:
        await update.message.reply_text(
            "✅ Surat qabul qilindi! Yana surat yoki "
            "video yuborishingiz mumkin."
        )
    elif update.message.video:
        await update.message.reply_text(
            "✅ Video qabul qilindi! Yana media yuborishingiz mumkin."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🏰 Baxt Qasri — shaxsiy xotiralar muzeyi.\n"
        "Muzey yaratish tugmasini bosing va media yuboring."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO,
            media
        )
    )

    print("Baxt Qasri ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🏰 Muzey yaratish",
            callback_data="create"
        )],
        [InlineKeyboardButton(
            "💝 Mening muzeyim",
            callback_data="my_museum"
        )],
        [InlineKeyboardButton(
            "❓ Yordam",
            callback_data="help"
        )],
    ]

    await update.message.reply_text(
        "🏰 Xush kelibsiz — Baxt Qasri!\n\n"
        "Surat va videolaringizdan unutilmas "
        "3D xotiralar olamini yaratamiz. 💝\n\n"
        "Boshlash uchun tugmani tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "create":
        context.user_data["creating"] = True
        await query.message.reply_text(
            "📸 Muzeyga qo‘shish uchun surat yoki "
            "video yuboring.\n\n"
            "Hozircha media qabul qilishni "
            "sinayapmiz."
        )
    elif query.data == "my_museum":
        await query.message.reply_text(
            "💝 Shaxsiy muzey havolasi funksiyasini "
            "keyingi bosqichda qo‘shamiz."
        )
    else:
        await query.message.reply_text(
            "📸 Muzey yaratish tugmasini bosing va "
            "surat yoki video yuboring."
        )


async def media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get("creating"):
        await update.message.reply_text(
            "Avval 🏰 Muzey yaratish tugmasini bosing."
        )
        return

    if update.message.photo:
        await update.message.reply_text(
            "✅ Surat qabul qilindi! Yana surat yoki "
            "video yuborishingiz mumkin."
        )
    elif update.message.video:
        await update.message.reply_text(
            "✅ Video qabul qilindi! Yana media yuborishingiz mumkin."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🏰 Baxt Qasri — shaxsiy xotiralar muzeyi.\n"
        "Muzey yaratish tugmasini bosing va media yuboring."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO,
            media
        )
    )

    print("Baxt Qasri ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🏰 Muzey yaratish",
            callback_data="create"
        )],
        [InlineKeyboardButton(
            "💝 Mening muzeyim",
            callback_data="my_museum"
        )],
        [InlineKeyboardButton(
            "❓ Yordam",
            callback_data="help"
        )],
    ]

    await update.message.reply_text(
        "🏰 Xush kelibsiz — Baxt Qasri!\n\n"
        "Surat va videolaringizdan unutilmas "
        "3D xotiralar olamini yaratamiz. 💝\n\n"
        "Boshlash uchun tugmani tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "create":
        context.user_data["creating"] = True
        await query.message.reply_text(
            "📸 Muzeyga qo‘shish uchun surat yoki "
            "video yuboring.\n\n"
            "Hozircha media qabul qilishni "
            "sinayapmiz."
        )
    elif query.data == "my_museum":
        await query.message.reply_text(
            "💝 Shaxsiy muzey havolasi funksiyasini "
            "keyingi bosqichda qo‘shamiz."
        )
    else:
        await query.message.reply_text(
            "📸 Muzey yaratish tugmasini bosing va "
            "surat yoki video yuboring."
        )


async def media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get("creating"):
        await update.message.reply_text(
            "Avval 🏰 Muzey yaratish tugmasini bosing."
        )
        return

    if update.message.photo:
        await update.message.reply_text(
            "✅ Surat qabul qilindi! Yana surat yoki "
            "video yuborishingiz mumkin."
        )
    elif update.message.video:
        await update.message.reply_text(
            "✅ Video qabul qilindi! Yana media yuborishingiz mumkin."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🏰 Baxt Qasri — shaxsiy xotiralar muzeyi.\n"
        "Muzey yaratish tugmasini bosing va media yuboring."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO,
            media
        )
    )

    print("Baxt Qasri ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ["BOT_TOKEN"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🏰 Muzey yaratish",
            callback_data="create"
        )],
        [InlineKeyboardButton(
            "💝 Mening muzeyim",
            callback_data="my_museum"
        )],
        [InlineKeyboardButton(
            "❓ Yordam",
            callback_data="help"
        )],
    ]

    await update.message.reply_text(
        "🏰 Xush kelibsiz — Baxt Qasri!\n\n"
        "Surat va videolaringizdan unutilmas "
        "3D xotiralar olamini yaratamiz. 💝\n\n"
        "Boshlash uchun tugmani tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if query.data == "create":
        context.user_data["creating"] = True
        await query.message.reply_text(
            "📸 Muzeyga qo‘shish uchun surat yoki "
            "video yuboring.\n\n"
            "Hozircha media qabul qilishni "
            "sinayapmiz."
        )
    elif query.data == "my_museum":
        await query.message.reply_text(
            "💝 Shaxsiy muzey havolasi funksiyasini "
            "keyingi bosqichda qo‘shamiz."
        )
    else:
        await query.message.reply_text(
            "📸 Muzey yaratish tugmasini bosing va "
            "surat yoki video yuboring."
        )


async def media(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.user_data.get("creating"):
        await update.message.reply_text(
            "Avval 🏰 Muzey yaratish tugmasini bosing."
        )
        return

    if update.message.photo:
        await update.message.reply_text(
            "✅ Surat qabul qilindi! Yana surat yoki "
            "video yuborishingiz mumkin."
        )
    elif update.message.video:
        await update.message.reply_text(
            "✅ Video qabul qilindi! Yana media yuborishingiz mumkin."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🏰 Baxt Qasri — shaxsiy xotiralar muzeyi.\n"
        "Muzey yaratish tugmasini bosing va media yuboring."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.VIDEO,
            media
        )
    )

    print("Baxt Qasri ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
  
