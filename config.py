"""
Конфигурация проекта
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Основные настройки приложения"""
    
    # Telegram Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # External API
    API_TEAMS = os.getenv('API_TEAMS')
    API_GAMES = os.getenv('API_GAMES')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # SQLAdmin
    ADMIN_SECRET_KEY = os.getenv('ADMIN_SECRET_KEY')
    ADMIN_PORT = int(os.getenv('ADMIN_PORT'))
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    
    # Уведомления
    NOTIFICATION_HOURS_BEFORE = int(os.getenv('NOTIFICATION_HOURS_BEFORE'))


config = Config()
