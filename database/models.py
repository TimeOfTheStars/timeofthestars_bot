"""
Модели базы данных для хоккейной лиги
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """Пользователи, подписанные на уведомления о матчах"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    notifications_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.telegram_id}>"
    
    def __str__(self):
        return f"{self.telegram_id} {'✅' if self.notifications_enabled else '❌'}"


class Player(Base):
    """Зарегистрированные игроки (свободные агенты)"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=False)
    birth_year = Column(Integer, nullable=True)
    position = Column(String(50), nullable=True)  # forward, defender, goalie
    experience = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    preferred_team_slug = Column(String(100), nullable=True)  # slug команды из API
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Player {self.full_name} (@{self.username})>"
    
    def __str__(self):
        position = self.position or 'не указана'
        return f"{self.full_name} - {position}"


class TeamApplication(Base):
    """Заявки команд на вступление в лигу"""
    __tablename__ = 'team_applications'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)  # ID подавшего заявку
    team_name = Column(String(255), nullable=False)
    captain_name = Column(String(255), nullable=False)
    captain_phone = Column(String(20), nullable=False)
    city = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default='pending')  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    admin_comment = Column(Text, nullable=True)  # Комментарий администратора
    
    def __repr__(self):
        return f"<TeamApplication {self.team_name} ({self.status})>"
    
    def __str__(self):
        status_emoji = {'pending': '⏳', 'approved': '✅', 'rejected': '❌'}.get(self.status, '❓')
        return f"{status_emoji} {self.team_name} - {self.captain_name}"


class GameNotification(Base):
    """История отправленных уведомлений о играх"""
    __tablename__ = 'game_notifications'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, nullable=False, index=True)  # ID игры из API
    notified_at = Column(DateTime, default=datetime.utcnow)
    users_count = Column(Integer, default=0)  # Количество уведомленных пользователей
    
    def __repr__(self):
        return f"<GameNotification game_id={self.game_id} at {self.notified_at}>"
