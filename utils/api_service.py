"""
Сервис для работы с внешним API лиги
"""
import requests
from typing import List, Dict, Optional
from config import config
from datetime import datetime


class APIService:
    """Сервис для работы с API Time of the Stars"""
    
    def __init__(self):
        self.teams_url = config.API_TEAMS
        self.games_url = config.API_GAMES
        self._teams_cache = None
        self._games_cache = None
    
    def get_teams(self, force_refresh: bool = False) -> List[Dict]:
        """
        Получение списка команд
        
        Args:
            force_refresh: Принудительно обновить кэш
            
        Returns:
            Список команд
        """
        if self._teams_cache is None or force_refresh:
            try:
                response = requests.get(self.teams_url, timeout=10)
                response.raise_for_status()
                self._teams_cache = response.json()
            except Exception as e:
                print(f"❌ Ошибка при получении команд: {e}")
                return []
        
        return self._teams_cache or []
    
    def get_team_by_id(self, team_id: int) -> Optional[Dict]:
        """
        Получение команды по ID
        
        Args:
            team_id: ID команды
            
        Returns:
            Информация о команде или None
        """
        teams = self.get_teams()
        for team in teams:
            if team.get('id') == team_id:
                return team
        return None
    
    def get_team_by_slug(self, slug: str) -> Optional[Dict]:
        """
        Получение команды по slug
        
        Args:
            slug: Slug команды
            
        Returns:
            Информация о команде или None
        """
        teams = self.get_teams()
        for team in teams:
            if team.get('slug') == slug:
                return team
        return None
    
    def get_games(self, force_refresh: bool = False) -> List[Dict]:
        """
        Получение списка игр
        
        Args:
            force_refresh: Принудительно обновить кэш
            
        Returns:
            Список игр
        """
        if self._games_cache is None or force_refresh:
            try:
                response = requests.get(self.games_url, timeout=10)
                response.raise_for_status()
                self._games_cache = response.json()
            except Exception as e:
                print(f"❌ Ошибка при получении игр: {e}")
                return []
        
        return self._games_cache or []
    
    def get_game_by_id(self, game_id: int) -> Optional[Dict]:
        """
        Получение игры по ID
        
        Args:
            game_id: ID игры
            
        Returns:
            Информация об игре или None
        """
        games = self.get_games()
        for game in games:
            if game.get('id') == game_id:
                return game
        return None
    
    def get_upcoming_games(self, days_ahead: int = 7) -> List[Dict]:
        """
        Получение предстоящих игр
        
        Args:
            days_ahead: На сколько дней вперед смотреть
            
        Returns:
            Список предстоящих игр с информацией о командах
        """
        games = self.get_games(force_refresh=True)
        upcoming = []
        today = datetime.now().date()
        
        for game in games:
            try:
                game_date = datetime.strptime(game['date'], '%Y-%m-%d').date()
                
                if game_date >= today:
                    # Добавляем информацию о командах
                    team_a = self.get_team_by_id(game['team_a_id'])
                    team_b = self.get_team_by_id(game['team_b_id'])
                    
                    game_info = game.copy()
                    game_info['team_a'] = team_a
                    game_info['team_b'] = team_b
                    
                    upcoming.append(game_info)
            except Exception as e:
                print(f"⚠️ Ошибка при обработке игры {game.get('id')}: {e}")
                continue
        
        # Сортировка по дате
        upcoming.sort(key=lambda x: (x['date'], x['time']))
        
        return upcoming
    
    def format_game_message(self, game: Dict) -> str:
        """
        Форматирование информации об игре для сообщения
        
        Args:
            game: Информация об игре
            
        Returns:
            Отформатированное сообщение
        """
        team_a = game.get('team_a', {})
        team_b = game.get('team_b', {})
        
        team_a_name = team_a.get('name', 'Команда A')
        team_b_name = team_b.get('name', 'Команда B')
        
        date_str = game.get('date', '')
        time_str = game.get('time', '')
        location = game.get('location', 'Место не указано')
        
        # Форматирование даты
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_formatted = date_obj.strftime('%d.%m.%Y')
        except:
            date_formatted = date_str
        
        # Форматирование времени
        try:
            time_obj = datetime.strptime(time_str, '%H:%M:%S')
            time_formatted = time_obj.strftime('%H:%M')
        except:
            time_formatted = time_str
        
        message = (
            # f"🏒 <b>Предстоящий матч</b>\n\n"
            f"🏟 <b>{team_a_name}</b> vs <b>{team_b_name}</b>\n\n"
            f"📅 Дата: {date_formatted}\n"
            f"⏰ Время: {time_formatted}\n"
            f"📍 Место: {location}\n"
        )
        
        if game.get('video_url'):
            message += f"\n🎥 <a href='{game['video_url']}'>Ссылка на трансляцию</a>\n"

        message += f"\n📊 <a href='https://timeofthestars.ru/zvezdaOtechestva?tab=table'>Турнирная таблица</a> | <a href='https://timeofthestars.ru/zvezdaOtechestva?tab=bestPlayers'>Лучшие игроки</a>"
        
        return message


# Глобальный экземпляр сервиса
api_service = APIService()
