import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters

# إعداد السجل (Logging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# قائمة الكتب
books = {
    "book1": {"title": "أثر الخداع التسويقي في بناء الصورة الذهنية للمستهلك", "path": "Books/اثر_الخداع_التسويقي.pdf"},
    "book2": {"title": "الثقافة الاسلامية في مجال التسويق", "path": "Books/الثقافة_الاسلامية.pdf"},
    "book3": {"title": "العادات والتقاليد بين الهوى والتقييد", "path": "Books/العادات_والتقاليد.pdf"},
    "book4": {"title": "لعلهم يهتدون الجزء الاول الاثنى عشرية", "path": "Books/لعلهم_يهتدون_1.pdf"},
    "book5": {"title": "لعلهم يهتدون الجزء الثاني الاسماعيلية", "path": "Books/لعلهم_يهتدون_2.pdf"},
    "book6": {"title": "لعلهم يهتدون الجزء الثالث الزيدية", "path": "Books/لعلهم_يهتدون_3.pdf"},
    "book7": {"title": "لعلهم يهتدون الجزء الرابع النصيرية", "path": "Books/Noor-Book.com  لعلهم يهتدون الجزء الرابع النصيرية.pdf"},
    "book8": {"title": "لعلهم يهتدون الجزء الخامس الدروز", "path": "Books/لعلهم_يهتدون_5.pdf"},
    "book9": {"title": "ملخص بحوث في قضايا فقهية معاصرة", "path": "Books/ملخص_بحوث.pdf"}
}

# دالة إعداد قائمة الأوامر (Menü)
async def set_bot_commands(application):
    commands = [
        BotCommand("start", "🔄 بدء البوت"),
        BotCommand("books", "📚 قائمة الكتب")
    ]
    await application.bot.set_my_commands(commands)

# دالة بدء البوت
async def start(update: Update, context: CallbackContext) -> None:
    try:
        keyboard = [[KeyboardButton("📚 كتبي")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "مرحباً! اختر أحد الخيارات أدناه:",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"حدث خطأ أثناء عرض الزر: {e}")
        await update.message.reply_text(f"حدثت مشكلة: {e}")

# دالة التعامل مع الضغط على الأزرار
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    book_id = query.data
    if book_id and book_id in books:
        book_info = books[book_id]
        with open(book_info['path'], 'rb') as book_file:
            await query.message.reply_document(
                document=book_file,
                filename=book_info['title'] + '.pdf',
                caption="✅ تم التحميل بنجاح"
            )
    else:
        await query.message.reply_text("❌ حدث خطأ: لم يتم تحديد الكتاب")

# دالة عرض قائمة الكتب
async def my_books(update: Update, context: CallbackContext) -> None:
    keyboard = [[InlineKeyboardButton(book["title"], callback_data=book_id)] for book_id, book in books.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('اختر كتابًا للتحميل:', reply_markup=reply_markup)

# دالة تشغيل البوت
async def main():
    try:
        token = "YOUR_BOT_TOKEN

```python
        application = Application.builder().token(token).build()

        # تعيين قائمة الأوامر (Menü)
        await set_bot_commands(application)

        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("books", my_books))
        application.add_handler(CallbackQueryHandler(button))
        application.add_handler(MessageHandler(filters.Regex("📚 كتبي"), my_books))

        application.run_polling()
    except Exception as e:
        logger.error(f"حدث خطأ في تشغيل البوت: {str(e)}")
        raise

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
