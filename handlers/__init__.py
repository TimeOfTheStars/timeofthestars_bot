"""
Обработчики команд бота
"""
from .start import register_start_handlers
from .notifications import register_notification_handlers
from .team_registration import register_team_handlers
from .player_registration import register_player_handlers

__all__ = [
    'register_start_handlers',
    'register_notification_handlers',
    'register_team_handlers',
    'register_player_handlers'
]
