import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlalchemy as sa
import os
import json
from pathlib import Path

# 🔐 Basic authentication for dashboard
DASHBOARD_PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'mindanalyzer123')

def check_auth():
    if 'dashboard_authenticated' not in st.session_state:
        st.sidebar.header("🔐 Dashboard Access")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if password == DASHBOARD_PASSWORD:
                st.session_state.dashboard_authenticated = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect password")
        st.stop()
    return True

# Check authentication
check_auth()

# Translation dictionary
TRANSLATIONS = {
    "en": {
        "title": "🧠 MindAnalyzer Specialist Dashboard",
        "subtitle": "Analytics dashboard for mental health professionals",
        "filters": "Filters",
        "date_range": "Date range:",
        "sentiment": "Sentiment:",
        "all": "All",
        "overview": "📈 Overview Metrics",
        "total_records": "Total Records",
        "positive_sentiments": "Positive Sentiments",
        "avg_confidence": "Avg Confidence",
        "avg_text_length": "Avg Text Length",
        "visualizations": "📊 Data Visualizations",
        "sentiment_distribution": "Sentiment Distribution",
        "top_emotions": "Top 10 Emotions",
        "count": "Count",
        "emotion": "Emotion",
        "no_emotions": "No emotions detected in selected data",
        "timeline": "📅 Request Timeline",
        "date": "Date",
        "requests": "Number of Requests",
        "records": "📋 All Records",
        "detailed_view": "🔍 Detailed View",
        "select_record": "Select record to view details:",
        "original_text": "Original Text",
        "analysis_results": "Analysis Results",
        "emotions": "Emotions:",
        "distortions": "Cognitive Distortions:",
        "footer": "MindAnalyzer Dashboard v1.0 | For use by qualified professionals only",
        "language": "Language:",
        "none_detected": "None detected",
        "database_error": "Database error:",
        "no_data": "No data found for selected filters",
        "user_filter": "User:"
    },
    "ru": {
        "title": "🧠 MindAnalyzer Панель Специалиста",
        "subtitle": "Аналитическая панель для специалистов в области ментального здоровья",
        "filters": "Фильтры",
        "date_range": "Диапазон дат:",
        "sentiment": "Настроение:",
        "all": "Все",
        "overview": "📈 Общая статистика",
        "total_records": "Всего записей",
        "positive_sentiments": "Позитивных настроений",
        "avg_confidence": "Средняя уверенность",
        "avg_text_length": "Средняя длина текста",
        "visualizations": "📊 Визуализации",
        "sentiment_distribution": "Распределение настроений",
        "top_emotions": "Топ-10 эмоций",
        "count": "Количество",
        "emotion": "Эмоция",
        "no_emotions": "Эмоции не обнаружены в выбранных данных",
        "timeline": "📅 Временная шкала запросов",
        "date": "Дата",
        "requests": "Количество запросов",
        "records": "📋 Все записи",
        "detailed_view": "🔍 Детальный просмотр",
        "select_record": "Выберите запрос для детального просмотра:",
        "original_text": "Исходный текст",
        "analysis_results": "Результаты анализа",
        "emotions": "Эмоции:",
        "distortions": "Когнитивные искажения:",
        "footer": "MindAnalyzer Dashboard v1.0 | Для использования квалифицированными специалистами",
        "language": "Язык:",
        "none_detected": "Не обнаружено",
        "database_error": "Ошибка базы данных:",
        "no_data": "Нет данных для выбранных фильтров",
        "user_filter": "Пользователь:"
    }
}

# Initialize session state for language
if 'language' not in st.session_state:
    st.session_state.language = 'en'

def get_translation(key):
    """Get translation for current language"""
    return TRANSLATIONS[st.session_state.language].get(key, key)

def parse_json_column(json_str, default):
    """Safely parse JSON column with error handling"""
    try:
        if json_str and json_str != '[]':
            data = json.loads(json_str)
            return ', '.join(data) if isinstance(data, list) else default
        return default
    except json.JSONDecodeError:
        return default

def get_database_path():
    """Get database path from environment variable or use default development path"""
    env_path = os.getenv('DATABASE_URL')
    if env_path:
        return env_path
    
    base_dir = Path(__file__).parent.parent.parent
    db_file = base_dir / 'instance' / 'mental_health_analysis.db'
    
    db_file.parent.mkdir(exist_ok=True, parents=True)
    
    return f'sqlite:///{db_file}'

# Page configuration
st.set_page_config(
    page_title="MindAnalyzer | Specialist Dashboard",
    page_icon="🧠",
    layout="wide"
)

# Language selector in sidebar
st.sidebar.header(get_translation("language"))
language = st.sidebar.radio(
    "Language", ["English", "Русский"], 
    index=0 if st.session_state.language == 'en' else 1, 
    label_visibility="collapsed")
st.session_state.language = 'en' if language == "English" else 'ru'

# Database connection
@st.cache_resource
def get_db_engine():
    """Create and cache database engine"""
    db_path = get_database_path()
    return sa.create_engine(db_path)

engine = get_db_engine()

# Page header
st.title(get_translation("title"))
st.markdown(get_translation("subtitle"))

# Sidebar filters
st.sidebar.header(get_translation("filters"))
date_range = st.sidebar.date_input(
    get_translation("date_range"),
    value=(datetime.now().date() - timedelta(days=7), datetime.now().date())
)

