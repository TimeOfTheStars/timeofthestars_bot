"""
Тестовый скрипт для проверки логики уведомлений
"""
from datetime import datetime, timedelta
import pytz
from utils.api_service import api_service
from config import config

print("=" * 60)
print("Проверка логики уведомлений")
print("=" * 60)

moscow_tz = pytz.timezone('Europe/Moscow')
now = datetime.now(moscow_tz)
notification_hours = config.NOTIFICATION_HOURS_BEFORE

print(f"\n⏰ Текущее время (MSK): {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📢 Уведомления отправляются за {notification_hours} часа до игры")
print(f"   (в период от {notification_hours} до {notification_hours - 1} часов до матча)")

# Получаем предстоящие игры
upcoming = api_service.get_upcoming_games(days_ahead=90)

if not upcoming:
    print("\n❌ Нет предстоящих игр")
else:
    print(f"\n🔍 Анализ {len(upcoming)} предстоящих игр:\n")
    
    for game in upcoming[:10]:  # Первые 10 игр
        team_a_name = game.get('team_a', {}).get('name', 'Команда A')
        team_b_name = game.get('team_b', {}).get('name', 'Команда B')
        game_dt = game['datetime']
        
        # Вычисляем время до игры в часах
        time_until_game = (game_dt - now).total_seconds() / 3600
        
        # Проверяем, попадает ли игра в окно уведомлений
        should_notify = notification_hours - 1 < time_until_game <= notification_hours
        
        status = "🔔 ОТПРАВИТЬ УВЕДОМЛЕНИЕ" if should_notify else "⏳ Ожидание"
        
        print(f"ID {game['id']}: {team_a_name} vs {team_b_name}")
        print(f"  Дата/время: {game_dt.strftime('%Y-%m-%d %H:%M')}")
        print(f"  До игры: {time_until_game:.2f} ч")
        print(f"  Статус: {status}")
        print()

print("=" * 60)
