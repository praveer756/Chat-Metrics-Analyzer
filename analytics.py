"""Analytics functions for WhatsApp chat data analysis.

Provides statistical analysis, text processing, and visualization 
helper functions for WhatsApp chat data.
"""

import logging
from collections import Counter
from typing import Any

import pandas as pd
import numpy as np
from wordcloud import WordCloud
from urlextract import URLExtract
import emoji

import config

logger = logging.getLogger(__name__)
extract = URLExtract()

POSITIVE_WORDS = {
    "good", "great", "awesome", "nice", "love", "happy", "excellent",
    "amazing", "best", "cool", "thanks", "thank", "wonderful", "fun"
}
NEGATIVE_WORDS = {
    "bad", "sad", "hate", "angry", "worst", "terrible", "poor",
    "awful", "upset", "issue", "problem", "annoying", "boring"
}


def _load_stopwords(stopwords_file: str = config.STOPWORDS_FILE) -> set[str]:
    """Load stopwords from file.
    
    Args:
        stopwords_file: Path to stopwords file.
        
    Returns:
        Set of stopwords.
        
    Raises:
        FileNotFoundError: If stopwords file not found.
    """
    try:
        with open(stopwords_file, 'r', encoding='utf-8') as f:
            return set(f.read().split('\n'))
    except FileNotFoundError:
        logger.warning(f"Stopwords file not found: {stopwords_file}")
        return set()


def fetch_stats(selected_user: str, df: pd.DataFrame) -> tuple[int, int, int, int]:
    """Fetch basic chat statistics for a user.
    
    Args:
        selected_user: User name or "Overall" for all users.
        df: Preprocessed chat DataFrame.
        
    Returns:
        Tuple of (total_messages, total_words, media_messages, links_shared).
    """
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    
    num_messages = user_df.shape[0]
    
    # Count total words
    words_list = []
    for message in user_df['message']:
        words_list.extend(str(message).split())
    total_words = len(words_list)
    
    # Count media messages
    num_media_messages = (user_df['message'] == config.MEDIA_OMITTED_MARKER).sum()
    
    # Count links
    links_list = []
    for message in user_df['message']:
        links_list.extend(extract.find_urls(str(message)))
    total_links = len(links_list)
    
    logger.debug(f"Stats for {selected_user}: {num_messages} msgs, {total_words} words")
    return num_messages, total_words, num_media_messages, total_links


