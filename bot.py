import telebot
import requests
import datetime as dt
from apscheduler.schedulers.background import BackgroundScheduler

from config import BOT_TOKEN, API_GAMES, API_TEAMS
from database import (
    init_db, add_subscriber, remove_subscriber,
    get_subscribers, set_last_notified, get_last_notified
)

bot = telebot.TeleBot(BOT_TOKEN)

teams_cache = {}

def load_teams():
    global teams_cache
    try:
        r = requests.get(API_TEAMS, timeout=10)
        r.raise_for_status()
        teams = r.json()
        teams_cache = {team["id"]: team for team in teams}
        print(f"Команды загружены: {len(teams_cache)} шт.")
    except Exception as e:
        print("Ошибка загрузки команд:", e)

def get_team_name(team_id: int) -> str:
    team = teams_cache.get(team_id)
    return team["name"] if team else f"Команда {team_id}"

def time_until(game_dt: dt.datetime) -> str:
    delta = game_dt - dt.datetime.now()
    if delta.total_seconds() < 0:
        return "Матч уже прошёл"

    total_seconds = int(delta.total_seconds())
    days = total_seconds // (24 * 3600)
    hours = (total_seconds % (24 * 3600)) // 3600
    minutes = (total_seconds % 3600) // 60

    parts = []
    if days > 0:
        if days == 1:
            parts.append("1 день")
        elif 2 <= days <= 4:
            parts.append(f"{days} дня")
        else:
            parts.append(f"{days} дней")

    if hours > 0:
        parts.append(f"{hours} ч.")
    if minutes > 0 and days == 0:
        parts.append(f"{minutes} мин.")

    return "Начало через " + " ".join(parts) if parts else "прямо сейчас!"

def format_game(game: dict, is_upcoming=True) -> tuple[str, telebot.types.InlineKeyboardMarkup | None]:
    date = dt.datetime.strptime(game["date"], "%Y-%m-%d").strftime("%d.%m.%Y")
    time = game["time"][:5]
    team_a = get_team_name(game["team_a_id"])
    team_b = get_team_name(game["team_b_id"])
    location = game["location"]

    game_dt = dt.datetime.strptime(f"{game['date']} {game['time']}", "%Y-%m-%d %H:%M:%S")

    header = "Ближайший матч" if is_upcoming else "Последний матч"
    timer = time_until(game_dt) if is_upcoming else "Сыгран"

    score = ""
    if game["score_team_a"] is not None and game["score_team_b"] is not None:
        score = f"\n📊 Счёт: {game['score_team_a']} : {game['score_team_b']}"

    text = (
        f"🏒 {header} 🥅\n\n"
        f"{team_a} 🆚 {team_b}\n\n"
        f"📅 Дата: {date}\n"
        f"🕗 Время: {time}\n"
        f"📍 Место: {location}{score}\n\n"
        f"⏰ {timer}"
    )

    keyboard = None
    if game.get("video_url"):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                text="Смотреть запись трансляции" if not is_upcoming else "Смотреть трансляцию",
                url=game["video_url"]
            )
        )

    return text, keyboard

def get_next_game() -> dict | None:
    try:
        r = requests.get(API_GAMES, timeout=10)
        r.raise_for_status()
        games = r.json()
        now = dt.datetime.now()
        future = [g for g in games if dt.datetime.strptime(f"{g['date']} {g['time']}", "%Y-%m-%d %H:%M:%S") > now]
        if not future: return None
        future.sort(key=lambda x: f"{x['date']} {x['time']}")
        return future[0]
    except Exception as e:
        print(e)
        return None

def get_last_game() -> dict | None:
    try:
        r = requests.get(API_GAMES, timeout=10)
        r.raise_for_status()
        games = r.json()
        now = dt.datetime.now()
        finished = [
            g for g in games
            if g["score_team_a"] is not None
            and g["score_team_b"] is not None
            and dt.datetime.strptime(f"{g['date']} {g['time']}", "%Y-%m-%d %H:%M:%S") <= now
        ]
        if not finished: return None
        finished.sort(key=lambda x: f"{x['date']} {x['time']}", reverse=True)
        return finished[0]
    except Exception as e:
        print(e)
        return None

