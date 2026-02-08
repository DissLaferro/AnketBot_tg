import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from config import BOT_TOKEN, ADMIN_IDS, CHANNEL_ID
import database

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы для пагинации
ANKETY_PER_PAGE = 10

# Состояния анкеты
NAME, AGE, USERNAME, ACTIVITY, CONFLICT, ABOUT, TIMEZONE, MINECRAFT = range(8)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало анкетирования"""
    user_id = update.effective_user.id
    
    # Проверяем, есть ли уже анкета от этого пользователя
    existing_anketa = database.get_anketa_by_user_id(user_id)
    
    if existing_anketa:
        status_text = {
            "pending": "⏳ ожидает рассмотрения",
            "accepted": "✅ уже принята",
            "rejected": "❌ была отклонена"
        }
        status = status_text.get(existing_anketa['status'], 'обрабатывается')
        
        await update.message.reply_text(
            f"Вы уже отправляли анкету!\n"
            f"Статус вашей анкеты: {status}\n\n"
            f"С одного аккаунта можно отправить только одну анкету.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "👋 Привет! Добро пожаловать!\n\n"
        "Сейчас я помогу тебе заполнить анкету для вступления.\n"
        "Это займет всего пару минут.\n\n"
        "⚠️ Обрати внимание:\n"
        "• Отвечай честно и подробно\n"
        "• С одного аккаунта можно отправить только одну анкету\n"
        "• Ты можешь отменить заполнение командой /cancel\n\n"
        "Готов? Тогда начнем! 🚀\n\n"
        "1️⃣ Введи своё имя или псевдоним:",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет имя и запрашивает возраст"""
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"Приятно познакомиться, {update.message.text}! 😊\n\n"
        "2️⃣ Сколько тебе лет?\n"
        "💡 Мы принимаем участников с 14 лет"
    )
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет возраст и запрашивает юзернейм"""
    age_text = update.message.text
    try:
        age_value = int(age_text)
        if age_value < 14:
            await update.message.reply_text(
                "😔 К сожалению, мы принимаем участников с 14 лет.\n"
                "Попробуй указать корректный возраст:"
            )
            return AGE
        context.user_data['age'] = age_text
    except ValueError:
        await update.message.reply_text(
            "❌ Пожалуйста, введи возраст числом (например: 16):"
        )
        return AGE
    
    await update.message.reply_text(
        "Отлично! ✅\n\n"
        "3️⃣ Укажи свой юзернейм в Telegram\n"
        "💡 Например: @username"
    )
    return USERNAME

async def username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет юзернейм и запрашивает активность"""
    context.user_data['username'] = update.message.text
    await update.message.reply_text(
        "Записал! 📝\n\n"
        "4️⃣ Оцени свою активность по 10-балльной шкале\n"
        "💡 Насколько часто ты онлайн? (1 - редко, 10 - постоянно)"
    )
    return ACTIVITY

async def activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет активность и запрашивает конфликтность"""
    activity_text = update.message.text
    try:
        activity_value = int(activity_text)
        if not 1 <= activity_value <= 10:
            await update.message.reply_text(
                "❌ Пожалуйста, введи число от 1 до 10:"
            )
            return ACTIVITY
        context.user_data['activity'] = activity_text
    except ValueError:
        await update.message.reply_text(
            "❌ Пожалуйста, введи число от 1 до 10:"
        )
        return ACTIVITY
    
    await update.message.reply_text(
        "Понял! 👍\n\n"
        "5️⃣ Оцени свою конфликтность по 10-балльной шкале\n"
        "💡 Как часто ты вступаешь в споры? (1 - спокойный, 10 - часто конфликтую)"
    )
    return CONFLICT

async def conflict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет конфликтность и запрашивает рассказ о себе"""
    conflict_text = update.message.text
    try:
        conflict_value = int(conflict_text)
        if not 1 <= conflict_value <= 10:
            await update.message.reply_text(
                "❌ Пожалуйста, введи число от 1 до 10:"
            )
            return CONFLICT
        context.user_data['conflict'] = conflict_text
    except ValueError:
        await update.message.reply_text(
            "❌ Пожалуйста, введи число от 1 до 10:"
        )
        return CONFLICT
    
    await update.message.reply_text(
        "Хорошо! 📊\n\n"
        "6️⃣ Расскажи о себе:\n"
        "• Почему решил зайти к нам?\n"
        "• В чём ты хорош?\n"
        "• Чем увлекаешься?\n\n"
        "💡 Напиши подробно, это важно!"
    )
    return ABOUT

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет рассказ о себе и запрашивает часовой пояс"""
    context.user_data['about'] = update.message.text
    await update.message.reply_text(
        "Интересно! 🌟\n\n"
        "7️⃣ Укажи свой часовой пояс в формате ±МСК\n"
        "💡 Примеры:\n"
        "• +0МСК (Москва)\n"
        "• +3МСК (на 3 часа больше Москвы)\n"
        "• -2МСК (на 2 часа меньше Москвы)"
    )
    return TIMEZONE

async def timezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет часовой пояс и запрашивает ник в Minecraft"""
    context.user_data['timezone'] = update.message.text
    await update.message.reply_text(
        "Отлично! 🌍\n\n"
        "8️⃣ Последний вопрос!\n"
        "Укажи свой ник в Minecraft\n"
        "💡 Пиши точно, как в игре"
    )
    return MINECRAFT

