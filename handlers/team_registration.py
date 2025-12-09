"""
Обработчик регистрации команд в лигу
"""
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardRemove
from database import get_session, TeamApplication
from keyboards.reply_keyboards import get_back_to_menu, get_team_management_menu, get_confirmation_keyboard
from utils.metrics import metrics_service


# Хранилище состояний регистрации и редактирования команд
team_registration_state = {}
team_edit_state = {}


def register_team_handlers(bot: TeleBot):
    """Регистрация обработчиков для команд"""
    
    @bot.message_handler(func=lambda message: message.text == "👥 Записать команду в лигу")
    def start_team_registration(message: Message):
        """Начало регистрации команды"""
        user_id = message.from_user.id
        
        # Логируем активность
        metrics_service.track_message(message, 'team_registration_start')
        
        # Проверка существующих заявок
        session = get_session()
        try:
            existing_apps = session.query(TeamApplication).filter_by(telegram_id=user_id).all()
            
            if existing_apps:
                # Показываем меню управления заявками
                apps_info = "\n\n".join([
                    f"📋 Заявка #{i+1}:\n"
                    f"Команда: {app.team_name}\n"
                    f"Капитан: {app.captain_name}\n"
                    f"Статус: {'✅ Одобрена' if app.status == 'approved' else '⏳ На рассмотрении' if app.status == 'pending' else '❌ Отклонена'}"
                    for i, app in enumerate(existing_apps)
                ])
                
                bot.send_message(
                    message.chat.id,
                    f"У вас уже есть заявки:\n\n{apps_info}\n\n"
                    "Выберите действие:",
                    reply_markup=get_team_management_menu()
                )
            else:
                # Первая регистрация - сразу начинаем процесс
                start_new_team_registration(bot, message)
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text == "➕ Добавить команду")
    def handle_add_team(message: Message):
        """Добавление новой команды"""
        start_new_team_registration(bot, message)
    
    @bot.message_handler(func=lambda message: message.text == "📋 Мои заявки")
    def handle_view_teams(message: Message):
        """Просмотр всех заявок пользователя"""
        user_id = message.from_user.id
        session = get_session()
        
        try:
            apps = session.query(TeamApplication).filter_by(telegram_id=user_id).all()
            
            if not apps:
                bot.send_message(
                    message.chat.id,
                    "У вас пока нет заявок на регистрацию команд.",
                    reply_markup=get_back_to_menu()
                )
                return
            
            apps_info = "\n\n".join([
                f"📋 Заявка #{i+1}:\n"
                f"Команда: {app.team_name}\n"
                f"Капитан: {app.captain_name}\n"
                f"Телефон: {app.captain_phone}\n"
                f"Город: {app.city or 'не указан'}\n"
                f"Статус: {'✅ Одобрена' if app.status == 'approved' else '⏳ На рассмотрении' if app.status == 'pending' else '❌ Отклонена'}"
                + (f"\nКомментарий админа: {app.admin_comment}" if app.admin_comment else "")
                for i, app in enumerate(apps)
            ])
            
            bot.send_message(
                message.chat.id,
                f"Ваши заявки:\n\n{apps_info}",
                reply_markup=get_team_management_menu()
            )
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text == "✏️ Изменить заявку")
    def handle_edit_team_start(message: Message):
        """Начало процесса редактирования заявки"""
        user_id = message.from_user.id
        session = get_session()
        
        try:
            apps = session.query(TeamApplication).filter_by(telegram_id=user_id).all()
            
            if not apps:
                bot.send_message(
                    message.chat.id,
                    "У вас нет заявок для редактирования.",
                    reply_markup=get_back_to_menu()
                )
                return
            
            if len(apps) == 1:
                # Одна заявка - сразу редактируем
                start_edit_team(bot, message, apps[0].id)
            else:
                # Несколько заявок - предлагаем выбрать
                team_edit_state[user_id] = {'step': 'select_team_to_edit', 'teams': [a.id for a in apps]}
                
                teams_list = "\n".join([
                    f"{i+1}. {app.team_name} ({app.captain_name})"
                    for i, app in enumerate(apps)
                ])
                
                bot.send_message(
                    message.chat.id,
                    f"Выберите заявку для редактирования (введите номер):\n\n{teams_list}",
                    reply_markup=get_back_to_menu()
                )
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text == "🗑 Удалить заявку")
    def handle_delete_team_start(message: Message):
        """Начало процесса удаления заявки"""
        user_id = message.from_user.id
        session = get_session()
        
        try:
            apps = session.query(TeamApplication).filter_by(telegram_id=user_id).all()
            
            if not apps:
                bot.send_message(
                    message.chat.id,
                    "У вас нет заявок для удаления.",
                    reply_markup=get_back_to_menu()
                )
                return
            
            if len(apps) == 1:
                # Одна заявка - сразу запрашиваем подтверждение
                team_edit_state[user_id] = {'step': 'confirm_delete', 'team_id': apps[0].id}
                bot.send_message(
                    message.chat.id,
                    f"Удалить заявку команды '{apps[0].team_name}'?",
                    reply_markup=get_confirmation_keyboard()
                )
            else:
                # Несколько заявок - предлагаем выбрать
                team_edit_state[user_id] = {'step': 'select_team_to_delete', 'teams': [a.id for a in apps]}
                
                teams_list = "\n".join([
                    f"{i+1}. {app.team_name} ({app.captain_name})"
                    for i, app in enumerate(apps)
                ])
                
                bot.send_message(
                    message.chat.id,
                    f"Выберите заявку для удаления (введите номер):\n\n{teams_list}",
                    reply_markup=get_back_to_menu()
                )
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text in ["✅ Подтвердить", "❌ Отменить"])
    def handle_confirmation(message: Message):
        """Обработка подтверждения/отмены"""
        user_id = message.from_user.id
        
        if user_id not in team_edit_state:
            return
        
        state = team_edit_state[user_id]
        
        if state.get('step') == 'confirm_delete':
            if message.text == "✅ Подтвердить":
                session = get_session()
                try:
                    app = session.query(TeamApplication).filter_by(id=state['team_id']).first()
                    if app:
                        team_name = app.team_name
                        session.delete(app)
                        session.commit()
                        bot.send_message(
                            message.chat.id,
                            f"✅ Заявка команды '{team_name}' удалена.",
                            reply_markup=get_back_to_menu()
                        )
                    else:
                        bot.send_message(
                            message.chat.id,
                            "❌ Заявка не найдена.",
                            reply_markup=get_back_to_menu()
                        )
                finally:
                    session.close()
            else:
                bot.send_message(
                    message.chat.id,
                    "Удаление отменено.",
                    reply_markup=get_team_management_menu()
                )
            
            del team_edit_state[user_id]
    
    @bot.message_handler(func=lambda message: message.from_user.id in team_registration_state)
    def team_registration_process(message: Message):
        """Процесс регистрации команды"""
        user_id = message.from_user.id
        state = team_registration_state[user_id]
        
        if message.text == "🏠 Главное меню" or message.text == "/cancel":
            del team_registration_state[user_id]
            bot.send_message(
                message.chat.id,
                "❌ Регистрация отменена.",
                reply_markup=get_back_to_menu()
            )
            return
        
        if state['step'] == 'team_name':
            state['team_name'] = message.text
            state['step'] = 'captain_name'
            bot.send_message(
                message.chat.id,
                "Введите ФИО капитана команды:"
            )
        
        elif state['step'] == 'captain_name':
            state['captain_name'] = message.text
            state['step'] = 'captain_phone'
            bot.send_message(
                message.chat.id,
                "Введите номер телефона капитана для связи:"
            )
        
        elif state['step'] == 'captain_phone':
            state['captain_phone'] = message.text
            state['step'] = 'city'
            bot.send_message(
                message.chat.id,
                "Введите город команды (или пропустите - /skip):"
            )
        
        elif state['step'] == 'city':
            if message.text != '/skip':
                state['city'] = message.text
            else:
                state['city'] = None
            state['step'] = 'description'
            bot.send_message(
                message.chat.id,
                "Введите краткое описание команды:\n - Уровень команды\n - Где играли предыдущий сезон\n\n (или пропустите - /skip):"
            )
        
        elif state['step'] == 'description':
            if message.text != '/skip':
                state['description'] = message.text
            else:
                state['description'] = None
            
            # Сохранение заявки в БД
            session = get_session()
            try:
                application = TeamApplication(
                    telegram_id=user_id,
                    team_name=state['team_name'],
                    captain_name=state['captain_name'],
                    captain_phone=state['captain_phone'],
                    city=state.get('city'),
                    description=state.get('description'),
                    status='pending'
                )
                session.add(application)
                session.commit()
                
                bot.send_message(
                    message.chat.id,
                    "✅ Заявка успешно подана!\n\n"
                    f"Команда: {state['team_name']}\n"
                    f"Капитан: {state['captain_name']}\n"
                    f"Телефон: {state['captain_phone']}\n"
                    f"Город: {state.get('city', 'не указан')}\n\n"
                    "Статус: ⏳ Ожидает рассмотрения\n\n"
                    "Администратор рассмотрит заявку и свяжется с вами в ближайшее время.",
                    reply_markup=get_team_management_menu()
                )
            except Exception as e:
                session.rollback()
                bot.send_message(
                    message.chat.id,
                    f"❌ Ошибка при подаче заявки: {e}",
                    reply_markup=get_back_to_menu()
                )
            finally:
                session.close()
                del team_registration_state[user_id]
    
    @bot.message_handler(func=lambda message: message.from_user.id in team_edit_state)
    def handle_team_edit_steps(message: Message):
        """Обработка шагов редактирования/удаления заявки"""
        user_id = message.from_user.id
        state = team_edit_state[user_id]
        
        if message.text == "🏠 Главное меню":
            del team_edit_state[user_id]
            bot.send_message(message.chat.id, "Действие отменено.", reply_markup=get_back_to_menu())
            return
        
        # Выбор заявки для редактирования
        if state.get('step') == 'select_team_to_edit':
            try:
                choice = int(message.text)
                if 1 <= choice <= len(state['teams']):
                    team_id = state['teams'][choice - 1]
                    start_edit_team(bot, message, team_id)
                else:
                    bot.send_message(message.chat.id, "❌ Неверный номер. Попробуйте снова.")
            except ValueError:
                bot.send_message(message.chat.id, "❌ Введите номер заявки.")
        
        # Выбор заявки для удаления
        elif state.get('step') == 'select_team_to_delete':
            try:
                choice = int(message.text)
                if 1 <= choice <= len(state['teams']):
                    team_id = state['teams'][choice - 1]
                    session = get_session()
                    try:
                        app = session.query(TeamApplication).filter_by(id=team_id).first()
                        if app:
                            team_edit_state[user_id] = {'step': 'confirm_delete', 'team_id': team_id}
                            bot.send_message(
                                message.chat.id,
                                f"Удалить заявку команды '{app.team_name}'?",
                                reply_markup=get_confirmation_keyboard()
                            )
                        else:
                            bot.send_message(message.chat.id, "❌ Заявка не найдена.", reply_markup=get_team_management_menu())
                            del team_edit_state[user_id]
                    finally:
                        session.close()
                else:
                    bot.send_message(message.chat.id, "❌ Неверный номер. Попробуйте снова.")
            except ValueError:
                bot.send_message(message.chat.id, "❌ Введите номер заявки.")
        
        # Редактирование - выбор поля
        elif state.get('step') == 'select_field':
            field_map = {
                '1': ('team_name', 'Введите новое название команды:'),
                '2': ('captain_name', 'Введите новое ФИО капитана:'),
                '3': ('captain_phone', 'Введите новый номер телефона:'),
                '4': ('city', 'Введите новый город (или /skip):'),
                '5': ('description', 'Введите новое описание (или /skip):')
            }
            
            if message.text in field_map:
                field, prompt = field_map[message.text]
                state['editing_field'] = field
                state['step'] = 'enter_new_value'
                bot.send_message(message.chat.id, prompt, reply_markup=get_back_to_menu())
            else:
                bot.send_message(message.chat.id, "❌ Выберите номер от 1 до 5.")
        
        # Редактирование - ввод нового значения
        elif state.get('step') == 'enter_new_value':
            session = get_session()
            try:
                app = session.query(TeamApplication).filter_by(id=state['team_id']).first()
                if app:
                    # Обработка /skip для необязательных полей
                    if message.text == '/skip' and state['editing_field'] in ['city', 'description']:
                        new_value = None
                    else:
                        new_value = message.text
                    
                    setattr(app, state['editing_field'], new_value)
                    session.commit()
                    
                    field_names = {
                        'team_name': 'Название команды',
                        'captain_name': 'ФИО капитана',
                        'captain_phone': 'Номер телефона',
                        'city': 'Город',
                        'description': 'Описание'
                    }
                    
                    bot.send_message(
                        message.chat.id,
                        f"✅ {field_names[state['editing_field']]} обновлено!",
                        reply_markup=get_team_management_menu()
                    )
                else:
                    bot.send_message(message.chat.id, "❌ Заявка не найдена.", reply_markup=get_team_management_menu())
            finally:
                session.close()
            
            del team_edit_state[user_id]