def notify_about_upcoming():
    game = get_next_game()
    if not game or get_last_notified() == game["id"]:
        return
    game_dt = dt.datetime.strptime(f"{game['date']} {game['time']}", "%Y-%m-%d %H:%M:%S")
    if (game_dt - dt.datetime.now()).total_seconds() > 7200:
        return

    text, kb = format_game(game, is_upcoming=True)
    for uid in get_subscribers():
        try:
            bot.send_message(uid, text, reply_markup=kb, disable_web_page_preview=True)
        except:
            pass
    set_last_notified(game["id"])

def show_game(message, game_func, fallback):
    game = game_func()
    if not game:
        bot.send_message(message.chat.id, fallback)
        return

    text, stream_kb = format_game(game, is_upcoming=(game_func == get_next_game))
    user_id = message.from_user.id

    final_kb = stream_kb

    if game_func == get_next_game and user_id not in get_subscribers():
        final_kb = telebot.types.InlineKeyboardMarkup()
        final_kb.add(telebot.types.InlineKeyboardButton("Подписаться на напоминания", callback_data="subscribe"))
        if stream_kb:
            final_kb.add(*stream_kb.keyboard[0])

    bot.send_message(message.chat.id, text, reply_markup=final_kb, disable_web_page_preview=True)

@bot.message_handler(commands=['next'])
@bot.message_handler(func=lambda m: m.text == "Ближайший матч")
def cmd_next(message):
    show_game(message, get_next_game, "Ближайших матчей пока нет")

@bot.message_handler(func=lambda m: m.text == "Предыдущая игра")
def cmd_last(message):
    show_game(message, get_last_game, "Пока не было ни одной завершённой игры")

@bot.message_handler(commands=['status'])
@bot.message_handler(func=lambda m: m.text == "Мой статус")
def cmd_status(message):
    is_sub = message.from_user.id in get_subscribers()
    game = get_next_game()

    text = "Твой статус:\n\n"
    text += "Подписка активна — напоминания включены\n" if is_sub else "Ты не подписан на напоминания\n"

    kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    if is_sub:
        kb.add(
            telebot.types.InlineKeyboardButton("Отписаться", callback_data="unsubscribe"),
            telebot.types.InlineKeyboardButton("Обновить", callback_data="status_refresh")
        )
    else:
        kb.add(telebot.types.InlineKeyboardButton("Подписаться", callback_data="subscribe"))

    if game:
        game_text, stream_kb = format_game(game, is_upcoming=True)
        text += f"\n{game_text}"
        if stream_kb:
            kb.add(*stream_kb.keyboard[0])
    else:
        text += "\nБлижайших матчей пока нет"

    bot.send_message(message.chat.id, text, reply_markup=kb, disable_web_page_preview=True)

@bot.message_handler(commands=['subscribe'], func=lambda m: m.text == "Подписаться")
def cmd_subscribe(message):
    add_subscriber(message.from_user.id)
    bot.send_message(message.chat.id, "Готово! Напомню за час до игры")

@bot.message_handler(commands=['unsubscribe'], func=lambda m: m.text == "Отписаться")
def cmd_unsubscribe(message):
    remove_subscriber(message.from_user.id)
    bot.send_message(message.chat.id, "Подписка отменена")

@bot.callback_query_handler(func=lambda c: c.data == "subscribe")
def cb_sub(call):
    add_subscriber(call.from_user.id)
    bot.answer_callback_query(call.id, "Подписка оформлена!")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    bot.send_message(call.message.chat.id, "Теперь ты получишь напоминание за час до игры!")

@bot.callback_query_handler(func=lambda c: c.data == "unsubscribe")
def cb_unsub(call):
    remove_subscriber(call.from_user.id)
    bot.answer_callback_query(call.id, "Подписка отменена")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.callback_query_handler(func=lambda c: c.data == "status_refresh")
def cb_refresh(call):
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    cmd_status(call.message)

@bot.message_handler(commands=['start'])
def cmd_start(message):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add("Ближайший матч", "Предыдущая игра")
    kb.add("Мой статус", "Подписаться", "Отписаться")

    bot.send_message(message.chat.id,
        "Привет! Я бот лиги «Time of the Stars»\n\n",
        reply_markup=kb)

def main():
    init_db()
    load_teams()

    scheduler = BackgroundScheduler()
    scheduler.add_job(notify_about_upcoming, 'interval', minutes=10)
    scheduler.add_job(load_teams, 'interval', hours=6)
    scheduler.start()

    print("Бот запущен — всё работает идеально!")
    bot.infinity_polling(none_stop=True)

if __name__ == '__main__':
    main()