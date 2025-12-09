"""
Система метрик и аналитики активности пользователей
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import func, and_
from database import get_session, User, UserActivity
from telebot.types import Message


class MetricsService:
    """Сервис для сбора и анализа метрик"""
    
    @staticmethod
    def log_activity(telegram_id: int, username: Optional[str], action: str, details: Optional[str] = None):
        """
        Логирование активности пользователя
        
        Args:
            telegram_id: ID пользователя в Telegram
            username: Username пользователя
            action: Тип действия
            details: Дополнительная информация
        """
        session = get_session()
        try:
            # Создаем запись активности
            activity = UserActivity(
                telegram_id=telegram_id,
                username=username,
                action=action,
                details=details
            )
            session.add(activity)
            
            # Обновляем счетчик и время последней активности у пользователя
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                user.last_activity = datetime.utcnow()
                user.total_interactions += 1
            
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"❌ Ошибка при логировании активности: {e}")
        finally:
            session.close()
    
    @staticmethod
    def track_message(message: Message, action: str):
        """
        Отслеживание сообщения пользователя
        
        Args:
            message: Объект сообщения от Telegram
            action: Описание действия
        """
        telegram_id = message.from_user.id
        username = message.from_user.username
        text = message.text[:100] if message.text else None  # Первые 100 символов
        
        MetricsService.log_activity(
            telegram_id=telegram_id,
            username=username,
            action=action,
            details=text
        )
    
    @staticmethod
    def get_total_users() -> int:
        """Получить общее количество пользователей"""
        session = get_session()
        try:
            return session.query(User).count()
        finally:
            session.close()
    
    @staticmethod
    def get_active_users(days: int = 7) -> int:
        """
        Получить количество активных пользователей за период
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Количество активных пользователей
        """
        session = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return session.query(User).filter(
                User.last_activity >= cutoff_date
            ).count()
        finally:
            session.close()
    
    @staticmethod
    def get_new_users(days: int = 7) -> int:
        """
        Получить количество новых пользователей за период
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Количество новых пользователей
        """
        session = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return session.query(User).filter(
                User.created_at >= cutoff_date
            ).count()
        finally:
            session.close()
    
    @staticmethod
    def get_subscribers_count() -> int:
        """Получить количество пользователей с включенными уведомлениями"""
        session = get_session()
        try:
            return session.query(User).filter_by(notifications_enabled=True).count()
        finally:
            session.close()
    
    @staticmethod
    def get_top_actions(days: int = 7, limit: int = 10):
        """
        Получить топ действий пользователей
        
        Args:
            days: Количество дней для анализа
            limit: Лимит результатов
            
        Returns:
            Список кортежей (действие, количество)
        """
        session = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            results = session.query(
                UserActivity.action,
                func.count(UserActivity.id).label('count')
            ).filter(
                UserActivity.timestamp >= cutoff_date
            ).group_by(
                UserActivity.action
            ).order_by(
                func.count(UserActivity.id).desc()
            ).limit(limit).all()
            
            return results
        finally:
            session.close()
    
    @staticmethod
    def get_total_interactions(days: int = 7) -> int:
        """
        Получить общее количество взаимодействий за период
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Количество взаимодействий
        """
        session = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return session.query(UserActivity).filter(
                UserActivity.timestamp >= cutoff_date
            ).count()
        finally:
            session.close()
    
    @staticmethod
    def get_hourly_activity(days: int = 1):
        """
        Получить почасовую активность
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Словарь {час: количество}
        """
        session = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            activities = session.query(UserActivity).filter(
                UserActivity.timestamp >= cutoff_date
            ).all()
            
            hourly_stats = {}
            for activity in activities:
                hour = activity.timestamp.hour
                hourly_stats[hour] = hourly_stats.get(hour, 0) + 1
            
            return hourly_stats
        finally:
            session.close()
    
    @staticmethod
    def get_retention_rate(days: int = 7) -> float:
        """
        Получить уровень удержания пользователей
        
        Args:
            days: Количество дней для анализа
            
        Returns:
            Процент удержания (0-100)
        """
        session = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Пользователи, зарегистрированные до cutoff_date
            old_users = session.query(User).filter(
                User.created_at < cutoff_date
            ).count()
            
            if old_users == 0:
                return 0.0
            
            # Из них активные за последние days дней
            active_old_users = session.query(User).filter(
                and_(
                    User.created_at < cutoff_date,
                    User.last_activity >= cutoff_date
                )
            ).count()
            
            return (active_old_users / old_users) * 100
        finally:
            session.close()


# Глобальный экземпляр сервиса метрик
metrics_service = MetricsService()
