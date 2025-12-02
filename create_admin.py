"""
Скрипт для создания администратора системы
"""
from database import get_session, Admin, init_db
import sys


def create_admin():
    """Создание нового администратора"""
    print("=" * 60)
    print("🔐 Создание администратора")
    print("=" * 60)
    
    # Инициализация БД
    init_db()
    
    # Ввод данных
    username = input("\nВведите логин администратора: ").strip()
    if not username:
        print("❌ Логин не может быть пустым!")
        return
    
    password = input("Введите пароль: ").strip()
    if not password:
        print("❌ Пароль не может быть пустым!")
        return
    
    confirm_password = input("Подтвердите пароль: ").strip()
    if password != confirm_password:
        print("❌ Пароли не совпадают!")
        return
    
    full_name = input("Введите ФИО (необязательно): ").strip() or None
    
    # Выбор роли
    print("\nВыберите роль:")
    print("1. admin - Полные права (просмотр, редактирование, удаление)")
    print("2. manager - Ограниченные права (просмотр, редактирование, БЕЗ удаления)")
    role_choice = input("Введите номер (1 или 2): ").strip()
    
    if role_choice == "1":
        role = "admin"
    elif role_choice == "2":
        role = "manager"
    else:
        print("❌ Неверный выбор! Используется роль 'manager' по умолчанию.")
        role = "manager"
    
    # Создание администратора
    session = get_session()
    try:
        # Проверяем, существует ли уже такой логин
        existing = session.query(Admin).filter_by(username=username).first()
        if existing:
            print(f"\n❌ Администратор с логином '{username}' уже существует!")
            return
        
        # Создаем нового администратора
        admin = Admin(
            username=username,
            full_name=full_name,
            role=role,
            is_active=True
        )
        admin.set_password(password)
        
        session.add(admin)
        session.commit()
        
        role_name = "Администратор (полные права)" if role == "admin" else "Менеджер (без удаления)"
        
        print("\n" + "=" * 60)
        print("✅ Администратор успешно создан!")
        print("=" * 60)
        print(f"\n👤 Логин: {username}")
        print(f"👤 ФИО: {full_name or 'не указано'}")
        print(f"🔑 Роль: {role_name}")
        print(f"\n🔗 Войти в админ-панель: http://localhost:5000/admin")
        print("\n" + "=" * 60)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Ошибка при создании администратора: {e}")
    finally:
        session.close()


def list_admins():
    """Список всех администраторов"""
    print("=" * 60)
    print("📋 Список администраторов")
    print("=" * 60)
    
    init_db()
    session = get_session()
    
    try:
        admins = session.query(Admin).all()
        
        if not admins:
            print("\n⚠️ Нет зарегистрированных администраторов")
            return
        
        print()
        for admin in admins:
            status = "✅ Активен" if admin.is_active else "❌ Отключен"
            role_emoji = "👑" if admin.role == "admin" else "👤"
            role_name = "Администратор (полные права)" if admin.role == "admin" else "Менеджер (без удаления)"
            
            print(f"ID: {admin.id}")
            print(f"  Логин: {admin.username}")
            print(f"  ФИО: {admin.full_name or 'не указано'}")
            print(f"  Роль: {role_emoji} {role_name}")
            print(f"  Статус: {status}")
            print(f"  Создан: {admin.created_at.strftime('%Y-%m-%d %H:%M')}")
            if admin.last_login:
                print(f"  Последний вход: {admin.last_login.strftime('%Y-%m-%d %H:%M')}")
            print()
        
        print("=" * 60)
    finally:
        session.close()


def reset_password():
    """Сброс пароля администратора"""
    print("=" * 60)
    print("🔄 Сброс пароля администратора")
    print("=" * 60)
    
    init_db()
    
    username = input("\nВведите логин администратора: ").strip()
    if not username:
        print("❌ Логин не может быть пустым!")
        return
    
    session = get_session()
    try:
        admin = session.query(Admin).filter_by(username=username).first()
        if not admin:
            print(f"\n❌ Администратор с логином '{username}' не найден!")
            return
        
        new_password = input("Введите новый пароль: ").strip()
        if not new_password:
            print("❌ Пароль не может быть пустым!")
            return
        
        confirm_password = input("Подтвердите новый пароль: ").strip()
        if new_password != confirm_password:
            print("❌ Пароли не совпадают!")
            return
        
        admin.set_password(new_password)
        session.commit()
        
        print(f"\n✅ Пароль для '{username}' успешно изменен!")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Ошибка при сбросе пароля: {e}")
    finally:
        session.close()


def main():
    """Главное меню"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "create":
            create_admin()
        elif command == "list":
            list_admins()
        elif command == "reset":
            reset_password()
        else:
            print(f"❌ Неизвестная команда: {command}")
            print_usage()
    else:
        print("\n🔐 Управление администраторами\n")
        print("1. Создать нового администратора")
        print("2. Показать список администраторов")
        print("3. Сбросить пароль администратора")
        print("0. Выход")
        
        choice = input("\nВыберите действие: ").strip()
        
        if choice == "1":
            create_admin()
        elif choice == "2":
            list_admins()
        elif choice == "3":
            reset_password()
        elif choice == "0":
            print("До свидания!")
        else:
            print("❌ Неверный выбор!")


def print_usage():
    """Вывод справки"""
    print("\nИспользование:")
    print("  python create_admin.py          - интерактивный режим")
    print("  python create_admin.py create   - создать администратора")
    print("  python create_admin.py list     - список администраторов")
    print("  python create_admin.py reset    - сбросить пароль")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Отменено пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
