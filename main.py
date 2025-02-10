import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext

# لا حاجة لاستدعاء keep_alive() في حالة استخدام Webhook؛ حيث يستخدم التطبيق الخادم المدمج.
# إذا كنت تعمل في بيئة تتطلب إبقاء العملية نشطة (مثل Replit) تأكد من استخدام طريقة مناسبة.

# إعداد السجل (Logging)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# قائمة الكتب (يمكن تعديلها حسب احتياجاتك)
books = {
    "book1": {
        "title": "أثر الخداع التسويقي في بناء الصورة الذهنية للمستهلك",
        "path": "Books/اثر_الخداع_التسويقي.pdf"
    },
    "book2": {
        "title": "الثقافة الاسلامية في مجال التسويق",
        "path": "Books/الثقافة_الاسلامية.pdf"
    },
    "book3": {
        "title": "العادات والتقاليد بين الهوى والتقييد",
        "path": "Books/العادات_والتقاليد.pdf"
    },
    "book4": {
        "title": "لعلهم يهتدون الجزء الاول الاثنى عشرية",
        "path": "Books/لعلهم_يهتدون_1.pdf"
    },
    "book5": {
        "title": "لعلهم يهتدون الجزء الثاني الاسماعيلية",
        "path": "Books/لعلهم_يهتدون_2.pdf"
    },
    "book6": {
        "title": "لعلهم يهتدون الجزء الثالث الزيدية",
        "path": "Books/لعلهم_يهتدون_3.pdf"
    },
    "book7": {
        "title": "لعلهم يهتدون الجزء الرابع النصيرية",
        "path": "Books/Noor-Book.com  لعلهم يهتدون الجزء الرابع النصيرية.pdf"
    },
    "book8": {
        "title": "لعلهم يهتدون الجزء الخامس الدروز",
        "path": "Books/لعلهم_يهتدون_5.pdf"
    },
    "book9": {
        "title": "ملخص بحوث في قضايا فقهية معاصرة",
        "path": "Books/ملخص_بحوث.pdf"
    }
}

# دالة بدء البوت
async def start(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.effective_user.id
        last_command_time = context.user_data.get('last_start_command', 0)
        current_time = update.message.date.timestamp()

        # منع تكرار الأمر خلال 5 ثوانٍ
        if current_time - last_command_time < 5:
            return

        context.user_data['last_start_command'] = current_time
        logger.info(f"تم استقبال أمر البدء من المستخدم {user_id}")

        # إنشاء زر لإعادة تشغيل البوت وعرض قائمة الكتب
        keyboard = [[KeyboardButton("عرض قائمة الكتب 📚")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        if not books:
            logger.error("لا توجد كتب في القائمة!")
            await update.message.reply_text("حدثت مشكلة في تحميل الكتب.", reply_markup=reply_markup)
            return

        # إنشاء أزرار الكتب باستخدام InlineKeyboard
        keyboard = []
        row = []
        for book_id, book_info in books.items():
            row.append(
                InlineKeyboardButton(book_info['title'], callback_data=book_id)
            )
            if len(row) == 2:  # ضع زرين في كل صف
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)

        # زر /start كخيار إعادة تشغيل دائم
        start_keyboard = [[KeyboardButton("/start")]]
        start_markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)

        await update.message.reply_text('اختر كتابًا للتحميل:', reply_markup=reply_markup)
        await update.message.reply_text('يمكنك الضغط على زر /start في أي وقت لعرض قائمة الكتب', reply_markup=start_markup)
        logger.info("تم عرض الأزرار بنجاح.")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء عرض الكتب: {e}")
        await update.message.reply_text(f"حدثت مشكلة في تحميل الكتب: {e}")

# دالة التعامل مع الضغط على أزرار الكتب
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    book_id = query.data
    if book_id is None:
        await query.message.reply_text("❌ حدث خطأ: لم يتم تحديد الكتاب")
        return
    try:
        book_info = books[book_id]
        progress_message = await query.message.reply_text("⏳ جاري تجهيز الملف...")

        # فتح الملف وإرساله للمستخدم
        with open(book_info['path'], 'rb') as book_file:
            await progress_message.edit_text("📤 جاري رفع الملف...")
            await update.effective_message.reply_document(
                document=book_file,
                filename=book_info['title'] + '.pdf',
                caption="✅ تم التحميل بنجاح"
            )
            await progress_message.delete()
            logger.info(f"تم إرسال الكتاب {book_info['title']} بنجاح.")
    except FileNotFoundError:
        logger.error(f"الملف {book_info['path']} غير موجود.")
        await progress_message.edit_text("❌ عذراً، لم نتمكن من العثور على الكتاب.")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إرسال الكتاب {book_info['title']}: {str(e)}")
        await progress_message.edit_text(f"❌ حدث خطأ في التحميل")

# الدالة الرئيسية لتشغيل البوت باستخدام Webhook
def main():
    try:
        print("بدء تشغيل البوت...")
        logger.info("بدء تهيئة البوت")

        token = "7734332111:AAHCqgBEdFQB6pr382vmjJzdHQkhXSBRGm8"
        if not token:
            raise ValueError("لم يتم تعيين توكن البوت")

        application = Application.builder().token(token).build()
        logger.info("تم الاتصال بالبوت بنجاح")

        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button))

        print("تم تهيئة البوت بنجاح، جاري بدء التشغيل...")
        logger.info("تم تهيئة البوت بنجاح")

        # تشغيل البوت باستخدام Webhook
        # تأكد من استبدال "your_domain.com" بالنطاق الخاص بخادمك (مثلاً: "your-app.onrender.com")
        application.run_webhook(
            listen="0.0.0.0",          # الاستماع لجميع العناوين
            port=8443,                 # تأكد من أن المنفذ مفتوح ويقبل الاتصالات (قد تحتاج لتغييره حسب مزود الخدمة)
            url_path=token,            # استخدم التوكن كجزء من URL endpoint
            webhook_url="https://telegrambot-x9zt.onrender.com" + token,  # الرابط الكامل الذي سيستخدمه Telegram لإرسال التحديثات
            allowed_updates=Update.ALL_TYPES
        )

    except Exception as e:
        error_msg = f"حدث خطأ في تشغيل البوت: {str(e)}"
        print(error_msg)
        logger.error(error_msg)
        raise

if __name__ == '__main__':
    main()