async def minecraft(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохраняет ник в Minecraft и завершает анкету"""
    context.user_data['minecraft'] = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Сохраняем анкету в базу данных
    database.add_anketa(user_id, context.user_data, username)
    
    # Формируем итоговую анкету
    form = (
        "✅ Анкета заполнена!\n\n"
        f"1️⃣ Имя/псевдоним: {context.user_data['name']}\n"
        f"2️⃣ Возраст: {context.user_data['age']}\n"
        f"3️⃣ Юзернейм: {context.user_data['username']}\n"
        f"4️⃣ Активность: {context.user_data['activity']}/10\n"
        f"5️⃣ Конфликтность: {context.user_data['conflict']}/10\n"
        f"6️⃣ О себе: {context.user_data['about']}\n"
        f"7️⃣ Часовой пояс: {context.user_data['timezone']}\n"
        f"8️⃣ Ник в Minecraft: {context.user_data['minecraft']}\n\n"
        "Спасибо за заполнение анкеты!"
    )
    
    await update.message.reply_text(form)
    
    await update.message.reply_text(
        "🎯 Твоя анкета отправлена на рассмотрение!\n\n"
        "Администраторы проверят её и сообщат о решении.\n"
        "Обычно это занимает от нескольких минут до нескольких часов.\n\n"
        "Ожидай уведомления! 📬"
    )
    
    # Отправляем анкету всем администраторам
    admin_form = (
        "📋 Новая анкета!\n\n"
        f"👤 От пользователя: {update.effective_user.mention_html()}\n"
        f"🆔 User ID: {user_id}\n\n"
        f"1️⃣ Имя/псевдоним: {context.user_data['name']}\n"
        f"2️⃣ Возраст: {context.user_data['age']}\n"
        f"3️⃣ Юзернейм: {context.user_data['username']}\n"
        f"4️⃣ Активность: {context.user_data['activity']}/10\n"
        f"5️⃣ Конфликтность: {context.user_data['conflict']}/10\n"
        f"6️⃣ О себе: {context.user_data['about']}\n"
        f"7️⃣ Часовой пояс: {context.user_data['timezone']}\n"
        f"8️⃣ Ник в Minecraft: {context.user_data['minecraft']}"
    )
    
    # Создаем кнопки для админов
    keyboard = [
        [
            InlineKeyboardButton("✅ Принять", callback_data=f"accept_{user_id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем анкету каждому администратору
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_form,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            logger.info(f"Анкета от пользователя {user_id} отправлена администратору {admin_id}")
        except Exception as e:
            logger.error(f"Ошибка при отправке анкеты администратору {admin_id}: {e}")
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена заполнения анкеты"""
    await update.message.reply_text(
        "❌ Заполнение анкеты отменено.\n\n"
        "Если передумаешь, используй команду /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def ankety_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /ankety - показывает путеводитель по анкетам (только для админов)"""
    user_id = update.effective_user.id
    
    # Проверяем, является ли пользователь админом
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У вас нет доступа к этой команде.")
        return
    
    await show_ankety_list(update.message, page=0)

async def show_ankety_list(message_or_query, page: int = 0):
    """Показывает список анкет с пагинацией"""
    ankety = database.get_all_ankety()
    
    if not ankety:
        text = "📋 Анкет пока нет."
        keyboard = []
    else:
        # Сортируем по дате создания (новые первые)
        ankety.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        total_pages = (len(ankety) - 1) // ANKETY_PER_PAGE + 1
        start_idx = page * ANKETY_PER_PAGE
        end_idx = start_idx + ANKETY_PER_PAGE
        page_ankety = ankety[start_idx:end_idx]
        
        # Формируем текст
        status_emoji = {
            "pending": "⏳",
            "accepted": "✅",
            "rejected": "❌"
        }
        
        text = f"📋 Путеводитель по анкетам (страница {page + 1}/{total_pages})\n\n"
        text += f"Всего анкет: {len(ankety)}\n"
        text += f"⏳ Ожидают: {len([a for a in ankety if a['status'] == 'pending'])}\n"
        text += f"✅ Принято: {len([a for a in ankety if a['status'] == 'accepted'])}\n"
        text += f"❌ Отклонено: {len([a for a in ankety if a['status'] == 'rejected'])}\n\n"
        text += "Нажмите на имя для просмотра анкеты:"
        
        # Формируем кнопки
        keyboard = []
        for anketa in page_ankety:
            status = status_emoji.get(anketa['status'], '❓')
            button_text = f"{status} {anketa['name']}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"view_{anketa['user_id']}")])
        
        # Кнопки навигации
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"ankety_{page-1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Вперёд ➡️", callback_data=f"ankety_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # Отправляем или редактируем сообщение
    if hasattr(message_or_query, 'edit_message_text'):
        await message_or_query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await message_or_query.reply_text(text=text, reply_markup=reply_markup)

async def show_anketa_detail(query, user_id: int):
    """Показывает детальную информацию об анкете"""
    anketa = database.get_anketa_by_user_id(user_id)
    
    if not anketa:
        await query.edit_message_text("Анкета не найдена.")
        return
    
    status_text = {
        "pending": "⏳ Ожидает рассмотрения",
        "accepted": "✅ Принята",
        "rejected": "❌ Отклонена"
    }
    
    text = (
        f"📋 Анкета: {anketa['name']}\n"
        f"Статус: {status_text.get(anketa['status'], 'Неизвестно')}\n\n"
        f"1️⃣ Имя/псевдоним: {anketa['name']}\n"
        f"2️⃣ Возраст: {anketa['age']}\n"
        f"3️⃣ Юзернейм: {anketa['user_username']}\n"
        f"4️⃣ Активность: {anketa['activity']}/10\n"
        f"5️⃣ Конфликтность: {anketa['conflict']}/10\n"
        f"6️⃣ О себе: {anketa['about']}\n"
        f"7️⃣ Часовой пояс: {anketa['timezone']}\n"
        f"8️⃣ Ник в Minecraft: {anketa['minecraft']}\n\n"
        f"🆔 User ID: {anketa['user_id']}"
    )
    
    if anketa.get('username'):
        text += f"\n👤 Telegram: @{anketa['username']}"
    
    keyboard = [[InlineKeyboardButton("⬅️ Назад к списку", callback_data="back_0")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text=text, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки принять/отклонить"""
    query = update.callback_query
    await query.answer()
    
    # Парсим callback_data
    data_parts = query.data.split('_')
    action = data_parts[0]
    
    # Обработка кнопок принять/отклонить
    if action in ["accept", "reject"]:
        user_id = int(data_parts[1])
        
        if action == "accept":
            # Обновляем статус в базе
            database.update_anketa_status(user_id, "accepted")
            
            # Уведомляем пользователя о принятии
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🎉 Поздравляем! Ваша анкета принята!"
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Публикуем анкету в канал, если он настроен
            if CHANNEL_ID:
                try:
                    # Извлекаем данные анкеты из текста сообщения
                    channel_message = query.message.text_html.replace("📋 Новая анкета!", "✅ Принятая анкета")
                    
                    await context.bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=channel_message,
                        parse_mode='HTML'
                    )
                    logger.info(f"Анкета пользователя {user_id} опубликована в канале")
                except Exception as e:
                    logger.error(f"Ошибка при публикации анкеты в канал: {e}")
            
            # Обновляем сообщение админа
            await query.edit_message_text(
                text=query.message.text + "\n\n✅ ПРИНЯТО",
                parse_mode='HTML'
            )
            logger.info(f"Анкета пользователя {user_id} принята")
            
        elif action == "reject":
            # Обновляем статус в базе
            database.update_anketa_status(user_id, "rejected")
            
            # Уведомляем пользователя об отклонении
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="😔 К сожалению, ваша анкета отклонена."
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Обновляем сообщение админа
            await query.edit_message_text(
                text=query.message.text + "\n\n❌ ОТКЛОНЕНО",
                parse_mode='HTML'
            )
            logger.info(f"Анкета пользователя {user_id} отклонена")
    
    # Обработка кнопок путеводителя
    elif action == "ankety":
        page = int(data_parts[1]) if len(data_parts) > 1 else 0
        await show_ankety_list(query, page)
    
    elif action == "view":
        user_id = int(data_parts[1])
        await show_anketa_detail(query, user_id)
    
    elif action == "back":
        page = int(data_parts[1]) if len(data_parts) > 1 else 0
        await show_ankety_list(query, page)

async def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Настройка обработчика диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username)],
            ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activity)],
            CONFLICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, conflict)],
            ABOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, about)],
            TIMEZONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, timezone)],
            MINECRAFT: [MessageHandler(filters.TEXT & ~filters.COMMAND, minecraft)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('ankety', ankety_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("Бот запущен...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    
    # Держим бота запущенным
    import asyncio
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановка бота...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
