"""
Тестовый скрипт для проверки определения ближайших игр
"""
from utils.api_service import api_service
from datetime import datetime
import pytz

print("=" * 60)
print("Проверка определения предстоящих игр")
print("=" * 60)

# Текущее время
moscow_tz = pytz.timezone('Europe/Moscow')
now = datetime.now(moscow_tz)
print(f"\n⏰ Текущее время (MSK): {now.strftime('%Y-%m-%d %H:%M:%S')}")

# Получаем предстоящие игры
print("\n🔍 Получение предстоящих игр...")
upcoming = api_service.get_upcoming_games(days_ahead=90)

if not upcoming:
    print("❌ Нет предстоящих игр")
else:
    print(f"\n✅ Найдено {len(upcoming)} предстоящих игр:\n")
    
    for i, game in enumerate(upcoming[:5], 1):  # Показываем первые 5
        team_a_name = game.get('team_a', {}).get('name', 'Команда A')
        team_b_name = game.get('team_b', {}).get('name', 'Команда B')
        game_dt = game['datetime']
        
        # Вычисляем время до игры
        time_diff = (game_dt - now).total_seconds() / 3600  # в часах
        
        print(f"{i}. {team_a_name} vs {team_b_name}")
        print(f"   Дата: {game_dt.strftime('%Y-%m-%d %H:%M')}")
        print(f"   До игры: {time_diff:.1f} часов")
        print()
    
    # Показываем ближайшую игру
    next_game = upcoming[0]
    print("\n" + "=" * 60)
    print("🏒 БЛИЖАЙШАЯ ИГРА:")
    print("=" * 60)
    print(api_service.format_game_message(next_game))

print("\n" + "=" * 60)
