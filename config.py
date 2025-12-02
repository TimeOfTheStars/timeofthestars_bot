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
    API_TEAMS = os.getenv('API_TEAMS', 'https://api.timeofthestars.ru/teams')
    API_GAMES = os.getenv('API_GAMES', 'https://api.timeofthestars.ru/games')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///hockey_league.db')
    
    # SQLAdmin
    ADMIN_SECRET_KEY = os.getenv('ADMIN_SECRET_KEY', 'your-secret-key-change-in-production')
    ADMIN_PORT = int(os.getenv('ADMIN_PORT', 5000))
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')
    
    # Уведомления
    NOTIFICATION_HOURS_BEFORE = int(os.getenv('NOTIFICATION_HOURS_BEFORE', 2))


config = Config()
