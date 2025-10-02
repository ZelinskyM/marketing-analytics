import pandas as pd
from datetime import datetime
import hashlib
import requests
import time
import re
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = "8140791835:AAGh6DwKrOK19iAupdwi50bGM5kjFIZPraM"
last_update_id = 0

SERVICE_PRICES = {
    "Стрижка": 900, "Борода": 500, "VIP": 500,
    "Удаление воском 1": 200, "Удаление воском 2": 300,
    "Уходовая маска Nishman": 1000, "Стрижка+борода": 1400,
    "Детская": 800, "Под машинку": 900
}

def load_data():
    try:
        # Используем относительный путь для работы с GitHub
        df = pd.read_csv("marketing_database.csv", encoding='utf-8')
        logger.info("База данных загружена")
        return df
    except FileNotFoundError:
        logger.info("Создана новая база данных")
        return pd.DataFrame(columns=[
            "visit_id", "client_id", "Дата", "Направление", "Имя", "Телефон", "Услуга", 
            "Цена", "Кто_пригласил", "Место_учебы", "Ссылка_VK", "Согласие_рассылка"
        ])

def save_data(df):
    df.to_csv("marketing_database.csv", index=False, encoding='utf-8')
    logger.info("Данные сохранены")

def send_telegram_message(chat_id, message, parse_mode='HTML'):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': parse_mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            logger.error(f"Telegram API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
        return False

def get_telegram_updates():
    global last_update_id
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {
        'offset': last_update_id + 1,
        'timeout': 10
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                return data.get('result', [])
        return []
    except Exception as e:
        logger.error(f"Telegram update error: {e}")
        return []

def process_telegram_command(update):
    global last_update_id
    
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '').strip()
    
    if not text or not chat_id:
        return
    
    last_update_id = update.get('update_id', last_update_id)
    logger.info(f"Обработка команды от {chat_id}: {text}")
    
    if text == '/start':
        welcome_message = """
🤖 <b>Добро пожаловать в Marketing Analytics Bot!</b>

Доступные команды:
/help - Показать справку
/add_client - Добавить клиента
/add_mailing - Добавить в рассылку
/stats - Статистика за сегодня
/history - История клиента
        """
        send_telegram_message(chat_id, welcome_message)
        
    elif text == '/help':
        help_message = """
📖 <b>Справка по командам:</b>

<b>Добавление клиентов:</b>
/add_client - Добавить клиента

<b>Рассылка:</b>
/add_mailing - Добавить в рассылку

<b>Аналитика:</b>
/stats - Статистика за сегодня
/history - История клиента

<b>Формат данных:</b>
Иван, 89123456789, Стрижка, Chop
        """
        send_telegram_message(chat_id, help_message)
        
    elif text == '/stats':
        df = load_data()
        clients_today, records_today, income_today, salary_today = get_today_stats(df)
        stats_message = f"""
📊 <b>Статистика за сегодня</b>

👥 Клиентов: <b>{clients_today}</b>
📝 Записей: <b>{records_today}</b>
💰 Выручка: <b>{income_today:,} ₽</b>
💵 Зарплата: <b>{salary_today:,.0f} ₽</b>
        """
        send_telegram_message(chat_id, stats_message)
        
    elif text == '/add_client':
        instruction = """
📝 <b>Добавление клиента</b>

Отправь данные в формате:
<code>Имя, Телефон, Услуга, Направление</code>

<b>Пример:</b>
<code>Анна, 89991234567, Стрижка, Chop</code>
        """
        send_telegram_message(chat_id, instruction)
        
    elif text == '/add_mailing':
        instruction = """
📧 <b>Добавление в рассылку</b>

Отправь данные в формате:
<code>Имя, Место учебы, Ссылка VK</code>

<b>Пример:</b>
<code>Мария, ТПУ, vk.com/maria</code>
        """
        send_telegram_message(chat_id, instruction)
        
    elif text == '/history':
        instruction = """
📋 <b>История клиента</b>

Отправь имя клиента:

<code>Иван</code>
        """
        send_telegram_message(chat_id, instruction)
    
    else:
        if re.match(r'^[^,]+,\s*\d+,\s*[^,]+,\s*[^,]+$', text):
            process_client_from_telegram(chat_id, text)
        elif re.match(r'^[^,]+,\s*[^,]*,\s*[^,]*$', text) and text.count(',') == 2:
            process_mailing_from_telegram(chat_id, text)
        elif re.match(r'^[а-яА-Яa-zA-Z\s]+$', text):
            process_client_history(chat_id, text)
        else:
            send_telegram_message(chat_id, "❌ Непонятная команда. Используй /help")

