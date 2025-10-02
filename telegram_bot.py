import pandas as pd
from datetime import datetime
import hashlib
import requests
import time
import re
import os

# --- НАСТРОЙКИ TELEGRAM ---
TELEGRAM_TOKEN = "8140791835:AAGh6DwKrOK19iAupdwi50bGM5kjFIZPraM"

# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ---
last_update_id = 0

# --- ОБНОВЛЕННЫЕ ЦЕНЫ УСЛУГ ---
SERVICE_PRICES = {
    "Стрижка": 900,
    "Борода": 500,
    "VIP": 500,
    "Удаление воском 1": 200,
    "Удаление воском 2": 300,
    "Уходовая маска Nishman": 1000,
    "Стрижка+борода": 1400,
    "Детская": 800,
    "Под машинку": 900
}

# --- БАЗА ДАННЫХ ---
def create_client_id(name, phone):
    unique_string = f"{name}_{phone}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def load_data():
    try:
        df = pd.read_csv("marketing_database.csv", encoding='utf-8')
        if 'visit_id' not in df.columns:
            df['visit_id'] = df.apply(lambda row: hashlib.md5(f"{row['Дата']}_{row['Имя']}_{row['Телефон']}".encode()).hexdigest(), axis=1)
            df.to_csv("marketing_database.csv", index=False, encoding='utf-8')
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "visit_id", "client_id", "Дата", "Направление", "Имя", "Телефон", "Услуга", 
            "Цена", "Кто_пригласил", "Место_учебы", "Ссылка_VK", "Согласие_рассылка"
        ])

def save_data(df):
    df.to_csv("marketing_database.csv", index=False, encoding='utf-8')

# --- ФУНКЦИИ ДЛЯ СТАТИСТИКИ ---
def get_today_stats(df):
    today = datetime.now().strftime("%Y-%m-%d")
    today_df = df[(df['Дата'].str.startswith(today)) & (df['Направление'] != 'Рассылка')]
    
    clients_today = today_df['Имя'].nunique()
    records_today = len(today_df)
    income_today = today_df['Цена'].sum()
    salary_today = income_today * 0.4
    
    return clients_today, records_today, income_today, salary_today

def get_client_history(df, client_id):
    """Возвращает историю всех посещений клиента"""
    client_history = df[df['client_id'] == client_id].sort_values('Дата', ascending=False)
    return client_history

