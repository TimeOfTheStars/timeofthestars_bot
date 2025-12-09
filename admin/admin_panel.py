"""
Настройка SQLAdmin панели для управления базой данных
"""
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from database.models import User, Player, TeamApplication, GameNotification, Admin as AdminModel, UserActivity
from database.database import engine, get_session
from config import config
from starlette.responses import HTMLResponse, Response
from starlette.routing import Route
from datetime import datetime
from typing import Optional
from wtforms import PasswordField, SelectField
from wtforms.validators import Optional as OptionalValidator
from utils.metrics import metrics_service


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
        User.username,
        User.first_name,
        User.notifications_enabled,
        User.total_interactions,
        User.last_activity,
        User.created_at
    ]
    
    # Колонки для поиска
    column_searchable_list = [User.telegram_id, User.username, User.first_name, User.last_name]
    
    # Фильтры
    column_filters = [User.notifications_enabled, User.created_at, User.last_activity]
    
    # Сортировка по умолчанию
    column_default_sort = [(User.last_activity, True)]
    
    # Форматирование названий колонок
    column_labels = {
        User.id: 'ID',
        User.telegram_id: 'Telegram ID',
        User.username: 'Username',
        User.first_name: 'Имя',
        User.last_name: 'Фамилия',
        User.notifications_enabled: 'Уведомления',
        User.total_interactions: 'Всего действий',
        User.last_activity: 'Последняя активность',
        User.created_at: 'Дата регистрации'
    }
    
    def is_accessible(self, request: Request) -> bool:
        """Проверка доступа"""
        return request.session.get("admin_role") in ["admin", "manager"]


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
    
    def is_accessible(self, request: Request) -> bool:
        """Проверка доступа"""
        return request.session.get("admin_role") in ["admin", "manager"]


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
    
    def is_accessible(self, request: Request) -> bool:
        """Проверка доступа"""
        return request.session.get("admin_role") in ["admin", "manager"]


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
    
    def is_accessible(self, request: Request) -> bool:
        """Проверка доступа"""
        return request.session.get("admin_role") in ["admin", "manager"]


class AdminUserAdmin(ModelView, model=AdminModel):
    """Админка для управления администраторами"""
    
    name = "Администратор"
    name_plural = "Администраторы"
    icon = "fa-solid fa-user-shield"
    
    column_list = [
        AdminModel.id,
        AdminModel.username,
        AdminModel.full_name,
        AdminModel.role,
        AdminModel.is_active,
        AdminModel.last_login,
        AdminModel.created_at
    ]
    
    column_searchable_list = [AdminModel.username, AdminModel.full_name]
    column_filters = [AdminModel.is_active, AdminModel.role, AdminModel.created_at]
    column_default_sort = [(AdminModel.created_at, True)]
    
    column_labels = {
        AdminModel.id: 'ID',
        AdminModel.username: 'Логин',
        AdminModel.password_hash: 'Хеш пароля',
        AdminModel.full_name: 'ФИО',
        AdminModel.role: 'Роль',
        AdminModel.is_active: 'Активен',
        AdminModel.created_at: 'Дата создания',
        AdminModel.last_login: 'Последний вход'
    }
    
    # Скрываем хеш пароля из деталей
    column_details_exclude_list = [AdminModel.password_hash]
    
    # Только нужные поля для формы (без password_hash и last_login)
    form_columns = [
        AdminModel.username,
        AdminModel.full_name,
        AdminModel.is_active
    ]
    
    async def scaffold_form(self):
        """Создание формы с дополнительными полями"""
        form_class = await super().scaffold_form()
        
        # Добавляем поле выбора роли
        form_class.role = SelectField(
            'Роль',
            choices=[
                ('admin', 'Администратор (полные права)'),
                ('manager', 'Менеджер (без удаления)')
            ],
            default='manager'
        )
        
        # Добавляем поле для смены пароля
        form_class.new_password = PasswordField(
            'Новый пароль',
            validators=[OptionalValidator()],
            description='Оставьте пустым, чтобы не менять пароль'
        )
        
        return form_class
    
    async def on_model_change(self, data: dict, model: AdminModel, is_created: bool, request: Request) -> None:
        """Вызывается перед сохранением модели"""
        # При редактировании заполняем текущую роль, если она не пришла из формы
        if not is_created and 'role' not in data:
            data['role'] = model.role
    
    def _normalize_wtform_data(self, model: AdminModel) -> dict:
        """Нормализация данных модели для WTForms (добавляем роль)"""
        data = super()._normalize_wtform_data(model)
        # Добавляем текущую роль для предзаполнения формы
        data['role'] = model.role
        return data
    
    async def insert_model(self, request: Request, data: dict) -> Optional[AdminModel]:
        """Создание нового администратора"""
        new_password = data.pop('new_password', None)
        role = data.pop('role', 'manager')  # Извлекаем роль из extra_fields
        
        session = get_session()
        try:
            admin = AdminModel(**data)
            admin.role = role  # Устанавливаем роль
            
            if new_password:
                admin.set_password(new_password)
            else:
                # Устанавливаем дефолтный пароль, если не указан
                admin.set_password('password')
            
            session.add(admin)
            session.commit()
            session.refresh(admin)
            return admin
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    async def update_model(self, request: Request, pk: str, data: dict) -> Optional[AdminModel]:
        """Обновление администратора"""
        new_password = data.pop('new_password', None)
        role = data.pop('role', None)  # Извлекаем роль из extra_fields
        
        session = get_session()
        try:
            admin = session.query(AdminModel).filter(AdminModel.id == pk).first()
            if not admin:
                return None
            
            # Обновляем поля
            for key, value in data.items():
                if hasattr(admin, key):
                    setattr(admin, key, value)
            
            # Обновляем роль, если указана
            if role:
                admin.role = role
            
            # Если указан новый пароль, меняем его
            if new_password:
                admin.set_password(new_password)
            
            session.commit()
            session.refresh(admin)
            return admin
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def is_accessible(self, request: Request) -> bool:
        """Доступ только для admin"""
        return request.session.get("admin_role") == "admin"


