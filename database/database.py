"""
Управление подключением к базе данных
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import config
from .models import Base


# Создание движка базы данных
engine = create_engine(
    config.DATABASE_URL,
    echo=False,  # Логирование SQL запросов (True для дебага)
    connect_args={'check_same_thread': False} if 'sqlite' in config.DATABASE_URL else {}
)

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Инициализация базы данных - создание всех таблиц
    """
    Base.metadata.create_all(bind=engine)
    print("✅ База данных инициализирована")


def get_session() -> Session:
    """
    Получение сессии базы данных
    
    Использование:
    ```python
    session = get_session()
    try:
        # работа с БД
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    ```
    """
    return SessionLocal()


def get_db():
    """
    Генератор сессии для использования в контекстном менеджере
    
    Использование:
    ```python
    with get_db() as session:
        # работа с БД
    ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
