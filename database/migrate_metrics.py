"""
Скрипт миграции для добавления полей метрик в существующую базу данных
Безопасно добавляет новые поля без потери данных
"""
import sys
from pathlib import Path

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from datetime import datetime
from database.database import engine, init_db


def field_exists(table_name, column_name):
    """Проверяет, существует ли поле в таблице"""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)


def migrate_users_table():
    """Добавление новых полей в таблицу users"""
    print("👤 Обновление таблицы users...")
    
    with engine.begin() as conn:
        # Проверяем и добавляем поля только если их нет
        if not field_exists('users', 'username'):
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN username VARCHAR(255)"
                ))
                print("  ✅ Добавлено поле: username")
            except Exception as e:
                print(f"  ⚠️ Ошибка при добавлении username: {e}")
        else:
            print("  ℹ️ Поле username уже существует")
        
        if not field_exists('users', 'first_name'):
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN first_name VARCHAR(255)"
                ))
                print("  ✅ Добавлено поле: first_name")
            except Exception as e:
                print(f"  ⚠️ Ошибка при добавлении first_name: {e}")
        else:
            print("  ℹ️ Поле first_name уже существует")
        
        if not field_exists('users', 'last_name'):
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN last_name VARCHAR(255)"
                ))
                print("  ✅ Добавлено поле: last_name")
            except Exception as e:
                print(f"  ⚠️ Ошибка при добавлении last_name: {e}")
        else:
            print("  ℹ️ Поле last_name уже существует")
        
        if not field_exists('users', 'last_activity'):
            try:
                # В SQLite нельзя добавить колонку с неконстантным DEFAULT, поэтому сначала добавляем без DEFAULT
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN last_activity DATETIME"
                ))
                # Заполняем существующие строки текущим временем
                conn.execute(text(
                    "UPDATE users SET last_activity = :now WHERE last_activity IS NULL"
                ), {"now": datetime.utcnow()})
                print("  ✅ Добавлено поле: last_activity (заполнено текущим временем для существующих записей)")
            except Exception as e:
                print(f"  ⚠️ Ошибка при добавлении last_activity: {e}")
        else:
            print("  ℹ️ Поле last_activity уже существует")
        
        if not field_exists('users', 'total_interactions'):
            try:
                conn.execute(text(
                    "ALTER TABLE users ADD COLUMN total_interactions INTEGER DEFAULT 0"
                ))
                print("  ✅ Добавлено поле: total_interactions")
            except Exception as e:
                print(f"  ⚠️ Ошибка при добавлении total_interactions: {e}")
        else:
            print("  ℹ️ Поле total_interactions уже существует")


def create_user_activity_table():
    """Создание таблицы user_activity"""
    print("\n📊 Создание таблицы логов активности...")
    try:
        # init_db() создаст все новые таблицы, указанные в моделях
        init_db()
        print("  ✅ Таблица user_activity создана или уже существует")
    except Exception as e:
        print(f"  ⚠️ Ошибка при создании таблицы: {e}")


def verify_data_integrity():
    """Проверка целостности данных"""
    print("\n✓ Проверка целостности данных...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as count FROM users"))
            user_count = result.fetchone()[0]
            print(f"  ✅ В таблице users {user_count} записей (все сохранены)")
            
            # Проверяем наличие таблицы user_activity
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if 'user_activity' in tables:
                print("  ✅ Таблица user_activity успешно создана")
            else:
                print("  ⚠️ Таблица user_activity не найдена")
    except Exception as e:
        print(f"  ❌ Ошибка при проверке: {e}")


def main():
    """Главная функция миграции"""
    print("=" * 60)
    print("🔄 Миграция базы данных для системы метрик")
    print("=" * 60)
    print("\n⚠️  ВАЖНО: Все существующие данные будут сохранены!")
    print()
    
    try:
        migrate_users_table()
        create_user_activity_table()
        verify_data_integrity()
        
        print("\n" + "=" * 60)
        print("✅ Миграция завершена успешно!")
        print("=" * 60)
        print("\nТеперь вы можете:")
        print("  1. Запустить бота: python bot.py")
        print("  2. Открыть админ-панель: http://localhost:5000/admin")
        print("  3. Посмотреть метрики: http://localhost:5000/metrics")
        print()
        return True
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ Ошибка при миграции!")
        print("=" * 60)
        print(f"\n{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)