def process_client_from_telegram(chat_id, text):
    try:
        parts = [part.strip() for part in text.split(',')]
        if len(parts) != 4:
            send_telegram_message(chat_id, "❌ Неверный формат. Нужно: Имя, Телефон, Услуга, Направление")
            return
        
        name, phone, service, direction = parts
        
        if service not in SERVICE_PRICES:
            send_telegram_message(chat_id, f"❌ Услуга '{service}' не найдена")
            return
        
        valid_directions = ["Учеба", "Продукты", "Цветочный", "Почта", "Chop", "Случайный"]
        if direction not in valid_directions:
            send_telegram_message(chat_id, f"❌ Направление '{direction}' не найдено")
            return
        
        price = SERVICE_PRICES[service]
        df = load_data()
        
        client_id = create_client_id(name, phone)
        visit_id = hashlib.md5(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_{name}_{phone}".encode()).hexdigest()
        
        existing_client = df[df['client_id'] == client_id]
        is_new_client = len(existing_client) == 0
        visit_count = len(existing_client) + 1
        
        new_visit = {
            "visit_id": visit_id, "client_id": client_id,
            "Дата": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Направление": direction, "Имя": name, "Телефон": phone,
            "Услуга": service, "Цена": price, "Кто_пригласил": "",
            "Место_учебы": "", "Ссылка_VK": "", "Согласие_рассылка": ""
        }
        
        df = pd.concat([df, pd.DataFrame([new_visit])], ignore_index=True)
        save_data(df)
        
        if is_new_client:
            message = f"🎉 <b>НОВЫЙ КЛИЕНТ ДОБАВЛЕН</b>\n\n"
        else:
            message = f"📋 <b>НОВОЕ ПОСЕЩЕНИЕ</b>\n\n"
        
        message += f"👤 <b>Имя:</b> {name}\n📞 <b>Телефон:</b> {phone}\n"
        message += f"🎯 <b>Направление:</b> {direction}\n💇 <b>Услуга:</b> {service}\n"
        message += f"💰 <b>Цена:</b> {price} руб.\n"
        
        if not is_new_client:
            message += f"📊 <b>Всего посещений:</b> {visit_count}\n"
        
        message += f"🕒 <b>Время:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}"
        
        send_telegram_message(chat_id, message)
        logger.info(f"Добавлен клиент: {name}")
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка: {str(e)}")
        logger.error(f"Ошибка добавления клиента: {e}")

def process_mailing_from_telegram(chat_id, text):
    try:
        parts = [part.strip() for part in text.split(',')]
        name, study_place, vk_link = parts
        
        df = load_data()
        client_id = create_client_id(name, "")
        visit_id = hashlib.md5(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_{name}_".encode()).hexdigest()
        
        new_mailing = {
            "visit_id": visit_id, "client_id": client_id,
            "Дата": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Направление": "Рассылка", "Имя": name, "Телефон": "",
            "Услуга": "", "Цена": 0, "Кто_пригласил": "",
            "Место_учебы": study_place, "Ссылка_VK": vk_link, "Согласие_рассылка": "Да"
        }
        
        df = pd.concat([df, pd.DataFrame([new_mailing])], ignore_index=True)
        save_data(df)
        
        message = f"📧 <b>КОНТАКТ ДОБАВЛЕН В РАССЫЛКУ</b>\n\n"
        message += f"👤 <b>Имя:</b> {name}\n🎓 <b>Место учебы:</b> {study_place}\n"
        message += f"🔗 <b>Ссылка VK:</b> {vk_link}\n✅ <b>Согласие:</b> Да\n"
        message += f"🕒 <b>Время:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}"
        
        send_telegram_message(chat_id, message)
        logger.info(f"Добавлен в рассылку: {name}")
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка: {str(e)}")
        logger.error(f"Ошибка добавления в рассылку: {e}")

def process_client_history(chat_id, client_name):
    try:
        df = load_data()
        client_data = df[df['Имя'] == client_name]
        if client_data.empty:
            send_telegram_message(chat_id, f"❌ Клиент '{client_name}' не найден")
            return
        
        client_id = client_data.iloc[0]['client_id']
        client_history = get_client_history(df, client_id)
        
        total_visits = len(client_history)
        total_spent = client_history['Цена'].sum()
        avg_spent = total_spent / total_visits if total_visits > 0 else 0
        
        message = f"📋 <b>ИСТОРИЯ КЛИЕНТА: {client_name}</b>\n\n"
        message += f"📊 <b>Всего посещений:</b> {total_visits}\n"
        message += f"💰 <b>Всего потрачено:</b> {total_spent:,} руб.\n"
        message += f"💳 <b>Средний чек:</b> {avg_spent:.0f} руб.\n\n"
        
        message += "<b>Последние посещения:</b>\n"
        for _, visit in client_history.head(5).iterrows():
            message += f"• {visit['Дата'][:16]} - {visit['Услуга']} ({visit['Цена']} руб.)\n"
        
        if total_visits > 5:
            message += f"\n... и еще {total_visits - 5} посещений"
        
        send_telegram_message(chat_id, message)
        logger.info(f"Показана история клиента: {client_name}")
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка: {str(e)}")
        logger.error(f"Ошибка получения истории: {e}")

def create_client_id(name, phone):
    return hashlib.md5(f"{name}_{phone}".encode()).hexdigest()

def get_today_stats(df):
    today = datetime.now().strftime("%Y-%m-%d")
    today_df = df[(df['Дата'].str.startswith(today)) & (df['Направление'] != 'Рассылка')]
    
    clients_today = today_df['Имя'].nunique()
    records_today = len(today_df)
    income_today = today_df['Цена'].sum()
    salary_today = income_today * 0.4
    
    return clients_today, records_today, income_today, salary_today

def get_client_history(df, client_id):
    return df[df['client_id'] == client_id].sort_values('Дата', ascending=False)

def telegram_bot_worker():
    global last_update_id
    logger.info("🤖 Telegram бот запущен и слушает сообщения...")
    
    while True:
        try:
            updates = get_telegram_updates()
            
            for update in updates:
                update_id = update.get('update_id', 0)
                if update_id > last_update_id:
                    last_update_id = update_id
                    process_telegram_command(update)
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Ошибка бота: {e}")
            time.sleep(5)

if __name__ == "__main__":
    telegram_bot_worker()
