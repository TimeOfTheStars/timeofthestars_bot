"""
Обработчик команды /start и главного меню
"""
from telebot import TeleBot
from telebot.types import Message
from database import get_session, User
from keyboards.reply_keyboards import get_main_menu


def register_start_handlers(bot: TeleBot):
    """Регистрация обработчиков для /start"""
    
    @bot.message_handler(commands=['start'])
    def start_command(message: Message):
        """Обработка команды /start"""
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        
        # Сохранение/обновление пользователя в БД
        session = get_session()
        try:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            
            if not user:
                # Создание нового пользователя
                user = User(
                    telegram_id=user_id,
                    notifications_enabled=False
                )
                session.add(user)
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Ошибка при сохранении пользователя: {e}")
        finally:
            session.close()
        
        # Приветственное сообщение
        welcome_text = (
            f"🏒 Добро пожаловать, {first_name}!\n\n"
            "Это бот хоккейной лиги Time of the Stars.\n\n"
            "Здесь вы можете:\n"
            "🏒 Смотреть расписание матчей и включать уведомления\n"
            "👥 Зарегистрировать свою команду в лиге\n"
            "👤️ Записаться в команду как игрок\n\n"
            "Выберите действие из меню ниже:"
        )
        
        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=get_main_menu()
        )
    
    @bot.message_handler(func=lambda message: message.text == "🏠 Главное меню")
    def main_menu(message: Message):
        """Возврат в главное меню"""
        text = (
            "🏠 Главное меню\n\n"
            "Выберите нужное действие:"
        )
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=get_main_menu()
        )
