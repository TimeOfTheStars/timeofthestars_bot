"""
Reply-клавиатуры для бота
"""
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Главное меню бота
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    
    keyboard.add(
        KeyboardButton("🏒 Матчи"),
        KeyboardButton("👥 Записать команду в лигу"),
        KeyboardButton("👤️ Записаться в команду (игрок)")
    )
    
    return keyboard


def get_back_to_menu() -> ReplyKeyboardMarkup:
    """
    Кнопка возврата в главное меню
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🏠 Главное меню"))
    
    return keyboard


def get_team_management_menu() -> ReplyKeyboardMarkup:
    """
    Меню управления заявками команд
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("➕ Добавить команду"),
        KeyboardButton("✏️ Изменить заявку")
    )
    keyboard.add(
        KeyboardButton("🗑 Удалить заявку"),
        KeyboardButton("📋 Мои заявки")
    )
    keyboard.add(KeyboardButton("🏠 Главное меню"))
    
    return keyboard


def get_player_management_menu() -> ReplyKeyboardMarkup:
    """
    Меню управления анкетами игроков
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("➕ Добавить анкету"),
        KeyboardButton("✏️ Изменить анкету")
    )
    keyboard.add(
        KeyboardButton("🗑 Удалить анкету"),
        KeyboardButton("📋 Мои анкеты")
    )
    keyboard.add(KeyboardButton("🏠 Главное меню"))
    
    return keyboard


def get_confirmation_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура подтверждения действия
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("✅ Подтвердить"),
        KeyboardButton("❌ Отменить")
    )
    
    return keyboard


def get_matches_menu(notifications_enabled: bool) -> ReplyKeyboardMarkup:
    """
    Меню для раздела матчей
    
    Args:
        notifications_enabled: Включены ли уведомления у пользователя
    """
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Кнопка вкл/выкл уведомлений в зависимости от статуса
    if notifications_enabled:
        keyboard.add(KeyboardButton("🔕 Отключить уведомления"))
    else:
        keyboard.add(KeyboardButton("🔔 Включить уведомления"))
    
    keyboard.add(KeyboardButton("➡️ Следующие 3 матча"))
    keyboard.add(
        KeyboardButton("📊 Турнирная таблица"),
        KeyboardButton("🏆 Лучшие игроки")
    )
    keyboard.add(KeyboardButton("🏠 Главное меню"))
    
    return keyboard