def most_busy_users(df: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    msg_counts = df['user'].value_counts().head()

    counts = df['user'].value_counts()
    percentage_df = ((counts / df.shape[0]) * 100).round(2).reset_index()
    percentage_df.columns = ['name', 'percent']

    logger.debug(f"Most busy user: {percentage_df.iloc[0]['name']}")
    return msg_counts, percentage_df


def create_wordcloud(selected_user: str, df: pd.DataFrame) -> WordCloud:
    """Generate a wordcloud for messages after removing stopwords.
    
    Args:
        selected_user: User name or "Overall" for all users.
        df: Preprocessed chat DataFrame.
        
    Returns:
        WordCloud object.
    """
    stop_words = _load_stopwords()
    
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    
    # Filter out system messages and media
    temp = user_df[user_df['user'] != config.GROUP_NOTIFICATION_MARKER]
    temp = temp[temp['message'] != config.MEDIA_OMITTED_MARKER]
    
    if temp.empty:
        logger.warning(f"No valid messages for wordcloud for {selected_user}")
        return WordCloud(width=config.WORDCLOUD_WIDTH, height=config.WORDCLOUD_HEIGHT)
    
    def remove_stop_words(message: str) -> str:
        """Remove stopwords from message."""
        words = [
            word for word in str(message).lower().split()
            if word not in stop_words and word.strip()
        ]
        return " ".join(words)
    
    temp_copy = temp.copy()
    temp_copy['message'] = temp_copy['message'].apply(remove_stop_words)
    
    wc = WordCloud(
        width=config.WORDCLOUD_WIDTH,
        height=config.WORDCLOUD_HEIGHT,
        min_font_size=config.WORDCLOUD_MIN_FONT,
        background_color=config.WORDCLOUD_BG_COLOR
    )
    wc.generate(" ".join(temp_copy['message'].astype(str)))
    
    logger.debug(f"Wordcloud generated for {selected_user}")
    return wc


def most_common_words(selected_user: str, df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Get most common words used by a user.
    
    Args:
        selected_user: User name or "Overall" for all users.
        df: Preprocessed chat DataFrame.
        top_n: Number of top words to return.
        
    Returns:
        DataFrame with top N most common words and their counts.
    """
    stop_words = _load_stopwords()
    
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    
    # Filter out system messages and media
    temp = user_df[user_df['user'] != config.GROUP_NOTIFICATION_MARKER]
    temp = temp[temp['message'] != config.MEDIA_OMITTED_MARKER]
    
    words = []
    for message in temp['message']:
        for word in str(message).lower().split():
            if word not in stop_words and word.strip():
                words.append(word)
    
    if not words:
        logger.warning(f"No words found for {selected_user}")
        return pd.DataFrame()
    
    most_common_df = pd.DataFrame(Counter(words).most_common(top_n))
    most_common_df.columns = ['word', 'count']
    
    logger.debug(f"Top {top_n} words extracted for {selected_user}")
    return most_common_df


def emoji_helper(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """Get most common emojis used by a user.
    
    Args:
        selected_user: User name or "Overall" for all users.
        df: Preprocessed chat DataFrame.
        
    Returns:
        DataFrame with emojis and their counts.
    """
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    
    emojis = []
    for message in user_df['message']:
        emojis.extend([c for c in str(message) if c in emoji.EMOJI_DATA])
    
    if not emojis:
        logger.info(f"No emojis found for {selected_user}")
        return pd.DataFrame()
    
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    emoji_df.columns = ['emoji', 'count']
    
    logger.debug(f"Emoji analysis completed for {selected_user}: {len(emoji_df)} unique emojis")
    return emoji_df


def monthly_timeline(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """Get monthly message timeline.
    
    Args:
        selected_user: User name or "Overall" for all users.
        df: Preprocessed chat DataFrame.
        
    Returns:
        DataFrame with time periods and message counts.
    """
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    
    timeline = user_df.groupby(['year', 'month_num', 'month']).size().reset_index(name='message')
    
    # Create readable time labels
    timeline['time'] = timeline.apply(
        lambda row: f"{row['month']}-{row['year']}", axis=1
    )
    
    logger.debug(f"Monthly timeline generated for {selected_user}: {len(timeline)} months")
    return timeline


def daily_timeline(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """Get daily message timeline.
    
    Args:
        selected_user: User name or "Overall" for all users.
        df: Preprocessed chat DataFrame.
        
    Returns:
        DataFrame with dates and daily message counts.
    """
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    
    daily_df = user_df.groupby('only_date').size().reset_index(name='message')
    
    logger.debug(f"Daily timeline generated for {selected_user}: {len(daily_df)} days")
    return daily_df


def week_activity_map(selected_user: str, df: pd.DataFrame) -> pd.Series:
    """Get message distribution by day of week.
    
    Args:
        selected_user: User name or "Overall" for all users.
        df: Preprocessed chat DataFrame.
        
    Returns:
        Series with day names and message counts.
    """
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    
    return user_df['day_name'].value_counts()


def month_activity_map(selected_user: str, df: pd.DataFrame) -> pd.Series:
    """Get message distribution by month.
    
    Args:
        selected_user: User name or "Overall" for all users.
        df: Preprocessed chat DataFrame.
        
    Returns:
        Series with month names and message counts.
    """
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    
    return user_df['month'].value_counts()


def activity_heatmap(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """Get activity heatmap by day and hour.
    
    Args:
        selected_user: User name or "Overall" for all users.
        df: Preprocessed chat DataFrame.
        
    Returns:
        DataFrame with day/period activity matrix.
    """
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    
    heatmap = user_df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)
    
    logger.debug(f"Activity heatmap generated for {selected_user}")
    return heatmap


def _filter_user_messages(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """Filter out non-user/media messages and apply user selection.

    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.

    Returns:
        Filtered DataFrame with clean message rows.
    """
    user_df = df if selected_user == 'Overall' else df[df['user'] == selected_user]
    user_df = user_df[user_df['user'] != config.GROUP_NOTIFICATION_MARKER]
    user_df = user_df[user_df['message'] != config.MEDIA_OMITTED_MARKER]
    return user_df.copy()


def _heuristic_sentiment_label(text: str) -> str:
    """Classify sentiment using a lightweight keyword heuristic.

    Args:
        text: Input message text.

    Returns:
        Sentiment label: positive, neutral, or negative.
    """
    tokens = {token.strip(".,!?;:\"'()[]{}").lower() for token in text.split()}
    pos_score = len(tokens & POSITIVE_WORDS)
    neg_score = len(tokens & NEGATIVE_WORDS)
    if pos_score > neg_score:
        return "positive"
    if neg_score > pos_score:
        return "negative"
    return "neutral"


def sentiment_over_time(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """Compute sentiment distribution by day for selected user scope.

    Tries transformer-based sentiment first (if transformers is available);
    otherwise falls back to a deterministic keyword heuristic.

    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.

    Returns:
        DataFrame with only_date and sentiment counts.
    """
    temp = _filter_user_messages(selected_user, df)
    if temp.empty:
        return pd.DataFrame(columns=["only_date", "positive", "neutral", "negative"])

    sentiment_labels: list[str] = []
    used_transformer = False

    try:
        from transformers import pipeline  # type: ignore

        classifier = pipeline(
            "sentiment-analysis",
            model=config.DEFAULT_SENTIMENT_MODEL,
            truncation=True,
        )
        chunks = temp['message'].astype(str).tolist()
        results = classifier(chunks, batch_size=32)
        for item in results:
            if isinstance(item, dict):
                label = str(item.get("label", "NEUTRAL")).lower()
            else:
                label = "neutral"
            sentiment_labels.append("positive" if "pos" in label else "negative")
        used_transformer = True
    except Exception as exc:  # pragma: no cover - fallback path for offline envs
        logger.info(f"Transformers sentiment unavailable, using heuristic fallback: {exc}")
        sentiment_labels = [_heuristic_sentiment_label(text) for text in temp['message'].astype(str)]

    temp['sentiment'] = sentiment_labels
    sentiment_daily = (
        temp.groupby(['only_date', 'sentiment'])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    for col in ["positive", "neutral", "negative"]:
        if col not in sentiment_daily.columns:
            sentiment_daily[col] = 0

    sentiment_daily = sentiment_daily[["only_date", "positive", "neutral", "negative"]]
    logger.debug(
        "Sentiment analysis completed for %s using %s",
        selected_user,
        "transformers" if used_transformer else "heuristic",
    )
    return sentiment_daily


def detect_message_anomalies(
    selected_user: str,
    df: pd.DataFrame,
    contamination: float = config.DEFAULT_ANOMALY_CONTAMINATION,
) -> pd.DataFrame:
    """Detect anomalous daily message volume using Isolation Forest.

    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.
        contamination: Expected outlier fraction in range [0.01, 0.20].

    Returns:
        DataFrame with daily volume, anomaly flag, and anomaly score.
    """
    from sklearn.ensemble import IsolationForest

    timeline = daily_timeline(selected_user, df)
    if timeline.empty or len(timeline) < 14:
        timeline['anomaly'] = 0
        timeline['anomaly_score'] = 0.0
        return timeline

    safe_contamination = float(np.clip(contamination, config.MIN_ANOMALY_CONTAMINATION, config.MAX_ANOMALY_CONTAMINATION))

    model = IsolationForest(
        contamination=safe_contamination,
        random_state=42,
        n_estimators=200,
    )
    X = timeline[['message']].astype(float)
    preds = model.fit_predict(X)
    scores = model.decision_function(X)

    result = timeline.copy()
    result['anomaly'] = (preds == -1).astype(int)
    result['anomaly_score'] = scores
    logger.debug(
        "Anomaly detection completed for %s with %s anomalies",
        selected_user,
        int(result['anomaly'].sum()),
    )
    return result


def decompose_daily_messages(selected_user: str, df: pd.DataFrame) -> pd.DataFrame:
    """Decompose daily message counts into trend/seasonality/residual.

    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.

    Returns:
        DataFrame with decomposition components; empty if not enough data.
    """
    from statsmodels.tsa.seasonal import seasonal_decompose

    timeline = daily_timeline(selected_user, df)
    if timeline.empty or len(timeline) < 21:
        return pd.DataFrame()

    ts = timeline.copy()
    ts['only_date'] = pd.to_datetime(ts['only_date'])
    ts = ts.set_index('only_date').asfreq('D', fill_value=0)

    try:
        decomposition = seasonal_decompose(ts['message'], model='additive', period=7)
    except Exception as exc:
        logger.warning(f"Time-series decomposition failed: {exc}")
        return pd.DataFrame()

    output = pd.DataFrame({
        'only_date': ts.index,
        'observed': decomposition.observed.values,
        'trend': decomposition.trend.values,
        'seasonal': decomposition.seasonal.values,
        'resid': decomposition.resid.values,
    }).dropna()

    logger.debug("Time-series decomposition completed for %s", selected_user)
    return output
