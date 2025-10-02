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

# --- СОВРЕМЕННЫЙ CSS ---
st.markdown("""
<style>
    /* Основные стили */
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0F1117;
        color: #FAFAFA;
    }
    
    .main .block-container {
        background: #1E1E1E;
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1rem;
        border: 1px solid #2D2D2D;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    /* Сайдбар */
    .css-1d391kg {
        background: linear-gradient(135deg, #1E1E1E 0%, #2D2D2D 100%);
        border-right: 1px solid #2D2D2D;
    }
    
    .css-1d391kg .css-1lcbmhc {
        background: transparent;
    }
    
    /* Заголовки */
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2.2rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
    }
    
    /* Кнопки */
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    }
    
    /* Формы */
    .stForm {
        background: #2D2D2D;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid #3D3D3D;
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background: #1E1E1E;
        border: 1px solid #3D3D3D;
        border-radius: 10px;
        color: #FFFFFF;
        padding: 12px;
    }
    
    .stRadio>div {
        background: #2D2D2D;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #3D3D3D;
    }
    
    /* Информационные блоки */
    .stInfo {
        background: linear-gradient(135deg, #2D2D2D, #3D3D3D);
        border: 1px solid #4ECDC4;
        border-radius: 12px;
    }
    
    /* Метрики */
    .stMetric {
        background: linear-gradient(135deg, #2D2D2D, #3D3D3D);
        border: 1px solid #3D3D3D;
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Таблицы */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #3D3D3D;
    }
    
    /* Адаптивность для телефона */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem;
            border-radius: 12px;
            margin-top: 0.5rem;
        }
        
        h1 {
            font-size: 1.8rem;
        }
        
        .stForm {
            padding: 1.5rem;
        }
        
        /* Автоматическое скрытие сайдбара после выбора */
        .css-1d391kg {
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        .css-1d391kg:focus-within {
            transform: translateX(0);
        }
    }
    
    /* Скрываем некоторые элементы на очень маленьких экранах */
    @media (max-width: 480px) {
        .main .block-container {
            padding: 0.8rem;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        h2 {
            font-size: 1.2rem;
        }
    }
    
    /* Стили для успешных сообщений */
    .stSuccess {
        background: linear-gradient(135deg, #2D2D2D, #1E3A28);
        border: 1px solid #10B981;
        border-radius: 12px;
    }
    
    /* Стили для предупреждений */
    .stWarning {
        background: linear-gradient(135deg, #2D2D2D, #3A2A1E);
        border: 1px solid #F59E0B;
        border-radius: 12px;
    }
    
    /* Стили для ошибок */
    .stError {
        background: linear-gradient(135deg, #2D2D2D, #3A1E1E);
        border: 1px solid #EF4444;
        border-radius: 12px;
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
        # Создаем visit_id для существующих данных если его нет
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
    today_df = df[(df['Дата'].str.startswith(today)) & (df['Направление'] != 'Рассылка')]
    
    clients_today = today_df['Имя'].nunique()
    records_today = len(today_df)
    income_today = today_df['Цена'].sum()
    salary_today = income_today * 0.4
    
    return clients_today, records_today, income_today, salary_today

def get_month_stats(df, year_month=None):
    if year_month is None:
        year_month = datetime.now().strftime("%Y-%m")
    
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

# --- ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ ИСТОРИИ КЛИЕНТА ---
def get_client_history(df, client_id):
    """Возвращает историю всех посещений клиента"""
    client_history = df[df['client_id'] == client_id].sort_values('Дата', ascending=False)
    return client_history

# --- АДАПТИВНАЯ НАВИГАЦИЯ ---
st.sidebar.title("🚀 Навигация")

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
        ["Главная", "Добавить клиента", "Рассылка", "Аналитика", "История клиентов"])
else:
    page = st.sidebar.radio("Выберите страницу:", 
        ["Главная", "Добавить клиента", "Рассылка", "Аналитика", "История клиентов"])

# --- СТАТИСТИКА ЗА ДЕНЬ В САЙДБАРЕ ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Сегодня")

clients_today, records_today, income_today, salary_today = get_today_stats(df)

st.sidebar.markdown(f"""
<div style='background: linear-gradient(135deg, #2D2D2D, #3D3D3D); padding: 1rem; border-radius: 12px; border: 1px solid #3D3D3D;'>
    <div style='color: #4ECDC4; font-size: 0.9rem;'>👥 Клиентов: <b>{clients_today}</b></div>
    <div style='color: #FF6B6B; font-size: 0.9rem;'>📝 Записей: <b>{records_today}</b></div>
    <div style='color: #FFD93D; font-size: 0.9rem;'>💰 Выручка: <b>{income_today:,} ₽</b></div>
    <div style='color: #6BCF7F; font-size: 0.9rem;'>💵 Зарплата: <b>{salary_today:,.0f} ₽</b></div>
</div>
""", unsafe_allow_html=True)

# --- ГЛАВНАЯ СТРАНИЦА ---
if page == "Главная":
    st.title("📈 Marketing Analytics")
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
    
    # Статистика за выбранный месяц
    month_stats = get_month_stats(df, selected_month)
    
    # Основная статистика за месяц
    st.subheader(f"📊 Статистика за {selected_month}")
    
    # Создаем две колонки: левая для основных метрик, правая для аналитики по направлениям
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Основные метрики друг под другом
        st.metric("👥 Клиентов", month_stats['all_clients'])
        st.metric("💰 Выручка", f"{month_stats['all_income']:,} ₽")
    
    with col2:
        # Аналитика по направлениям (компактно)
        st.markdown("**📈 По направлениям:**")
        st.markdown(f"📚 Учеба {month_stats['study_income']:,} ₽")
        st.markdown(f"🛍️ Продукты {month_stats['products_income']:,} ₽")
        st.markdown(f"💐 Цветочный{month_stats['flowers_income']:,} ₽")
        st.markdown(f"📮 Почта {month_stats['post_income']:,} ₽")
        st.markdown(f"✂️ Chop {month_stats['chop_income']:,} ₽")
        st.markdown(f"🎲 Случайный {month_stats['random_income']:,} ₽")

# --- ДОБАВИТЬ КЛИЕНТА ---
elif page == "Добавить клиента":
    st.title("👥 Добавить клиента")
    st.markdown("---")
    
    # Создаем форму с уникальным ключом
    with st.form("client_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            direction = st.selectbox("Направление*", ["Учеба", "Продукты", "Цветочный", "Почта", "Chop", "Случайный"])
            name = st.text_input("Имя клиента*")
            phone = st.text_input("Номер телефона*")
            
        with col2:
            service = st.selectbox("Услуга*", list(SERVICE_PRICES.keys()))
            price = SERVICE_PRICES[service]
            st.info(f"💰 Стоимость услуги: **{price} руб.**")
            
            # Поле "Кто пригласил" только для Учебы
            if direction == "Учеба":
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
                visit_id = hashlib.md5(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_{name}_{phone}".encode()).hexdigest()
                
                # Проверка на существующего клиента
                existing_client = df[df['client_id'] == client_id]
                
                if len(existing_client) > 0:
                    st.warning(f"👤 Клиент {name} уже существует в базе. Добавляем новое посещение...")
                    
                    # Показываем историю клиента
                    client_history = get_client_history(df, client_id)
                    st.info(f"📋 История клиента {name} ({len(client_history)} посещений):")
                    
                    for _, visit in client_history.head(3).iterrows():
                        st.write(f"• {visit['Дата'][:16]} - {visit['Услуга']} ({visit['Цена']} руб.)")
                    
                    if len(client_history) > 3:
                        st.write(f"... и еще {len(client_history) - 3} посещений")
                
                # Добавляем новую запись (посещение)
                new_visit = {
                    "visit_id": visit_id,
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
                df = pd.concat([df, pd.DataFrame([new_visit])], ignore_index=True)
                
                save_data(df)
                st.success(f"✅ Посещение клиента {name} успешно сохранено!")
                
            else:
                st.error("❌ Пожалуйста, заполните обязательные поля (отмечены *)")

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
        with st.form("mailing_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                mailing_name = st.text_input("Имя*")
                study_place = st.text_input("Место учебы")
                
            with col2:
                vk_link = st.text_input("Ссылка VK")
                mailing_consent = st.radio("Согласие на рассылку*", ["Да", "Нет"])
            
            submitted_mailing = st.form_submit_button("💾 Сохранить контакт", use_container_width=True)
            
            if submitted_mailing:
                if mailing_name:
                    client_id = create_client_id(mailing_name, "")
                    visit_id = hashlib.md5(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_{mailing_name}_".encode()).hexdigest()
                    
                    new_mailing = {
                        "visit_id": visit_id,
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
                    st.success(f"✅ {mailing_name} добавлен в базу рассылки!")
                else:
                    st.error("❌ Пожалуйста, укажите имя")
    
    else:  # База контактов
        mailing_df = df[df["Направление"] == "Рассылка"]
        if not mailing_df.empty:
            st.dataframe(mailing_df[["Имя", "Место_учебы", "Ссылка_VK", "Согласие_рассылка"]])
            
            contacts_to_delete = st.multiselect(
                "Выберите контакты для удаления:",
                mailing_df["Имя"].unique()
            )
            
            if contacts_to_delete and st.button("🗑️ Удалить выбранные контакты", use_container_width=True):
                df = df[~((df["Направление"] == "Рассылка") & (df["Имя"].isin(contacts_to_delete)))]
                save_data(df)
                st.success(f"✅ Удалено {len(contacts_to_delete)} контактов!")
                st.rerun()
        else:
            st.info("📭 База рассылки пуста")

# --- АНАЛИТИКА ---
elif page == "Аналитика":
    st.title("📈 Аналитика")
    st.markdown("---")
    
    if not df.empty:
        # Статистика
        st.subheader("📊 Общая статистика")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_income = df[df['Направление'] != 'Рассылка']["Цена"].sum()
            st.metric("💰 Выручка", f"{total_income:,} ₽")
            
        with col2:
            total_clients = df[df['Направление'] != 'Рассылка']["Имя"].nunique()
            st.metric("👥 Клиентов", total_clients)
            
        with col3:
            total_services = len(df[df['Направление'] != 'Рассылка'])
            st.metric("📝 Услуг", total_services)
            
        with col4:
            filtered_df = df[df['Направление'] != 'Рассылка']
            avg_price = filtered_df["Цена"].mean() if len(filtered_df) > 0 else 0
            st.metric("💳 Средний чек", f"{avg_price:.0f} ₽")
        
        # Фильтры
        st.subheader("🔍 Фильтры")
        
        col1, col2 = st.columns(2)
        
        with col1:
            filter_direction = st.multiselect("Направление", df["Направление"].unique())
            filter_service = st.multiselect("Услуга", df["Услуга"].unique())
            
        with col2:
            min_price = st.number_input("Минимальная цена", 0, value=0)
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
        st.dataframe(filtered_df, use_container_width=True)
        
        # Управление клиентами
        st.subheader("🗑️ Управление клиентами")
        all_clients = filtered_df["Имя"].unique()
        
        if len(all_clients) > 0:
            clients_to_delete = st.multiselect("Выберите клиентов для удаления:", all_clients)
            
            if clients_to_delete and st.button("🗑️ Удалить выбранных клиентов", use_container_width=True):
                df = df[~df["Имя"].isin(clients_to_delete)]
                save_data(df)
                st.success(f"✅ Удалено {len(clients_to_delete)} клиентов!")
                st.rerun()
        
        # Экспорт
        st.subheader("📤 Экспорт данных")
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Скачать CSV",
            data=csv,
            file_name=f"marketing_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    else:
        st.info("📊 Данные появятся здесь после добавления клиентов")

# --- ИСТОРИЯ КЛИЕНТОВ ---
elif page == "История клиентов":
    st.title("📋 История клиентов")
    st.markdown("---")
    
    if not df.empty:
        # Выбор клиента для просмотра истории
        all_clients = sorted(df[df['Направление'] != 'Рассылка']['Имя'].unique())
        
        if all_clients:
            selected_client = st.selectbox("Выберите клиента для просмотра истории:", all_clients)
            
            if selected_client:
                # Находим client_id выбранного клиента
                client_data = df[df['Имя'] == selected_client]
                if not client_data.empty:
                    client_id = client_data.iloc[0]['client_id']
                    
                    # Получаем историю клиента
                    client_history = get_client_history(df, client_id)
                    
                    # Основная информация о клиенте
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        total_visits = len(client_history)
                        st.metric("📊 Всего посещений", total_visits)
                    
                    with col2:
                        total_spent = client_history['Цена'].sum()
                        st.metric("💰 Всего потрачено", f"{total_spent:,} ₽")
                    
                    with col3:
                        avg_spent = total_spent / total_visits if total_visits > 0 else 0
                        st.metric("💳 Средний чек", f"{avg_spent:.0f} ₽")
                    
                    st.markdown("---")
                    
                    # История посещений
                    st.subheader("📅 История посещений")
                    for _, visit in client_history.iterrows():
                        with st.container():
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.write(f"**{visit['Дата'][:16]}**")
                            with col2:
                                st.write(f"**{visit['Услуга']}**")
                            with col3:
                                st.write(f"**{visit['Цена']} ₽**")
                            
                            if visit['Направление'] == 'Учеба' and visit['Кто_пригласил']:
                                st.write(f"Пригласил: {visit['Кто_пригласил']}")
                            
                            st.markdown("---")
                else:
                    st.info("Клиент не найден в базе данных")
        else:
            st.info("📊 В базе данных пока нет клиентов")
    else:
        st.info("📊 Данные появятся здесь после добавления клиентов")

# --- JavaScript для автоматического скрытия сайдбара на телефоне ---
if is_mobile:
    st.markdown("""
    <script>
    // Автоматическое скрытие сайдбара после выбора пункта на мобильных
    setTimeout(function() {
        const sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.transform = "translateX(-100%)";
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)
