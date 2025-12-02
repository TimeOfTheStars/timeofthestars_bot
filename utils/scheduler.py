"""
Планировщик уведомлений о предстоящих матчах
"""
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from telebot import TeleBot
from database import get_session, User, GameNotification
from utils.api_service import api_service
from config import config


class NotificationScheduler:
    """Планировщик для отправки уведомлений о матчах"""
    
    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.scheduler = BackgroundScheduler(timezone=pytz.timezone('Europe/Moscow'))
        self.notification_hours = config.NOTIFICATION_HOURS_BEFORE
    
    def start(self):
        """Запуск планировщика"""
        # Проверяем матчи каждые 10 минут
        self.scheduler.add_job(
            self.check_upcoming_games,
            trigger=IntervalTrigger(minutes=10),
            id='check_games',
            name='Проверка предстоящих матчей',
            replace_existing=True
        )
        
        self.scheduler.start()
        print(f"✅ Планировщик уведомлений запущен (проверка каждые 10 минут)")
        print(f"⏰ Уведомления будут отправляться за {self.notification_hours} часа до матча")
    
    def stop(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        print("⛔ Планировщик уведомлений остановлен")
    
    def check_upcoming_games(self):
        """Проверка предстоящих игр и отправка уведомлений"""
        try:
            print(f"\n🔍 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Проверка предстоящих матчей...")
            
            # Получаем предстоящие матчи
            upcoming_games = api_service.get_upcoming_games(days_ahead=7)
            
            if not upcoming_games:
                print("   Нет предстоящих матчей")
                return
            
            session = get_session()
            try:
                # Текущее время
                now = datetime.now(pytz.timezone('Europe/Moscow'))
                
                for game in upcoming_games:
                    try:
                        # Парсим дату и время игры
                        game_datetime_str = f"{game['date']} {game['time']}"
                        game_datetime = datetime.strptime(game_datetime_str, '%Y-%m-%d %H:%M:%S')
                        game_datetime = pytz.timezone('Europe/Moscow').localize(game_datetime)
                        
                        # Вычисляем время отправки уведомления
                        notification_time = game_datetime - timedelta(hours=self.notification_hours)
                        
                        # Проверяем, нужно ли отправлять уведомление
                        # Уведомление отправляется в период от N часов до N-1 часов до игры
                        time_until_game = (game_datetime - now).total_seconds() / 3600  # в часах
                        
                        # Проверяем, не отправляли ли мы уже уведомление для этой игры
                        already_notified = session.query(GameNotification).filter_by(
                            game_id=game['id']
                        ).first()
                        
                        if already_notified:
                            continue
                        
                        # Если до игры осталось от N до N-1 часов, отправляем уведомление
                        if self.notification_hours - 1 < time_until_game <= self.notification_hours:
                            print(f"   📢 Отправка уведомлений о матче #{game['id']} "
                                  f"({game.get('team_a', {}).get('name', 'Команда A')} vs "
                                  f"{game.get('team_b', {}).get('name', 'Команда B')})")
                            
                            self.send_game_notification(game, session)
                        elif time_until_game <= 0:
                            print(f"   ⏰ Матч #{game['id']} уже начался или прошел")
                        else:
                            print(f"   ⏳ До матча #{game['id']} осталось {time_until_game:.1f} ч")
                    
                    except Exception as e:
                        print(f"   ❌ Ошибка при обработке игры {game.get('id')}: {e}")
                        continue
            
            finally:
                session.close()
        
        except Exception as e:
            print(f"   ❌ Ошибка при проверке предстоящих матчей: {e}")
    
    def send_game_notification(self, game: dict, session):
        """
        Отправка уведомления о предстоящей игре всем подписанным пользователям
        
        Args:
            game: Информация об игре
            session: Сессия БД
        """
        try:
            # Получаем всех пользователей с включенными уведомлениями
            users = session.query(User).filter_by(notifications_enabled=True).all()
            
            if not users:
                print(f"   ⚠️ Нет пользователей с включенными уведомлениями")
                return
            
            # Формируем сообщение
            message = "🔔 <b>Напоминание о предстоящем матче!</b>\n\n"
            message += api_service.format_game_message(game)
            
            # Отправляем уведомления
            success_count = 0
            for user in users:
                try:
                    self.bot.send_message(
                        user.telegram_id,
                        message,
                        parse_mode='HTML'
                    )
                    success_count += 1
                except Exception as e:
                    print(f"   ❌ Ошибка при отправке уведомления пользователю {user.telegram_id}: {e}")
            
            # Сохраняем информацию об отправленном уведомлении
            notification = GameNotification(
                game_id=game['id'],
                users_count=success_count
            )
            session.add(notification)
            session.commit()
            
            print(f"   ✅ Уведомления отправлены {success_count} пользователям")
        
        except Exception as e:
            print(f"   ❌ Ошибка при отправке уведомлений: {e}")
            session.rollback()
