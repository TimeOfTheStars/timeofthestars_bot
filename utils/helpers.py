"""
Вспомогательные функции
"""
from datetime import datetime, timedelta


def format_datetime(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
    """
    Форматирование даты и времени
    
    Args:
        dt: Объект datetime
        format_str: Формат вывода
        
    Returns:
        Отформатированная строка
    """
    return dt.strftime(format_str)


def calculate_notification_time(broadcast_datetime: datetime, hours_before: int = 2) -> datetime:
    """
    Вычисление времени отправки уведомления
    
    Args:
        broadcast_datetime: Время трансляции
        hours_before: За сколько часов до трансляции отправить уведомление
        
    Returns:
        Время отправки уведомления
    """
    return broadcast_datetime - timedelta(hours=hours_before)


def escape_markdown(text: str) -> str:
    """
    Экранирование специальных символов для Markdown
    
    Args:
        text: Исходный текст
        
    Returns:
        Текст с экранированными символами
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text
