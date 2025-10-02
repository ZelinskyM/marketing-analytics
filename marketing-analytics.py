import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(
    page_title="Marketing Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- АДАПТИВНЫЙ CSS ДЛЯ ТЕЛЕФОНА ---
st.markdown("""
<style>
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
        }
        .row-widget.stColumns {
            flex-direction: column;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
        .stButton button {
            width: 100%;
            margin: 5px 0;
        }
        .stForm {
            width: 100% !important;
        }
        .stDataFrame {
            overflow-x: auto;
        }
        .css-1d391kg {
            padding: 1rem;
        }
    }
    
    .main {
        font-family: Arial, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- БАЗА ДАННЫХ ---
def create_client_id(name, phone):
    unique_string = f"{name}_{phone}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def load_data():
    try:
        df = pd.read_csv("marketing_database.csv", encoding='utf-8')
        if 'client_id' not in df.columns:
            df['client_id'] = df.apply(lambda row: create_client_id(row['Имя'], row['Телефон']), axis=1)
            df.to_csv("marketing_database.csv", index=False, encoding='utf-8')
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=[
            "client_id", "Дата", "Направление", "Имя", "Телефон", "Услуга", 
            "Цена", "Кто_пригласил", "Место_учебы", "Ссылка_VK", "Согласие_рассылка"
        ])

def save_data(df):
    df.to_csv("marketing_database.csv", index=False, encoding='utf-8')

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

# --- ЗАГРУЗКА ДАННЫХ ---
df = load_data()

# --- ФУНКЦИИ ДЛЯ СТАТИСТИКИ ---
def get_today_stats(df):
    today = datetime.now().strftime("%Y-%m-%d")
    # Исключаем записи с направлением "Рассылка" из статистики
    today_df = df[(df['Дата'].str.startswith(today)) & (df['Направление'] != 'Рассылка')]
    
    clients_today = today_df['Имя'].nunique()
    records_today = len(today_df)
    income_today = today_df['Цена'].sum()
    salary_today = income_today * 0.4
    
    return clients_today, records_today, income_today, salary_today

def get_month_stats(df, year_month=None):
    if year_month is None:
        year_month = datetime.now().strftime("%Y-%m")
    
    # Исключаем записи с направлением "Рассылка" из статистики
    month_df = df[(df['Дата'].str.startswith(year_month)) & (df['Направление'] != 'Рассылка')]
    
    stats = {
        'all_clients': month_df['Имя'].nunique(),
        'all_income': month_df['Цена'].sum(),
        'products_clients': month_df[month_df['Направление'] == 'Продукты']['Имя'].nunique(),
        'products_income': month_df[month_df['Направление'] == 'Продукты']['Цена'].sum(),
        'study_clients': month_df[month_df['Направление'] == 'Учеба']['Имя'].nunique(),
        'study_income': month_df[month_df['Направление'] == 'Учеба']['Цена'].sum(),
        'flowers_clients': month_df[month_df['Направление'] == 'Цветочный']['Имя'].nunique(),
        'flowers_income': month_df[month_df['Направление'] == 'Цветочный']['Цена'].sum(),
        'post_clients': month_df[month_df['Направление'] == 'Почта']['Имя'].nunique(),
        'post_income': month_df[month_df['Направление'] == 'Почта']['Цена'].sum(),
        'chop_clients': month_df[month_df['Направление'] == 'Chop']['Имя'].nunique(),
        'chop_income': month_df[month_df['Направление'] == 'Chop']['Цена'].sum(),
        'random_clients': month_df[month_df['Направление'] == 'Случайный']['Имя'].nunique(),
        'random_income': month_df[month_df['Направление'] == 'Случайный']['Цена'].sum()
    }
    
    return stats

# --- АДАПТИВНАЯ НАВИГАЦИЯ ---
st.sidebar.title("📱 Навигация")

# Определяем тип устройства
try:
    from streamlit import runtime
    if runtime.exists():
        context = runtime.get_instance().script_run_ctx
        if hasattr(context, 'request'):
            user_agent = context.request.headers.get('user-agent', '')
            is_mobile = any(device in user_agent.lower() for device in ['mobile', 'android', 'iphone'])
        else:
            is_mobile = False
    else:
        is_mobile = False
except:
    is_mobile = False

if is_mobile:
    page = st.sidebar.selectbox("Выберите страницу:", 
        ["Главная", "Добавить клиента", "Рассылка", "Аналитика"])
else:
    page = st.sidebar.radio("Выберите страницу:", 
        ["Главная", "Добавить клиента", "Рассылка", "Аналитика"])

# --- СТАТИСТИКА ЗА ДЕНЬ В САЙДБАРЕ ---
st.sidebar.markdown("---")

# Получаем статистику за сегодня (исключая рассылку)
clients_today, records_today, income_today, salary_today = get_today_stats(df)

st.sidebar.info(f"""
**Статистика за день:**
- Клиентов: {clients_today}
- Записей: {records_today}
- Выручка: {income_today:,} руб.
- Зарплата (40%): {salary_today:,.0f} руб.
""")

# --- ГЛАВНАЯ СТРАНИЦА ---
if page == "Главная":
    st.title("🏠 Marketing Analytics")
    st.markdown("---")
    
    # Выбор месяца для аналитики
    if not df.empty:
        df['Месяц'] = df['Дата'].str[:7]
        available_months = sorted(df['Месяц'].unique(), reverse=True)
        selected_month = st.selectbox("Выберите месяц для аналитики:", 
                                    available_months, index=0)
    else:
        selected_month = datetime.now().strftime("%Y-%m")
        st.selectbox("Выберите месяц для аналитики:", [selected_month])
    
    # Статистика за выбранный месяц (исключая рассылку)
    month_stats = get_month_stats(df, selected_month)
    
    # Основная статистика за месяц
    st.subheader(f"📈 Статистика за {selected_month}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Всего клиентов за месяц", month_stats['all_clients'])
        st.metric("Общая выручка за месяц", f"{month_stats['all_income']:,} руб.")
    
    with col2:
        # Статистика по направлениям
        st.markdown("**Выручка по направлениям:**")
        st.markdown(f"📚 Учеба: {month_stats['study_income']:,} руб.")
        st.markdown(f"🛍️ Продукты: {month_stats['products_income']:,} руб.")
        st.markdown(f"💐 Цветочный: {month_stats['flowers_income']:,} руб.")
        st.markdown(f"📮 Почта: {month_stats['post_income']:,} руб.")
        st.markdown(f"✂️ Chop: {month_stats['chop_income']:,} руб.")
        st.markdown(f"🎲 Случайный: {month_stats['random_income']:,} руб.")

# --- ДОБАВИТЬ КЛИЕНТА ---
elif page == "Добавить клиента":
    st.title("👥 Добавить клиента")
    st.markdown("---")
    
    with st.form("client_form"):
        # Добавляем новые направления "Chop" и "Случайный"
        direction = st.selectbox("Направление*", ["Учеба", "Продукты", "Цветочный", "Почта", "Chop", "Случайный"])
        name = st.text_input("Имя клиента*")
        phone = st.text_input("Номер телефона*")
        service = st.selectbox("Услуга*", list(SERVICE_PRICES.keys()))
        
        price = SERVICE_PRICES[service]
        st.info(f"💰 Стоимость услуги: **{price} руб.**")
        
        # Поле "Кто пригласил" только для Учебы
        if direction == "Учеба":
            # Все клиенты из базы + контакты из рассылки (исключая направление "Рассылка" из выбора)
            all_people = list(df[df['Направление'] != 'Рассылка']["Имя"].unique())
            mailing_contacts = list(df[df["Направление"] == "Рассылка"]["Имя"].unique())
            all_available_people = list(set(all_people + mailing_contacts))
            
            invited_by = st.selectbox("Кто пригласил", [""] + sorted(all_available_people))
        else:
            invited_by = ""
        
        submitted = st.form_submit_button("💾 Сохранить клиента", use_container_width=True)
        
        if submitted:
            if name and phone and service:
                client_id = create_client_id(name, phone)
                
                # Проверка на дубликат
                existing_client = df[df['client_id'] == client_id]
                
                if len(existing_client) > 0:
                    st.warning("Клиент уже существует в базе. Обновляем информацию...")
                    mask = df['client_id'] == client_id
                    df.loc[mask, 'Дата'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    df.loc[mask, 'Направление'] = direction
                    df.loc[mask, 'Услуга'] = service
                    df.loc[mask, 'Цена'] = price
                    df.loc[mask, 'Кто_пригласил'] = invited_by
                else:
                    new_client = {
                        "client_id": client_id,
                        "Дата": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Направление": direction,
                        "Имя": name,
                        "Телефон": phone,
                        "Услуга": service,
                        "Цена": price,
                        "Кто_пригласил": invited_by,
                        "Место_учебы": "",
                        "Ссылка_VK": "",
                        "Согласие_рассылка": ""
                    }
                    df = pd.concat([df, pd.DataFrame([new_client])], ignore_index=True)
                
                save_data(df)
                st.success(f"Клиент {name} успешно сохранен!")
            else:
                st.error("Пожалуйста, заполните обязательные поля (отмечены *)")

# --- РАССЫЛКА ---
elif page == "Рассылка":
    st.title("📧 Рассылка")
    st.markdown("---")
    
    # На мобильных используем selectbox вместо tabs
    if is_mobile:
        tab_option = st.selectbox("Выберите раздел:", ["Добавить контакт", "База контактов"])
    else:
        tab_option = st.radio("Выберите раздел:", ["Добавить контакт", "База контактов"], horizontal=True)
    
    if tab_option == "Добавить контакт":
        with st.form("mailing_form"):
            mailing_name = st.text_input("Имя*")
            study_place = st.text_input("Место учебы")
            vk_link = st.text_input("Ссылка VK")
            mailing_consent = st.radio("Согласие на рассылку*", ["Да", "Нет"])
            
            submitted_mailing = st.form_submit_button("💾 Сохранить контакт", use_container_width=True)
            
            if submitted_mailing:
                if mailing_name:
                    client_id = create_client_id(mailing_name, "")
                    
                    new_mailing = {
                        "client_id": client_id,
                        "Дата": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Направление": "Рассылка",
                        "Имя": mailing_name,
                        "Телефон": "",
                        "Услуга": "",
                        "Цена": 0,
                        "Кто_пригласил": "",
                        "Место_учебы": study_place,
                        "Ссылка_VK": vk_link,
                        "Согласие_рассылка": mailing_consent
                    }
                    df = pd.concat([df, pd.DataFrame([new_mailing])], ignore_index=True)
                    save_data(df)
                    st.success(f"{mailing_name} добавлен в базу рассылки!")
                else:
                    st.error("Пожалуйста, укажите имя")
    
    else:  # База контактов
        mailing_df = df[df["Направление"] == "Рассылка"]
        if not mailing_df.empty:
            st.dataframe(mailing_df[["Имя", "Место_учебы", "Ссылка_VK", "Согласие_рассылка"]])
            
            contacts_to_delete = st.multiselect(
                "Выберите контакты для удаления:",
                mailing_df["Имя"].unique()
            )
            
            if contacts_to_delete and st.button("Удалить выбранные контакты", use_container_width=True):
                df = df[~((df["Направление"] == "Рассылка") & (df["Имя"].isin(contacts_to_delete)))]
                save_data(df)
                st.success(f"Удалено {len(contacts_to_delete)} контактов!")
                st.rerun()
        else:
            st.info("База рассылки пуста")

# --- АНАЛИТИКА ---
elif page == "Аналитика":
    st.title("📈 Аналитика")
    st.markdown("---")
    
    if not df.empty:
        # Статистика - на мобильных вертикально
        st.subheader("📊 Общая статистика")
        
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
        with col1:
            # Исключаем рассылку из общей статистики
            total_income = df[df['Направление'] != 'Рассылка']["Цена"].sum()
            st.metric("Общая выручка", f"{total_income:,} руб.")
            
        with col2:
            total_clients = df[df['Направление'] != 'Рассылка']["Имя"].nunique()
            st.metric("Всего клиентов", total_clients)
            
        with col3:
            total_services = len(df[df['Направление'] != 'Рассылка'])
            st.metric("Всего услуг", total_services)
            
        with col4:
            filtered_df = df[df['Направление'] != 'Рассылка']
            avg_price = filtered_df["Цена"].mean() if len(filtered_df) > 0 else 0
            st.metric("Средний чек", f"{avg_price:.0f} руб.")
        
        # Фильтры
        st.subheader("🔍 Фильтры")
        
        filter_direction = st.multiselect("Направление", df["Направление"].unique())
        filter_service = st.multiselect("Услуга", df["Услуга"].unique())
        
        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input("Минимальная цена", 0, value=0)
        with col2:
            max_price = st.number_input("Максимальная цена", 0, value=int(df["Цена"].max()))
        
        # Применяем фильтры
        filtered_df = df.copy()
        
        if filter_direction:
            filtered_df = filtered_df[filtered_df["Направление"].isin(filter_direction)]
        if filter_service:
            filtered_df = filtered_df[filtered_df["Услуга"].isin(filter_service)]
        
        filtered_df = filtered_df[(filtered_df["Цена"] >= min_price) & (filtered_df["Цена"] <= max_price)]
        
        # Данные
        st.subheader("📋 Данные")
        st.dataframe(filtered_df)
        
        # Управление клиентами
        st.subheader("🗑️ Управление клиентами")
        all_clients = filtered_df["Имя"].unique()
        
        if len(all_clients) > 0:
            clients_to_delete = st.multiselect("Выберите клиентов для удаления:", all_clients)
            
            if clients_to_delete and st.button("Удалить выбранных клиентов", use_container_width=True):
                df = df[~df["Имя"].isin(clients_to_delete)]
                save_data(df)
                st.success(f"Удалено {len(clients_to_delete)} клиентов!")
                st.rerun()
        
        # Экспорт
        st.subheader("📤 Экспорт данных")
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Скачать CSV",
            data=csv,
            file_name=f"marketing_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    else:
        st.info("Данные появятся здесь после добавления клиентов")
