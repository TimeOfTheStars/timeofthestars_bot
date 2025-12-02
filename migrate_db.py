"""
Скрипт миграции базы данных - добавление поля role в таблицу admins
"""
import sqlite3
from config import config

def migrate_db():
    """Добавление поля role в таблицу admins"""
    db_path = config.DATABASE_URL.replace('sqlite:///', '')
    
    print("=" * 60)
    print("🔄 Миграция базы данных")
    print("=" * 60)
    print(f"\n📂 База данных: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли уже колонка role
        cursor.execute("PRAGMA table_info(admins)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'role' in columns:
            print("\n✅ Поле 'role' уже существует в таблице admins")
        else:
            print("\n➕ Добавление поля 'role' в таблицу admins...")
            cursor.execute("ALTER TABLE admins ADD COLUMN role VARCHAR(50) DEFAULT 'manager'")
            conn.commit()
            print("✅ Поле 'role' успешно добавлено")
        
        # Обновляем существующих администраторов
        print("\n🔄 Обновление существующих администраторов...")
        cursor.execute("UPDATE admins SET role = 'admin' WHERE role IS NULL OR role = ''")
        updated = cursor.rowcount
        conn.commit()
        
        if updated > 0:
            print(f"✅ Обновлено записей: {updated}")
        else:
            print("ℹ️ Нет записей для обновления")
        
        # Показываем список администраторов
        print("\n📋 Список администраторов после миграции:")
        cursor.execute("SELECT id, username, role, is_active FROM admins")
        admins = cursor.fetchall()
        
        for admin in admins:
            admin_id, username, role, is_active = admin
            status = "✅" if is_active else "❌"
            role_emoji = "👑" if role == "admin" else "👤"
            role_name = "admin (полные права)" if role == "admin" else "manager (без удаления)"
            print(f"  {status} {role_emoji} {username} - {role_name}")
        
        print("\n" + "=" * 60)
        print("✅ Миграция завершена успешно!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Ошибка миграции: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_db()