def start_new_team_registration(bot: TeleBot, message: Message):
    """Начало процесса регистрации новой команды"""
    user_id = message.from_user.id
    team_registration_state[user_id] = {'step': 'team_name'}
    
    bot.send_message(
        message.chat.id,
        "👥 Регистрация команды в лигу\n\n"
        "Введите название команды:\n\n"
        "Для отмены отправьте /cancel",
        reply_markup=ReplyKeyboardRemove()
    )


def start_edit_team(bot: TeleBot, message: Message, team_id: int):
    """Начало редактирования конкретной заявки"""
    user_id = message.from_user.id
    session = get_session()
    
    try:
        app = session.query(TeamApplication).filter_by(id=team_id).first()
        if not app:
            bot.send_message(message.chat.id, "❌ Заявка не найдена.", reply_markup=get_team_management_menu())
            return
        
        team_edit_state[user_id] = {'step': 'select_field', 'team_id': team_id}
        
        bot.send_message(
            message.chat.id,
            f"Текущие данные заявки:\n\n"
            f"1. Название команды: {app.team_name}\n"
            f"2. ФИО капитана: {app.captain_name}\n"
            f"3. Телефон: {app.captain_phone}\n"
            f"4. Город: {app.city or 'не указан'}\n"
            f"5. Описание: {app.description or 'не указано'}\n\n"
            "Введите номер поля для редактирования (1-5):",
            reply_markup=get_back_to_menu()
        )
    finally:
        session.close()