# --- ФУНКЦИИ TELEGRAM ---
def send_telegram_message(chat_id, message, parse_mode='HTML'):
    """Отправляет сообщение в Telegram"""
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
            print(f"Telegram API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False

def get_telegram_updates():
    """Получает обновления от Telegram бота"""
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
        print(f"Telegram update error: {e}")
        return []

def get_bot_info():
    """Получает информацию о боте"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def process_client_from_telegram(chat_id, text):
    """Обрабатывает данные клиента из Telegram"""
    try:
        parts = [part.strip() for part in text.split(',')]
        if len(parts) != 4:
            send_telegram_message(chat_id, "❌ Неверный формат. Нужно: Имя, Телефон, Услуга, Направление")
            return
        
        name, phone, service, direction = parts
        
        # Проверяем услугу
        if service not in SERVICE_PRICES:
            send_telegram_message(chat_id, f"❌ Услуга '{service}' не найдена. Доступные: {', '.join(SERVICE_PRICES.keys())}")
            return
        
        # Проверяем направление
        valid_directions = ["Учеба", "Продукты", "Цветочный", "Почта", "Chop", "Случайный"]
        if direction not in valid_directions:
            send_telegram_message(chat_id, f"❌ Направление '{direction}' не найдено. Доступные: {', '.join(valid_directions)}")
            return
        
        price = SERVICE_PRICES[service]
        
        # Загружаем актуальные данные
        df = load_data()
        
        # Добавляем клиента в базу
        client_id = create_client_id(name, phone)
        visit_id = hashlib.md5(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_{name}_{phone}".encode()).hexdigest()
        
        existing_client = df[df['client_id'] == client_id]
        is_new_client = len(existing_client) == 0
        visit_count = len(existing_client) + 1
        
        new_visit = {
            "visit_id": visit_id,
            "client_id": client_id,
            "Дата": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Направление": direction,
            "Имя": name,
            "Телефон": phone,
            "Услуга": service,
            "Цена": price,
            "Кто_пригласил": "",
            "Место_учебы": "",
            "Ссылка_VK": "",
            "Согласие_рассылка": ""
        }
        
        df = pd.concat([df, pd.DataFrame([new_visit])], ignore_index=True)
        save_data(df)
        
        # Отправляем подтверждение
        if is_new_client:
            message = f"🎉 <b>НОВЫЙ КЛИЕНТ ДОБАВЛЕН</b>\n\n"
        else:
            message = f"📋 <b>НОВОЕ ПОСЕЩЕНИЕ</b>\n\n"
        
        message += f"👤 <b>Имя:</b> {name}\n"
        message += f"📞 <b>Телефон:</b> {phone}\n"
        message += f"🎯 <b>Направление:</b> {direction}\n"
        message += f"💇 <b>Услуга:</b> {service}\n"
        message += f"💰 <b>Цена:</b> {price} руб.\n"
        
        if not is_new_client:
            message += f"📊 <b>Всего посещений:</b> {visit_count}\n"
        
        message += f"🕒 <b>Время:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}"
        
        send_telegram_message(chat_id, message)
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка при добавлении клиента: {str(e)}")

def process_mailing_from_telegram(chat_id, text):
    """Обрабатывает данные рассылки из Telegram"""
    try:
        parts = [part.strip() for part in text.split(',')]
        name, study_place, vk_link = parts
        
        # Загружаем актуальные данные
        df = load_data()
        
        # Добавляем в рассылку
        client_id = create_client_id(name, "")
        visit_id = hashlib.md5(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_{name}_".encode()).hexdigest()
        
        new_mailing = {
            "visit_id": visit_id,
            "client_id": client_id,
            "Дата": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Направление": "Рассылка",
            "Имя": name,
            "Телефон": "",
            "Услуга": "",
            "Цена": 0,
            "Кто_пригласил": "",
            "Место_учебы": study_place,
            "Ссылка_VK": vk_link,
            "Согласие_рассылка": "Да"
        }
        
        df = pd.concat([df, pd.DataFrame([new_mailing])], ignore_index=True)
        save_data(df)
        
        message = f"📧 <b>КОНТАКТ ДОБАВЛЕН В РАССЫЛКУ</b>\n\n"
        message += f"👤 <b>Имя:</b> {name}\n"
        message += f"🎓 <b>Место учебы:</b> {study_place}\n"
        message += f"🔗 <b>Ссылка VK:</b> {vk_link}\n"
        message += f"✅ <b>Согласие:</b> Да\n"
        message += f"🕒 <b>Время:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}"
        
        send_telegram_message(chat_id, message)
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка при добавлении в рассылку: {str(e)}")

def process_client_history(chat_id, client_name):
    """Показывает историю клиента"""
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
        
        # Последние 5 посещений
        message += "<b>Последние посещения:</b>\n"
        for _, visit in client_history.head(5).iterrows():
            message += f"• {visit['Дата'][:16]} - {visit['Услуга']} ({visit['Цена']} руб.)\n"
        
        if total_visits > 5:
            message += f"\n... и еще {total_visits - 5} посещений"
        
        send_telegram_message(chat_id, message)
        
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка при получении истории: {str(e)}")

def process_telegram_command(update):
    """Обрабатывает команды из Telegram"""
    global last_update_id
    
    message = update.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '').strip()
    
    if not text or not chat_id:
        return
    
    # Обновляем last_update_id
    last_update_id = update.get('update_id', last_update_id)
    
    print(f"Получено сообщение от {chat_id}: {text}")
    
    # Основные команды
    if text == '/start':
        welcome_message = """
🤖 <b>Добро пожаловать в Marketing Analytics Bot!</b>

Доступные команды:
/help - Показать справку
/add_client - Добавить клиента
/add_mailing - Добавить в рассылку
/stats - Статистика за сегодня
/history - История клиента

Просто отправь команду и следуй инструкциям!
        """
        send_telegram_message(chat_id, welcome_message)
        
    elif text == '/help':
        help_message = """
📖 <b>Справка по командам:</b>

<b>Добавление клиентов:</b>
/add_client - Добавить нового клиента или посещение

<b>Рассылка:</b>
/add_mailing - Добавить контакт в рассылку

<b>Аналитика:</b>
/stats - Статистика за сегодня
/history - История клиента

<b>Формат добавления клиента:</b>
Имя, Телефон, Услуга, Направление

Пример:
<code>Иван, 89123456789, Стрижка, Chop</code>

<b>Формат рассылки:</b>
Имя, Место учебы, Ссылка VK

Пример:
<code>Мария, ТПУ, vk.com/maria</code>
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

📅 {datetime.now().strftime('%d.%m.%Y')}
        """
        send_telegram_message(chat_id, stats_message)
        
    elif text == '/add_client':
        instruction = """
📝 <b>Добавление клиента</b>

Отправь данные в формате:
<code>Имя, Телефон, Услуга, Направление</code>

<b>Пример:</b>
<code>Анна, 89991234567, Стрижка, Chop</code>

<b>Доступные услуги:</b>
Стрижка, Борода, VIP, Удаление воском 1, Удаление воском 2, Уходовая маска Nishman, Стрижка+борода, Детская, Под машинку

<b>Направления:</b>
Учеба, Продукты, Цветочный, Почта, Chop, Случайный
        """
        send_telegram_message(chat_id, instruction)
        
    elif text == '/add_mailing':
        instruction = """
📧 <b>Добавление в рассылку</b>

Отправь данные в формате:
<code>Имя, Место учебы, Ссылка VK</code>

<b>Пример:</b>
<code>Мария, ТПУ, vk.com/maria_ivanova</code>
        """
        send_telegram_message(chat_id, instruction)
        
    elif text == '/history':
        instruction = """
📋 <b>История клиента</b>

Отправь имя клиента для просмотра истории:

<code>Иван</code>
        """
        send_telegram_message(chat_id, instruction)
    
    else:
        # Обработка данных клиента
        if re.match(r'^[^,]+,\s*\d+,\s*[^,]+,\s*[^,]+$', text):
            process_client_from_telegram(chat_id, text)
        elif re.match(r'^[^,]+,\s*[^,]*,\s*[^,]*$', text) and text.count(',') == 2:
            process_mailing_from_telegram(chat_id, text)
        elif re.match(r'^[а-яА-Яa-zA-Z\s]+$', text):
            process_client_history(chat_id, text)
        else:
            send_telegram_message(chat_id, "❌ Непонятная команда. Используй /help для справки.")

def telegram_bot_worker():
    """Фоновая задача для обработки Telegram сообщений"""
    global last_update_id
    
    print("🤖 Telegram бот запущен и слушает сообщения...")
    
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
            print(f"Telegram bot error: {e}")
            time.sleep(5)

# --- ЗАПУСК БОТА ---
if __name__ == "__main__":
    print("🚀 Запуск Telegram бота...")
    
    # Проверяем токен
    bot_info = get_bot_info()
    if bot_info and bot_info.get('ok'):
        bot_data = bot_info['result']
        print(f"✅ Бот подключен: @{bot_data.get('username', 'N/A')}")
    else:
        print("❌ Ошибка подключения к боту")
        exit(1)
    
    # Запускаем бота
    telegram_bot_worker()