class UserActivityAdmin(ModelView, model=UserActivity):
    """Админка для логов активности пользователей"""
    
    name = "Активность"
    name_plural = "Логи активности пользователей"
    icon = "fa-solid fa-chart-line"
    
    # Только чтение
    can_create = False
    can_edit = False
    can_delete = False
    
    column_list = [
        UserActivity.id,
        UserActivity.telegram_id,
        UserActivity.username,
        UserActivity.action,
        UserActivity.details,
        UserActivity.timestamp
    ]
    
    column_searchable_list = [UserActivity.telegram_id, UserActivity.username, UserActivity.action]
    column_filters = [UserActivity.action, UserActivity.timestamp]
    column_default_sort = [(UserActivity.timestamp, True)]
    
    column_labels = {
        UserActivity.id: 'ID',
        UserActivity.telegram_id: 'Telegram ID',
        UserActivity.username: 'Username',
        UserActivity.action: 'Действие',
        UserActivity.details: 'Детали',
        UserActivity.timestamp: 'Время'
    }
    
    def is_accessible(self, request: Request) -> bool:
        """Проверка доступа"""
        return request.session.get("admin_role") in ["admin", "manager"]


class AdminAuthentication(AuthenticationBackend):
    """Бэкенд аутентификации для админ-панели"""
    
    async def login(self, request: Request) -> bool:
        """Обработка логина"""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        if not username or not password:
            return False
        
        session = get_session()
        try:
            admin = session.query(AdminModel).filter_by(
                username=username,
                is_active=True
            ).first()
            
            if admin and admin.check_password(password):
                # Обновляем время последнего входа
                admin.last_login = datetime.utcnow()
                session.commit()
                
                # Сохраняем в сессии ID, username и роль
                request.session.update({
                    "admin_id": admin.id,
                    "username": admin.username,
                    "admin_role": admin.role
                })
                return True
            
            return False
        finally:
            session.close()
    
    async def logout(self, request: Request) -> bool:
        """Обработка выхода"""
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        """Проверка аутентификации"""
        admin_id = request.session.get("admin_id")
        
        if not admin_id:
            return False
        
        session = get_session()
        try:
            admin = session.query(AdminModel).filter_by(
                id=admin_id,
                is_active=True
            ).first()
            
            # Обновляем роль в сессии на случай если она изменилась
            if admin:
                request.session["admin_role"] = admin.role
            
            return admin is not None
        finally:
            session.close()


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
                        margin: 10px;
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
                    <a href="/metrics">📊 Метрики</a>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(html)
    
    async def metrics_page(request):
        """Страница с метриками и статистикой"""
        # Проверяем аутентификацию
        if not request.session.get("admin_id"):
            return Response("Unauthorized", status_code=401)
        
        # Собираем метрики
        total_users = metrics_service.get_total_users()
        active_7d = metrics_service.get_active_users(7)
        active_30d = metrics_service.get_active_users(30)
        new_7d = metrics_service.get_new_users(7)
        new_30d = metrics_service.get_new_users(30)
        subscribers = metrics_service.get_subscribers_count()
        interactions_7d = metrics_service.get_total_interactions(7)
        interactions_30d = metrics_service.get_total_interactions(30)
        retention_7d = metrics_service.get_retention_rate(7)
        retention_30d = metrics_service.get_retention_rate(30)
        top_actions = metrics_service.get_top_actions(7, 10)
        
        # HTML страницы
        actions_html = "".join([
            f"<tr><td>{action}</td><td>{count}</td></tr>"
            for action, count in top_actions
        ])
        
        html = f"""
        <html>
            <head>
                <title>Метрики бота</title>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        margin: 0;
                        padding: 20px;
                        background: #f5f5f5;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 10px;
                        margin-bottom: 30px;
                    }}
                    .metrics-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        margin-bottom: 30px;
                    }}
                    .metric-card {{
                        background: white;
                        padding: 25px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .metric-value {{
                        font-size: 36px;
                        font-weight: bold;
                        color: #667eea;
                        margin: 10px 0;
                    }}
                    .metric-label {{
                        color: #666;
                        font-size: 14px;
                    }}
                    .actions-table {{
                        background: white;
                        padding: 25px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        padding: 12px;
                        text-align: left;
                        border-bottom: 1px solid #eee;
                    }}
                    th {{
                        background: #f8f9fa;
                        font-weight: 600;
                    }}
                    .back-link {{
                        display: inline-block;
                        padding: 10px 20px;
                        background: white;
                        color: #667eea;
                        text-decoration: none;
                        border-radius: 5px;
                        margin-top: 20px;
                    }}
                    .back-link:hover {{
                        background: #f0f0f0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 Метрики бота хоккейной лиги</h1>
                    <p>Статистика использования и активности пользователей</p>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">👥 Всего пользователей</div>
                        <div class="metric-value">{total_users}</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">🔔 Подписчиков на уведомления</div>
                        <div class="metric-value">{subscribers}</div>
                        <div class="metric-label">{round(subscribers/total_users*100 if total_users > 0 else 0, 1)}% от общего числа</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">📈 Активных за 7 дней</div>
                        <div class="metric-value">{active_7d}</div>
                        <div class="metric-label">{round(active_7d/total_users*100 if total_users > 0 else 0, 1)}% от общего числа</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">📈 Активных за 30 дней</div>
                        <div class="metric-value">{active_30d}</div>
                        <div class="metric-label">{round(active_30d/total_users*100 if total_users > 0 else 0, 1)}% от общего числа</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">🆕 Новых за 7 дней</div>
                        <div class="metric-value">{new_7d}</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">🆕 Новых за 30 дней</div>
                        <div class="metric-value">{new_30d}</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">💬 Взаимодействий за 7 дней</div>
                        <div class="metric-value">{interactions_7d}</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">💬 Взаимодействий за 30 дней</div>
                        <div class="metric-value">{interactions_30d}</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">🔄 Retention Rate (7д)</div>
                        <div class="metric-value">{round(retention_7d, 1)}%</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-label">🔄 Retention Rate (30д)</div>
                        <div class="metric-value">{round(retention_30d, 1)}%</div>
                    </div>
                </div>
                
                <div class="actions-table">
                    <h2>🎯 Топ действий за последние 7 дней</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Действие</th>
                                <th>Количество</th>
                            </tr>
                        </thead>
                        <tbody>
                            {actions_html}
                        </tbody>
                    </table>
                </div>
                
                <a href="/admin" class="back-link">← Вернуться в админ-панель</a>
            </body>
        </html>
        """
        return HTMLResponse(html)
    
    # Middleware для сессий
    middleware = [
        Middleware(SessionMiddleware, secret_key=config.ADMIN_SECRET_KEY)
    ]
    
    app = Starlette(
        routes=[
            Route('/', homepage),
            Route('/metrics', metrics_page),
        ],
        middleware=middleware
    )
    
    # Создание бэкенда аутентификации
    authentication_backend = AdminAuthentication(secret_key=config.ADMIN_SECRET_KEY)
    
    # Создание админ-панели с аутентификацией
    admin = Admin(
        app,
        engine,
        title="Админ-панель хоккейной лиги",
        base_url='/admin',
        authentication_backend=authentication_backend
    )
    
    # Регистрация моделей
    admin.add_view(UserAdmin)
    admin.add_view(TeamApplicationAdmin)
    admin.add_view(PlayerAdmin)
    admin.add_view(GameNotificationAdmin)
    admin.add_view(UserActivityAdmin)  # Добавляем логи активности
    admin.add_view(AdminUserAdmin)
    
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
