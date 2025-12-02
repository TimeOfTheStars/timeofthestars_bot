"""
Настройка SQLAdmin панели для управления базой данных
"""
from starlette.applications import Starlette
from sqladmin import Admin, ModelView
from database.models import User, Player, TeamApplication, GameNotification
from database.database import engine
from config import config
from starlette.responses import HTMLResponse
from starlette.routing import Route


class UserAdmin(ModelView, model=User):
    """Админка для пользователей (подписчики уведомлений)"""
    
    # Настройки отображения
    name = "Подписчик"
    name_plural = "Подписчики на уведомления"
    icon = "fa-solid fa-bell"
    
    # Колонки в списке
    column_list = [
        User.id,
        User.telegram_id,
        User.notifications_enabled,
        User.created_at
    ]
    
    # Колонки для поиска
    column_searchable_list = [User.telegram_id]
    
    # Фильтры
    column_filters = [User.notifications_enabled, User.created_at]
    
    # Сортировка по умолчанию
    column_default_sort = [(User.created_at, True)]
    
    # Форматирование названий колонок
    column_labels = {
        User.id: 'ID',
        User.telegram_id: 'Telegram ID',
        User.notifications_enabled: 'Уведомления',
        User.created_at: 'Дата регистрации'
    }


class TeamApplicationAdmin(ModelView, model=TeamApplication):
    """Админка для заявок команд"""
    
    name = "Заявка команды"
    name_plural = "Заявки команд"
    icon = "fa-solid fa-users"
    
    column_list = [
        TeamApplication.id,
        TeamApplication.team_name,
        TeamApplication.captain_name,
        TeamApplication.captain_phone,
        TeamApplication.city,
        TeamApplication.status,
        TeamApplication.created_at
    ]
    
    column_searchable_list = [TeamApplication.team_name, TeamApplication.captain_name, TeamApplication.city]
    column_filters = [TeamApplication.status, TeamApplication.city, TeamApplication.created_at]
    column_default_sort = [(TeamApplication.created_at, True)]
    
    column_labels = {
        TeamApplication.id: 'ID',
        TeamApplication.telegram_id: 'Telegram ID подавшего',
        TeamApplication.team_name: 'Название команды',
        TeamApplication.captain_name: 'Капитан',
        TeamApplication.captain_phone: 'Телефон',
        TeamApplication.city: 'Город',
        TeamApplication.description: 'Описание',
        TeamApplication.status: 'Статус',
        TeamApplication.admin_comment: 'Комментарий админа',
        TeamApplication.created_at: 'Дата заявки'
    }


class PlayerAdmin(ModelView, model=Player):
    """Админка для игроков"""
    
    name = "Игрок"
    name_plural = "Игроки"
    icon = "fa-solid fa-user"
    
    column_list = [
        Player.id,
        Player.full_name,
        Player.position,
        Player.birth_year,
        Player.phone,
        Player.preferred_team_slug,
        Player.created_at
    ]
    
    column_searchable_list = [Player.full_name, Player.username]
    column_filters = [Player.position, Player.birth_year, Player.created_at]
    column_default_sort = [(Player.created_at, True)]
    
    column_labels = {
        Player.id: 'ID',
        Player.telegram_id: 'Telegram ID',
        Player.username: 'Username',
        Player.full_name: 'ФИО',
        Player.birth_year: 'Год рождения',
        Player.position: 'Позиция',
        Player.experience: 'Опыт',
        Player.phone: 'Телефон',
        Player.preferred_team_slug: 'Предпочитаемая команда (slug)',
        Player.created_at: 'Дата регистрации',
        Player.updated_at: 'Обновлено'
    }


class GameNotificationAdmin(ModelView, model=GameNotification):
    """Админка для истории уведомлений"""
    
    name = "Уведомление"
    name_plural = "История уведомлений"
    icon = "fa-solid fa-bell"
    
    column_list = [
        GameNotification.id,
        GameNotification.game_id,
        GameNotification.users_count,
        GameNotification.notified_at
    ]
    
    column_filters = [GameNotification.game_id, GameNotification.notified_at]
    column_default_sort = [(GameNotification.notified_at, True)]
    
    column_labels = {
        GameNotification.id: 'ID',
        GameNotification.game_id: 'ID игры',
        GameNotification.users_count: 'Количество уведомленных',
        GameNotification.notified_at: 'Дата отправки'
    }


def create_admin_app():
    """
    Создание Starlette приложения с админ-панелью
    
    Returns:
        Starlette app с настроенной админ-панелью
    """
    
    async def homepage(request):
        html = """
        <html>
            <head>
                <title>Админ-панель</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .container {
                        text-align: center;
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    }
                    h1 {
                        color: #333;
                        margin-bottom: 20px;
                    }
                    a {
                        display: inline-block;
                        padding: 15px 30px;
                        background: #667eea;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        font-size: 18px;
                        transition: background 0.3s;
                    }
                    a:hover {
                        background: #764ba2;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🏒 Хоккейная лига Time of the Stars</h1>
                    <p>Административная панель</p>
                    <a href="/admin">Войти в админ-панель</a>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(html)
    
    app = Starlette(
        routes=[
            Route('/', homepage),
        ]
    )
    
    # Создание админ-панели
    admin = Admin(
        app,
        engine,
        title="Админ-панель хоккейной лиги",
        base_url='/admin'
    )
    
    # Регистрация моделей
    admin.add_view(UserAdmin)
    admin.add_view(TeamApplicationAdmin)
    admin.add_view(PlayerAdmin)
    admin.add_view(GameNotificationAdmin)
    
    return app


if __name__ == '__main__':
    import uvicorn
    
    app = create_admin_app()
    
    print("=" * 60)
    print("🔧 Запуск админ-панели SQLAdmin")
    print("=" * 60)
    print(f"\n📍 Главная: http://localhost:{config.ADMIN_PORT}")
    print(f"🔐 Админка: http://localhost:{config.ADMIN_PORT}/admin")
    print("\n📱 Нажмите Ctrl+C для остановки\n")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=config.ADMIN_PORT
    )
