"""
Обработчик матчей и уведомлений
"""
from telebot import TeleBot
from telebot.types import Message
from database import get_session, User
from keyboards.reply_keyboards import get_back_to_menu, get_matches_menu
from utils import api_service


# Хранилище состояния пагинации для каждого пользователя
user_matches_offset = {}


def register_notification_handlers(bot: TeleBot):
    """Регистрация обработчиков для матчей и уведомлений"""
    
    @bot.message_handler(func=lambda message: message.text == "🏒 Матчи")
    def matches_menu(message: Message):
        """Меню матчей - показываем ближайший матч"""
        user_id = message.from_user.id
        
        # Сброс смещения при входе в меню
        user_matches_offset[user_id] = 0
        
        session = get_session()
        try:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            
            if not user:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Ошибка: пользователь не найден. Попробуйте /start"
                )
                return
            
            # Получаем предстоящие матчи
            upcoming = api_service.get_upcoming_games(days_ahead=90)
            
            if not upcoming:
                bot.send_message(
                    message.chat.id,
                    "📅 Нет информации о предстоящих матчах.",
                    reply_markup=get_matches_menu(user.notifications_enabled)
                )
                return
            
            # Показываем ближайший матч
            next_game = upcoming[0]
            game_message = "🏒 <b>Ближайший матч:</b>\n\n" + api_service.format_game_message(next_game)
            
            # Добавляем информацию о статусе уведомлений
            if user.notifications_enabled:
                game_message += "\n\n🔔 Уведомления включены"
            else:
                game_message += "\n\n🔕 Уведомления отключены"
            
            bot.send_message(
                message.chat.id,
                game_message,
                parse_mode='HTML',
                reply_markup=get_matches_menu(user.notifications_enabled)
            )
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text in ["🔔 Включить уведомления", "🔕 Отключить уведомления"])
    def toggle_notifications(message: Message):
        """Переключение уведомлений"""
        user_id = message.from_user.id
        
        session = get_session()
        try:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            
            if not user:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Ошибка: пользователь не найден. Попробуйте /start"
                )
                return
            
            # Переключаем статус
            user.notifications_enabled = not user.notifications_enabled
            session.commit()
            
            if user.notifications_enabled:
                response = "✅ Уведомления включены!\n\nВы будете получать уведомления о предстоящих матчах."
            else:
                response = "🔕 Уведомления отключены."
            
            bot.send_message(
                message.chat.id,
                response,
                reply_markup=get_matches_menu(user.notifications_enabled)
            )
        except Exception as e:
            session.rollback()
            bot.send_message(
                message.chat.id,
                f"❌ Ошибка: {e}",
                reply_markup=get_back_to_menu()
            )
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text == "➡️ Следующие 3 матча")
    def show_next_matches(message: Message):
        """Показать следующие 3 матча"""
        user_id = message.from_user.id
        
        # Получаем текущее смещение
        offset = user_matches_offset.get(user_id, 0)
        
        session = get_session()
        try:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            
            if not user:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Ошибка: пользователь не найден. Попробуйте /start"
                )
                return
            
            # Получаем предстоящие матчи
            upcoming = api_service.get_upcoming_games(days_ahead=90)
            
            if not upcoming:
                bot.send_message(
                    message.chat.id,
                    "📅 Нет информации о предстоящих матчах.",
                    reply_markup=get_matches_menu(user.notifications_enabled)
                )
                return
            
            # Вычисляем новое смещение (пропускаем первый матч при первом запросе)
            if offset == 0:
                offset = 1  # Пропускаем ближайший, который уже показан
            else:
                offset += 3  # Увеличиваем на 3 для следующих
            
            # Проверяем, есть ли еще матчи
            if offset >= len(upcoming):
                bot.send_message(
                    message.chat.id,
                    "📅 Больше нет запланированных матчей.",
                    reply_markup=get_matches_menu(user.notifications_enabled)
                )
                # Сбрасываем смещение
                user_matches_offset[user_id] = 0
                return
            
            # Получаем следующие 3 матча
            next_matches = upcoming[offset:offset+3]
            
            # Отправляем информацию о матчах
            for idx, game in enumerate(next_matches, 1):
                game_message = api_service.format_game_message(game)
                bot.send_message(
                    message.chat.id,
                    game_message,
                    parse_mode='HTML'
                )
            
            # Обновляем смещение
            user_matches_offset[user_id] = offset
            
            # Информируем о количестве оставшихся матчей
            remaining = len(upcoming) - (offset + len(next_matches))
            if remaining > 0:
                bot.send_message(
                    message.chat.id,
                    f"Ещё {remaining} матчей доступно.",
                    reply_markup=get_matches_menu(user.notifications_enabled)
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "Это все запланированные матчи.",
                    reply_markup=get_matches_menu(user.notifications_enabled)
                )
                # Сбрасываем смещение для следующего раза
                user_matches_offset[user_id] = 0
                
        finally:
            session.close()
