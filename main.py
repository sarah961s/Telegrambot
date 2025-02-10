# دالة بدء البوت
async def start(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.effective_user.id
        # التحقق من الوقت المنقضي منذ آخر أمر start
        last_command_time = context.user_data.get('last_start_command', 0)
        current_time = update.message.date.timestamp()

        # منع تكرار الأمر خلال 5 ثوانٍ
        if current_time - last_command_time < 5:
            return

        context.user_data['last_start_command'] = current_time
        logger.info(f"تم استقبال أمر البدء من المستخدم {user_id}")

        # إنشاء زر "كتبي" لعرض قائمة الكتب
        keyboard = [
            [KeyboardButton("كتبي 📚")],  # زر "كتبي"
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        # إرسال رسالة ترحيب مع زر "كتبي"
        await update.message.reply_text('مرحبًا! اضغط على "كتبي 📚" لعرض قائمة الكتب.',
                                        reply_markup=reply_markup)
        logger.info("تم عرض زر كتبي بنجاح.")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء عرض زر البداية: {e}")
        await update.message.reply_text(f"حدثت مشكلة في تحميل زر البداية: {e}")


# دالة التعامل مع الضغط على الأزرار
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
  
        # فتح الكتاب وإرساله للمستخدم
        with open(book_info['path'], 'rb') as book_file:
            await progress_message.edit_text("📤 جاري رفع الملف...")
            sent_message = await update.effective_message.reply_document(
                document=book_file,
                filename=book_info['title'] + '.pdf',
                caption="✅ تم التحميل بنجاح")
            await progress_message.delete()
            logger.info(f"تم إرسال الكتاب {book_info['title']} بنجاح.")
    except FileNotFoundError:
        logger.error(f"الملف {book_info['path']} غير موجود.")
        await progress_message.edit_text(
            "❌ عذراً، لم نتمكن من العثور على الكتاب.")
    except Exception as e:
        logger.error(
            f"حدث خطأ أثناء إرسال الكتاب {book_info['title']}: {str(e)}")
        await progress_message.edit_text(f"❌ حدث خطأ في التحميل")


# دالة عرض قائمة الكتب عند الضغط على "كتبي"
async def show_books(update: Update, context: CallbackContext) -> None:
    try:
        # إنشاء الأزرار التي سيتم عرضها للمستخدم
        keyboard = []
        row = []
        for book_id, book_info in books.items():
            row.append(
                InlineKeyboardButton(book_info['title'],
                                     callback_data=book_id))
            if len(row) == 2:  # سيتم وضع زرين في كل صف
                keyboard.append(row)
                row = []
        if row:  # إضافة الصف الأخير إذا كان غير مكتمل
            keyboard.append(row)
        reply_markup = InlineKeyboardMarkup(keyboard)

        # إرسال قائمة الكتب للمستخدم
        await update.message.reply_text('اختر كتابًا للتحميل:', reply_markup=reply_markup)
        logger.info("تم عرض قائمة الكتب بنجاح.")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء عرض الكتب: {e}")
        await update.message.reply_text(f"حدثت مشكلة في تحميل الكتب: {e}")

# دالة التعامل مع زر "كتبي"
async def handle_custom_buttons(update: Update, context: CallbackContext) -> None:
    if update.message.text == "كتبي 📚":
        await show_books(update, context)
    else:
        await start(update, context)


# الدالة الرئيسية لتشغيل البوت
def main():
    try:
        print("بدء تشغيل البوت...")
        logger.info("بدء تهيئة البوت")

        # إعداد البوت باستخدام التوكن
        token = "7734332111:AAHCqgBEdFQB6pr382vmjJzdHQkhXSBRGm8"
        if not token or token == "":
            raise ValueError("لم يتم تعيين توكن البوت")

        application = Application.builder().token(token).build()
        logger.info("تم الاتصال بالبوت بنجاح")

        # إضافة المعالجات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button))
        application.add_handler(MessageHandler(filters.TEXT, handle_custom_buttons))

        print("تم تهيئة البوت بنجاح، جاري بدء التشغيل...")
        logger.info("تم تهيئة البوت بنجاح")

        # تشغيل البوت
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        error_msg = f"حدث خطأ في تشغيل البوت: {str(e)}"
        print(error_msg)
        logger.error(error_msg)
        raise


# تشغيل البوت إذا كان هذا هو الملف الرئيسي
if __name__ == '__main__':
    main()
