"""
Обработчик регистрации игроков
"""
from telebot import TeleBot
from telebot.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from database import get_session, Player
from keyboards.reply_keyboards import get_back_to_menu, get_player_management_menu, get_confirmation_keyboard
from utils import api_service


# Хранилище состояний регистрации и редактирования игроков
player_registration_state = {}
player_edit_state = {}


def get_position_keyboard():
    """Клавиатура выбора позиции"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(
        KeyboardButton("Нападающий"),
        KeyboardButton("Защитник"),
        KeyboardButton("Вратарь")
    )
    keyboard.add(KeyboardButton("Пропустить"))
    return keyboard


def get_teams_keyboard():
    """Клавиатура выбора команды"""
    teams = api_service.get_teams()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    
    for team in teams:
        keyboard.add(KeyboardButton(team['name']))
    
    keyboard.add(KeyboardButton("Пропустить"))
    return keyboard


def register_player_handlers(bot: TeleBot):
    """Регистрация обработчиков для игроков"""
    
    @bot.message_handler(func=lambda message: message.text == "👤️ Записаться в команду (игрок)")
    def start_player_registration(message: Message):
        """Начало регистрации игрока"""
        user_id = message.from_user.id
        
        # Проверка существующих анкет
        session = get_session()
        try:
            existing_players = session.query(Player).filter_by(telegram_id=user_id).all()
            
            if existing_players:
                # Показываем меню управления анкетами
                players_info = "\n\n".join([
                    f"📋 Анкета #{i+1}:\n"
                    f"Имя: {player.full_name}\n"
                    f"Позиция: {player.position or 'не указана'}\n"
                    f"Телефон: {player.phone or 'не указан'}"
                    for i, player in enumerate(existing_players)
                ])
                
                bot.send_message(
                    message.chat.id,
                    f"У вас уже есть анкеты:\n\n{players_info}\n\n"
                    "Выберите действие:",
                    reply_markup=get_player_management_menu()
                )
            else:
                # Первая регистрация - сразу начинаем процесс
                start_new_player_registration(bot, message)
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text == "➕ Добавить анкету")
    def handle_add_player(message: Message):
        """Добавление новой анкеты"""
        start_new_player_registration(bot, message)
    
    @bot.message_handler(func=lambda message: message.text == "📋 Мои анкеты")
    def handle_view_players(message: Message):
        """Просмотр всех анкет пользователя"""
        user_id = message.from_user.id
        session = get_session()
        
        try:
            players = session.query(Player).filter_by(telegram_id=user_id).all()
            
            if not players:
                bot.send_message(
                    message.chat.id,
                    "У вас пока нет анкет игрока.",
                    reply_markup=get_back_to_menu()
                )
                return
            
            players_info = "\n\n".join([
                f"📋 Анкета #{i+1}:\n"
                f"Имя: {player.full_name}\n"
                f"Год рождения: {player.birth_year or 'не указан'}\n"
                f"Позиция: {player.position or 'не указана'}\n"
                f"Телефон: {player.phone or 'не указан'}\n"
                f"Опыт: {player.experience or 'не указан'}\n"
                + (f"Команда: {api_service.get_team_by_slug(player.preferred_team_slug)['name']}\n" if player.preferred_team_slug and api_service.get_team_by_slug(player.preferred_team_slug) else "")
                for i, player in enumerate(players)
            ])
            
            bot.send_message(
                message.chat.id,
                f"Ваши анкеты:\n\n{players_info}",
                reply_markup=get_player_management_menu()
            )
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text == "✏️ Изменить анкету")
    def handle_edit_player_start(message: Message):
        """Начало процесса редактирования анкеты"""
        user_id = message.from_user.id
        session = get_session()
        
        try:
            players = session.query(Player).filter_by(telegram_id=user_id).all()
            
            if not players:
                bot.send_message(
                    message.chat.id,
                    "У вас нет анкет для редактирования.",
                    reply_markup=get_back_to_menu()
                )
                return
            
            if len(players) == 1:
                # Одна анкета - сразу редактируем
                start_edit_player(bot, message, players[0].id)
            else:
                # Несколько анкет - предлагаем выбрать
                player_edit_state[user_id] = {'step': 'select_player_to_edit', 'players': [p.id for p in players]}
                
                players_list = "\n".join([
                    f"{i+1}. {player.full_name} ({player.position or 'без позиции'})"
                    for i, player in enumerate(players)
                ])
                
                bot.send_message(
                    message.chat.id,
                    f"Выберите анкету для редактирования (введите номер):\n\n{players_list}",
                    reply_markup=get_back_to_menu()
                )
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text == "🗑 Удалить анкету")
    def handle_delete_player_start(message: Message):
        """Начало процесса удаления анкеты"""
        user_id = message.from_user.id
        session = get_session()
        
        try:
            players = session.query(Player).filter_by(telegram_id=user_id).all()
            
            if not players:
                bot.send_message(
                    message.chat.id,
                    "У вас нет анкет для удаления.",
                    reply_markup=get_back_to_menu()
                )
                return
            
            if len(players) == 1:
                # Одна анкета - сразу запрашиваем подтверждение
                player_edit_state[user_id] = {'step': 'confirm_delete', 'player_id': players[0].id}
                bot.send_message(
                    message.chat.id,
                    f"Удалить анкету игрока '{players[0].full_name}'?",
                    reply_markup=get_confirmation_keyboard()
                )
            else:
                # Несколько анкет - предлагаем выбрать
                player_edit_state[user_id] = {'step': 'select_player_to_delete', 'players': [p.id for p in players]}
                
                players_list = "\n".join([
                    f"{i+1}. {player.full_name} ({player.position or 'без позиции'})"
                    for i, player in enumerate(players)
                ])
                
                bot.send_message(
                    message.chat.id,
                    f"Выберите анкету для удаления (введите номер):\n\n{players_list}",
                    reply_markup=get_back_to_menu()
                )
        finally:
            session.close()
    
    @bot.message_handler(func=lambda message: message.text in ["✅ Подтвердить", "❌ Отменить"] and message.from_user.id in player_edit_state)
    def handle_player_confirmation(message: Message):
        """Обработка подтверждения/отмены для игроков"""
        user_id = message.from_user.id
        state = player_edit_state[user_id]
        
        if state.get('step') == 'confirm_delete':
            if message.text == "✅ Подтвердить":
                session = get_session()
                try:
                    player = session.query(Player).filter_by(id=state['player_id']).first()
                    if player:
                        player_name = player.full_name
                        session.delete(player)
                        session.commit()
                        bot.send_message(
                            message.chat.id,
                            f"✅ Анкета игрока '{player_name}' удалена.",
                            reply_markup=get_back_to_menu()
                        )
                    else:
                        bot.send_message(
                            message.chat.id,
                            "❌ Анкета не найдена.",
                            reply_markup=get_back_to_menu()
                        )
                finally:
                    session.close()
            else:
                bot.send_message(
                    message.chat.id,
                    "Удаление отменено.",
                    reply_markup=get_player_management_menu()
                )
            
            del player_edit_state[user_id]
    
    @bot.message_handler(func=lambda message: message.from_user.id in player_registration_state)
    def player_registration_process(message: Message):
        """Процесс регистрации игрока"""
        user_id = message.from_user.id
        state = player_registration_state[user_id]
        
        if message.text == "🏠 Главное меню" or message.text == "/cancel":
            del player_registration_state[user_id]
            bot.send_message(
                message.chat.id,
                "❌ Регистрация отменена.",
                reply_markup=get_back_to_menu()
            )
            return
        
        if state['step'] == 'full_name':
            state['full_name'] = message.text
            state['step'] = 'birth_year'
            bot.send_message(
                message.chat.id,
                "Введите год рождения (или пропустите - /skip):"
            )
        
        elif state['step'] == 'birth_year':
            if message.text != '/skip':
                try:
                    birth_year = int(message.text)
                    if 1950 <= birth_year <= 2015:
                        state['birth_year'] = birth_year
                    else:
                        bot.send_message(
                            message.chat.id,
                            "⚠️ Некорректный год. Введите год от 1950 до 2015:"
                        )
                        return
                except ValueError:
                    bot.send_message(
                        message.chat.id,
                        "⚠️ Введите корректный год (число):"
                    )
                    return
            else:
                state['birth_year'] = None
            
            state['step'] = 'position'
            bot.send_message(
                message.chat.id,
                "Выберите позицию:",
                reply_markup=get_position_keyboard()
            )
        
        elif state['step'] == 'position':
            position_map = {
                'Нападающий': 'forward',
                'Защитник': 'defender',
                'Вратарь': 'goalie',
                'Пропустить': None
            }
            
            if message.text in position_map:
                state['position'] = position_map[message.text]
                state['step'] = 'experience'
                bot.send_message(
                    message.chat.id,
                    "Расскажите о своём опыте игры (или пропустите - /skip):",
                    reply_markup=ReplyKeyboardRemove()
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Выберите позицию из предложенных вариантов:",
                    reply_markup=get_position_keyboard()
                )
        
        elif state['step'] == 'experience':
            if message.text != '/skip':
                state['experience'] = message.text
            else:
                state['experience'] = None
            
            state['step'] = 'phone'
            bot.send_message(
                message.chat.id,
                "Введите номер телефона для связи (или пропустите - /skip):"
            )
        
        elif state['step'] == 'phone':
            if message.text != '/skip':
                state['phone'] = message.text
            else:
                state['phone'] = None
            
            state['step'] = 'team'
            bot.send_message(
                message.chat.id,
                "Выберите команду, в которую хотите попасть (или пропустите):",
                reply_markup=get_teams_keyboard()
            )
        
        elif state['step'] == 'team':
            if message.text != 'Пропустить':
                # Найти slug команды по названию
                teams = api_service.get_teams()
                team_slug = None
                for team in teams:
                    if team['name'] == message.text:
                        team_slug = team['slug']
                        break
                state['preferred_team_slug'] = team_slug
            else:
                state['preferred_team_slug'] = None
            
            # Сохранение игрока в БД
            session = get_session()
            try:
                player = Player(
                    telegram_id=user_id,
                    username=message.from_user.username,
                    full_name=state['full_name'],
                    birth_year=state.get('birth_year'),
                    position=state.get('position'),
                    experience=state.get('experience'),
                    phone=state.get('phone'),
                    preferred_team_slug=state.get('preferred_team_slug')
                )
                session.add(player)
                session.commit()
                
                position_text = {
                    'forward': 'Нападающий',
                    'defender': 'Защитник',
                    'goalie': 'Вратарь'
                }.get(state.get('position'), 'не указана')
                
                team_text = ""
                if state.get('preferred_team_slug'):
                    team = api_service.get_team_by_slug(state['preferred_team_slug'])
                    if team:
                        team_text = f"\nПредпочитаемая команда: {team['name']}"
                
                bot.send_message(
                    message.chat.id,
                    "✅ Вы успешно зарегистрированы как игрок!\n\n"
                    f"Имя: {state['full_name']}\n"
                    f"Год рождения: {state.get('birth_year', 'не указан')}\n"
                    f"Позиция: {position_text}\n"
                    f"Телефон: {state.get('phone', 'не указан')}"
                    f"{team_text}\n\n"
                    "Ваша анкета отправлена администраторам.",
                    reply_markup=get_player_management_menu()
                )
            except Exception as e:
                session.rollback()
                bot.send_message(
                    message.chat.id,
                    f"❌ Ошибка при регистрации: {e}",
                    reply_markup=get_back_to_menu()
                )
            finally:
                session.close()
                del player_registration_state[user_id]
    
    @bot.message_handler(func=lambda message: message.from_user.id in player_edit_state)
    def handle_player_edit_steps(message: Message):
        """Обработка шагов редактирования/удаления анкеты"""
        user_id = message.from_user.id
        state = player_edit_state[user_id]
        
        if message.text == "🏠 Главное меню":
            del player_edit_state[user_id]
            bot.send_message(message.chat.id, "Действие отменено.", reply_markup=get_back_to_menu())
            return
        
        # Выбор анкеты для редактирования
        if state.get('step') == 'select_player_to_edit':
            try:
                choice = int(message.text)
                if 1 <= choice <= len(state['players']):
                    player_id = state['players'][choice - 1]
                    start_edit_player(bot, message, player_id)
                else:
                    bot.send_message(message.chat.id, "❌ Неверный номер. Попробуйте снова.")
            except ValueError:
                bot.send_message(message.chat.id, "❌ Введите номер анкеты.")
        
        # Выбор анкеты для удаления
        elif state.get('step') == 'select_player_to_delete':
            try:
                choice = int(message.text)
                if 1 <= choice <= len(state['players']):
                    player_id = state['players'][choice - 1]
                    session = get_session()
                    try:
                        player = session.query(Player).filter_by(id=player_id).first()
                        if player:
                            player_edit_state[user_id] = {'step': 'confirm_delete', 'player_id': player_id}
                            bot.send_message(
                                message.chat.id,
                                f"Удалить анкету игрока '{player.full_name}'?",
                                reply_markup=get_confirmation_keyboard()
                            )
                        else:
                            bot.send_message(message.chat.id, "❌ Анкета не найдена.", reply_markup=get_player_management_menu())
                            del player_edit_state[user_id]
                    finally:
                        session.close()
                else:
                    bot.send_message(message.chat.id, "❌ Неверный номер. Попробуйте снова.")
            except ValueError:
                bot.send_message(message.chat.id, "❌ Введите номер анкеты.")
        
        # Редактирование - выбор поля
        elif state.get('step') == 'select_field':
            field_map = {
                '1': ('full_name', 'Введите новое полное имя:'),
                '2': ('birth_year', 'Введите новый год рождения (или /skip):'),
                '3': ('position', 'Выберите новую позицию:', get_position_keyboard()),
                '4': ('experience', 'Введите новый опыт (или /skip):'),
                '5': ('phone', 'Введите новый номер телефона (или /skip):'),
                '6': ('preferred_team_slug', 'Выберите новую команду:', get_teams_keyboard())
            }
            
            if message.text in field_map:
                field_info = field_map[message.text]
                field = field_info[0]
                prompt = field_info[1]
                state['editing_field'] = field
                state['step'] = 'enter_new_value'
                
                keyboard = field_info[2] if len(field_info) > 2 else get_back_to_menu()
                bot.send_message(message.chat.id, prompt, reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, "❌ Выберите номер от 1 до 6.")
        
        # Редактирование - ввод нового значения
        elif state.get('step') == 'enter_new_value':
            session = get_session()
            try:
                player = session.query(Player).filter_by(id=state['player_id']).first()
                if player:
                    # Обработка различных полей
                    if state['editing_field'] == 'birth_year':
                        if message.text == '/skip':
                            new_value = None
                        else:
                            try:
                                new_value = int(message.text)
                                if not (1950 <= new_value <= 2015):
                                    bot.send_message(message.chat.id, "⚠️ Год должен быть от 1950 до 2015.")
                                    return
                            except ValueError:
                                bot.send_message(message.chat.id, "⚠️ Введите корректный год.")
                                return
                    
                    elif state['editing_field'] == 'position':
                        position_map = {
                            'Нападающий': 'forward',
                            'Защитник': 'defender',
                            'Вратарь': 'goalie',
                            'Пропустить': None
                        }
                        new_value = position_map.get(message.text)
                        if message.text not in position_map:
                            bot.send_message(message.chat.id, "⚠️ Выберите позицию из предложенных.", reply_markup=get_position_keyboard())
                            return
                    
                    elif state['editing_field'] == 'preferred_team_slug':
                        if message.text == 'Пропустить':
                            new_value = None
                        else:
                            teams = api_service.get_teams()
                            new_value = None
                            for team in teams:
                                if team['name'] == message.text:
                                    new_value = team['slug']
                                    break
                            if not new_value:
                                bot.send_message(message.chat.id, "⚠️ Команда не найдена.", reply_markup=get_teams_keyboard())
                                return
                    
                    else:
                        # Текстовые поля
                        if message.text == '/skip' and state['editing_field'] in ['experience', 'phone']:
                            new_value = None
                        else:
                            new_value = message.text
                    
                    setattr(player, state['editing_field'], new_value)
                    session.commit()
                    
                    field_names = {
                        'full_name': 'Полное имя',
                        'birth_year': 'Год рождения',
                        'position': 'Позиция',
                        'experience': 'Опыт',
                        'phone': 'Номер телефона',
                        'preferred_team_slug': 'Предпочитаемая команда'
                    }
                    
                    bot.send_message(
                        message.chat.id,
                        f"✅ {field_names[state['editing_field']]} обновлено!",
                        reply_markup=get_player_management_menu()
                    )
                else:
                    bot.send_message(message.chat.id, "❌ Анкета не найдена.", reply_markup=get_player_management_menu())
            finally:
                session.close()
            
            del player_edit_state[user_id]


def start_new_player_registration(bot: TeleBot, message: Message):
    """Начало процесса регистрации нового игрока"""
    user_id = message.from_user.id
    player_registration_state[user_id] = {'step': 'full_name'}
    
    bot.send_message(
        message.chat.id,
        "👤️ Регистрация игрока\n\n"
        "Введите ваше полное имя (ФИО):",
        reply_markup=ReplyKeyboardRemove()
    )


def start_edit_player(bot: TeleBot, message: Message, player_id: int):
    """Начало редактирования конкретной анкеты"""
    user_id = message.from_user.id
    session = get_session()
    
    try:
        player = session.query(Player).filter_by(id=player_id).first()
        if not player:
            bot.send_message(message.chat.id, "❌ Анкета не найдена.", reply_markup=get_player_management_menu())
            return
        
        player_edit_state[user_id] = {'step': 'select_field', 'player_id': player_id}
        
        team_text = "не указана"
        if player.preferred_team_slug:
            team = api_service.get_team_by_slug(player.preferred_team_slug)
            if team:
                team_text = team['name']
        
        bot.send_message(
            message.chat.id,
            f"Текущие данные анкеты:\n\n"
            f"1. Полное имя: {player.full_name}\n"
            f"2. Год рождения: {player.birth_year or 'не указан'}\n"
            f"3. Позиция: {player.position or 'не указана'}\n"
            f"4. Опыт: {player.experience or 'не указан'}\n"
            f"5. Телефон: {player.phone or 'не указан'}\n"
            f"6. Команда: {team_text}\n\n"
            "Введите номер поля для редактирования (1-6):",
            reply_markup=get_back_to_menu()
        )
    finally:
        session.close()
