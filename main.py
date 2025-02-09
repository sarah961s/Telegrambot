import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# إعدادات السجل (التسجيل)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# قائمة الكتب (يمكن تعديلها)
books = {
    "لعلهم يهتدون الجزء الرابع النصيرية": r"C:\Users\obada\OneDrive\Desktop\Telbot\Books\Noor-Book.com  لعلهم يهتدون الجزء الرابع النصيرية.pdf",
        "ملخص بحوث في قضايا فقهية معاصرة": r"C:\Users\obada\OneDrive\Desktop\Telbot\Books\Noor-Book.com  ملخص بحوث في قضايا فقهية معاصرة.pdf",
}

# دالة بدء البوت
async def start(update: Update, context: CallbackContext) -> None:
    try:
        logger.info("تم استقبال أمر البدء")
        
        # التحقق من وجود الكتب في القائمة
        if not books:
            logger.error("لا توجد كتب في القائمة!")
            await update.message.reply_text("حدثت مشكلة في تحميل الكتب.")
            return
        
        # إنشاء الأزرار التي سيتم عرضها للمستخدم
        keyboard = [
            [InlineKeyboardButton(book, callback_data=book) for book in books.keys()]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text('اختر كتابًا للتحميل:', reply_markup=reply_markup)
        logger.info("تم عرض الأزرار بنجاح.")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء عرض الكتب: {e}")
        await update.message.reply_text(f"حدثت مشكلة في تحميل الكتب: {e}")

# دالة التعامل مع الضغط على الأزرار
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    book_name = query.data
    file_path = books[book_name]
    await query.message.reply_text(f'جاري تحميل {book_name}...')
    try:
        # فتح الكتاب وإرساله للمستخدم
        with open(file_path, 'rb') as book_file:
            await query.message.reply_document(book_file)
        logger.info(f"تم إرسال الكتاب {book_name} بنجاح.")
    except FileNotFoundError:
        logger.error(f"الملف {file_path} غير موجود.")
        await query.message.reply_text("عذرًا، لم نتمكن من العثور على الكتاب.")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إرسال الكتاب {book_name}: {str(e)}")
        await query.message.reply_text(f"حدث خطأ: {str(e)}")

# الدالة الرئيسية لتشغيل البوت
def main():
    # إعداد البوت باستخدام التوكن
    application = Application.builder().token("7433784129:AAH3ku61TMQCHqviqkF7M2Rr9B7d48xySUc").build()

    # إضافة المعالجات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # تشغيل البوت
    application.run_polling()

# تشغيل البوت إذا كان هذا هو الملف الرئيسي
if __name__ == '__main__':
    main()