sentiment_options = [get_translation('all'), 'positive', 'negative', 'neutral', 'mixed']
selected_sentiment = st.sidebar.selectbox(get_translation("sentiment"), sentiment_options)

# User selection filter
try:
    with engine.connect() as conn:
        users_df = pd.read_sql("SELECT id, username FROM users", conn)
    
    user_options = ["All Users"] + [f"{row['id']} - {row['username']}" for _, row in users_df.iterrows()]
    selected_user = st.sidebar.selectbox(get_translation("user_filter"), user_options)
    
except Exception as e:
    st.sidebar.warning("Could not load users list")
    selected_user = "All Users"

# Data loading
try:
    query = sa.text("""
        SELECT id, original_text, sentiment, confidence_score, emotions, distortions, created_at
        FROM analysis_results 
        WHERE DATE(created_at) BETWEEN :start_date AND :end_date
    """)
    
    params = {'start_date': date_range[0], 'end_date': date_range[1]}
    
    if selected_user != "All Users":
        user_id = int(selected_user.split(" - ")[0])
        query = sa.text(str(query) + " AND user_id = :user_id")
        params['user_id'] = user_id

    if selected_sentiment != get_translation('all'):
        query = sa.text(str(query) + " AND sentiment = :sentiment")
        params['sentiment'] = selected_sentiment

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
    
    if df.empty:
        st.warning(get_translation("no_data"))
        st.stop()
    
    # Parse JSON columns
    df['emotions'] = df['emotions'].apply(lambda x: parse_json_column(x, get_translation('none_detected')))
    df['distortions'] = df['distortions'].apply(lambda x: parse_json_column(x, get_translation('none_detected')))
    df['created_at'] = pd.to_datetime(df['created_at'])
    
except Exception as e:
    error_msg = f"{get_translation('database_error')} {e}"
    st.error(error_msg)
    st.stop()

# Metrics section
st.header(get_translation("overview"))
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(get_translation("total_records"), len(df))
with col2:
    positive_count = len(df[df['sentiment'] == 'positive'])
    st.metric(get_translation("positive_sentiments"), positive_count)
with col3:
    avg_confidence = df['confidence_score'].mean()
    st.metric(get_translation("avg_confidence"), f"{avg_confidence:.1%}")
with col4:
    avg_text_length = df['original_text'].str.len().mean()
    st.metric(get_translation("avg_text_length"), f"{avg_text_length:.0f} chars")

# Visualizations
st.header(get_translation("visualizations"))
viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    sentiment_counts = df['sentiment'].value_counts()
    fig_sentiment = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title=get_translation("sentiment_distribution"),
        color=sentiment_counts.index,
        color_discrete_map={
            'positive': '#2E8B57',
            'negative': '#DC143C', 
            'neutral': '#1E90FF',
            'mixed': '#FF8C00'
        }
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)

with viz_col2:
    all_emotions = []
    for emotions_str in df['emotions']:
        if emotions_str != get_translation('none_detected'):
            all_emotions.extend([e.strip() for e in emotions_str.split(',')])
    
    if all_emotions:
        emotion_counts = pd.Series(all_emotions).value_counts().head(10)
        fig_emotions = px.bar(
            x=emotion_counts.values,
            y=emotion_counts.index,
            orientation='h',
            title=get_translation("top_emotions"),
            labels={'x': get_translation("count"), 'y': get_translation("emotion")}
        )
        st.plotly_chart(fig_emotions, use_container_width=True)
    else:
        st.info(get_translation("no_emotions"))

# Timeline chart
st.subheader(get_translation("timeline"))
df['date'] = df['created_at'].dt.date
timeline_data = df['date'].value_counts().sort_index()
fig_timeline = px.line(
    x=timeline_data.index,
    y=timeline_data.values,
    title=get_translation("timeline"),
    labels={'x': get_translation("date"), 'y': get_translation("requests")}
)
st.plotly_chart(fig_timeline, use_container_width=True)

# Data table
st.header(get_translation("records"))
st.dataframe(
    df[['created_at', 'sentiment', 'confidence_score', 'emotions', 'distortions']],
    use_container_width=True,
    hide_index=True
)

# Detailed view
st.header(get_translation("detailed_view"))
selected_id = st.selectbox(get_translation("select_record"), df['id'])

if selected_id:
    selected_record = df[df['id'] == selected_id].iloc[0]
    
    st.subheader(get_translation("original_text"))
    st.write(selected_record['original_text'])
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("Sentiment" if st.session_state.language == 'en' else "Настроение", selected_record['sentiment'])
    with col_b:
        st.metric("Confidence" if st.session_state.language == 'en' else "Уверенность", f"{selected_record['confidence_score']:.1%}")
    with col_c:
        st.metric("Date" if st.session_state.language == 'en' else "Дата", selected_record['created_at'].strftime("%Y-%m-%d %H:%M"))
    
    st.subheader(get_translation("analysis_results"))
    st.write(f"**{get_translation('emotions')}** {selected_record['emotions']}")
    st.write(f"**{get_translation('distortions')}** {selected_record['distortions']}")

# Footer
st.markdown("---")
st.caption(get_translation("footer"))