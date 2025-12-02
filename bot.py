"""
Главный файл запуска Telegram бота для хоккейной лиги
"""
import telebot
from config import config
from database import init_db
from handlers import (
    register_start_handlers,
    register_notification_handlers,
    register_team_handlers,
    register_player_handlers
)


def create_bot():
    """
    Создание и настройка бота
    
    Returns:
        Настроенный экземпляр бота
    """
    if not config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден в .env файле!")
    
    bot = telebot.TeleBot(config.BOT_TOKEN)
    
    # Регистрация обработчиков
    register_start_handlers(bot)
    register_notification_handlers(bot)
    register_team_handlers(bot)
    register_player_handlers(bot)
    
    return bot


def main():
    """
    Главная функция запуска бота
    """
    print("=" * 50)
    print("🏒 Запуск бота хоккейной лиги Time of the Stars")
    print("=" * 50)
    
    # Инициализация базы данных
    print("\n📊 Инициализация базы данных...")
    init_db()
    
    # Создание бота
    print("\n🤖 Создание бота...")
    bot = create_bot()
    
    print("\n✅ Бот успешно запущен!")
    print("📱 Нажмите Ctrl+C для остановки\n")
    print("=" * 50)
    
    # Запуск polling
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except KeyboardInterrupt:
        print("\n\n⛔ Остановка бота...")
        print("👋 До свидания!")
    except Exception as e:
        print(f"\n❌ Ошибка при работе бота: {e}")
        raise


if __name__ == '__main__':
    main()
