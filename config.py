"""Configuration and constants for Chat Metrics Analyzer."""

# File Processing
STOPWORDS_FILE = "stop_hinglish.txt"
WHATSAPP_DATE_PATTERN = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{1,2}\s*[ap]m\s-\s'
WHATSAPP_USER_PATTERN = r'([\w\W]+?):\s'
MEDIA_OMITTED_MARKER = '<Media omitted>\n'
GROUP_NOTIFICATION_MARKER = 'group_notification'

# Streamlit Configuration
SIDEBAR_TITLE = "Chat Metrics Analyzer"
FILE_UPLOADER_LABEL = "Choose a file"
BUTTON_LABEL = "Show Analysis"

# Visualization Configuration
FIGURE_DPI = 100
WORDCLOUD_WIDTH = 500
WORDCLOUD_HEIGHT = 500
WORDCLOUD_MIN_FONT = 10
WORDCLOUD_BG_COLOR = 'white'

# UI Layout
STATS_COLUMNS = 4
ACTIVITY_MAP_COLUMNS = 2
HEATMAP_FIGSIZE_WIDTH = 10
HEATMAP_FIGSIZE_HEIGHT = 6

# Caching Configuration
CACHE_TTL_SECONDS = 3600  # 1 hour

# Data Validation
MIN_MESSAGES = 1
REQUIRED_DATAFRAME_COLUMNS = {'date', 'user', 'message', 'only_date', 'year', 'month_num', 'month', 'day', 'day_name', 'hour', 'minute', 'period'}

# Phase 2 - AI/ML
DEFAULT_ANOMALY_CONTAMINATION = 0.05
MIN_ANOMALY_CONTAMINATION = 0.01
MAX_ANOMALY_CONTAMINATION = 0.20
DEFAULT_SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
