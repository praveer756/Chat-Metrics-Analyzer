"""Chat Metrics Analyzer - Main Streamlit Application.

Interactive dashboard for analyzing WhatsApp chat exports and extracting insights
about user behavior, communication patterns, and message statistics.
"""

import logging
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

import config
import preprocessor
import analytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Chat Metrics Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_data(ttl=config.CACHE_TTL_SECONDS)
def load_and_preprocess(file_content: str) -> pd.DataFrame:
    """Load and preprocess chat data with caching.
    
    Args:
        file_content: Raw file content as string.
        
    Returns:
        Preprocessed DataFrame.
    """
    try:
        df = preprocessor.preprocess(file_content)
        preprocessor.validate_dataframe(df)
        logger.info(f"Successfully loaded {len(df)} messages")
        return df
    except ValueError as e:
        logger.error(f"Preprocessing error: {e}")
        raise


def display_statistics(selected_user: str, df: pd.DataFrame) -> None:
    """Display top statistics for selected user.
    
    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.
    """
    num_messages, words, num_media_messages, num_links = analytics.fetch_stats(selected_user, df)
    
    st.subheader("📊 Top Statistics")
    col1, col2, col3, col4 = st.columns(config.STATS_COLUMNS)
    
    with col1:
        st.metric("Total Messages", num_messages)
    with col2:
        st.metric("Total Words", words)
    with col3:
        st.metric("Media Shared", num_media_messages)
    with col4:
        st.metric("Links Shared", num_links)


def display_timelines(selected_user: str, df: pd.DataFrame) -> None:
    """Display message timelines.
    
    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.
    """
    st.subheader("📈 Message Timelines")
    
    # Monthly timeline
    timeline = analytics.monthly_timeline(selected_user, df)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(timeline['time'], timeline['message'], marker='o', color='green', linewidth=2)
    ax.set_title("Monthly Message Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Messages")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    
    # Daily timeline
    daily = analytics.daily_timeline(selected_user, df)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(daily['only_date'], daily['message'], marker='.', color='blue', linewidth=1, alpha=0.7)
    ax.set_title("Daily Message Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Messages")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)


def display_activity_maps(selected_user: str, df: pd.DataFrame) -> None:
    """Display activity maps by day and month.
    
    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.
    """
    st.subheader("🔥 Activity Analysis")
    
    col1, col2 = st.columns(config.ACTIVITY_MAP_COLUMNS)
    
    with col1:
        st.write("**Most Active Day of Week**")
        busy_day = analytics.week_activity_map(selected_user, df)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(busy_day.index.tolist(), np.asarray(busy_day.values, dtype=float), color='skyblue', edgecolor='black')
        ax.set_title("Messages by Day")
        ax.set_xlabel("Day")
        ax.set_ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.write("**Most Active Month**")
        busy_month = analytics.month_activity_map(selected_user, df)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(busy_month.index.tolist(), np.asarray(busy_month.values, dtype=float), color='orange', edgecolor='black')
        ax.set_title("Messages by Month")
        ax.set_xlabel("Month")
        ax.set_ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)


def display_heatmap(selected_user: str, df: pd.DataFrame) -> None:
    """Display activity heatmap.
    
    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.
    """
    st.subheader("🌡️ Weekly Activity Heatmap")
    
    user_heatmap = analytics.activity_heatmap(selected_user, df)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(user_heatmap, cmap='YlOrRd', annot=True, fmt='.0f', cbar_kws={'label': 'Messages'})
    ax.set_title("Message Activity by Day and Hour")
    plt.tight_layout()
    st.pyplot(fig)


def display_most_busy_users(df: pd.DataFrame) -> None:
    """Display most active users in group.
    
    Args:
        df: Preprocessed DataFrame.
    """
    st.subheader("👥 Most Active Users")
    
    msg_counts, percentage_df = analytics.most_busy_users(df)
    
    col1, col2 = st.columns(config.ACTIVITY_MAP_COLUMNS)
    
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(msg_counts.index.tolist(), np.asarray(msg_counts.values, dtype=float), color='red', edgecolor='black')
        ax.set_title("Messages by User")
        ax.set_xlabel("User")
        ax.set_ylabel("Count")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.write("**User Contribution Percentage**")
        st.dataframe(percentage_df, use_container_width=True)


def display_wordcloud(selected_user: str, df: pd.DataFrame) -> None:
    """Display wordcloud visualization.
    
    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.
    """
    st.subheader("☁️ Word Cloud")
    
    try:
        word_cloud = analytics.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.imshow(word_cloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Could not generate wordcloud: {e}")
        logger.error(f"Wordcloud error: {e}")


def display_phase2_ai_insights(selected_user: str, df: pd.DataFrame) -> None:
    """Display Phase 2 AI/ML insights.

    Args:
        selected_user: User name or "Overall".
        df: Preprocessed DataFrame.
    """
    st.header("🤖 AI Insights (Phase 2)")
    tab1, tab2, tab3 = st.tabs([
        "Sentiment Trend",
        "Anomaly Detection",
        "Time-Series Decomposition",
    ])

    with tab1:
        st.write("Daily positive/neutral/negative message trend.")
        sentiment_df = analytics.sentiment_over_time(selected_user, df)
        if sentiment_df.empty:
            st.info("Not enough message data for sentiment analysis.")
        else:
            fig, ax = plt.subplots(figsize=(11, 4))
            ax.plot(sentiment_df['only_date'], sentiment_df['positive'], label='Positive', color='green')
            ax.plot(sentiment_df['only_date'], sentiment_df['neutral'], label='Neutral', color='gray')
            ax.plot(sentiment_df['only_date'], sentiment_df['negative'], label='Negative', color='red')
            ax.set_title("Sentiment Trend Over Time")
            ax.set_xlabel("Date")
            ax.set_ylabel("Messages")
            ax.legend()
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)

    with tab2:
        st.write("Flag unusual spikes/dips in daily message volume using Isolation Forest.")
        contamination = st.slider(
            "Anomaly sensitivity (expected anomaly rate)",
            min_value=float(config.MIN_ANOMALY_CONTAMINATION),
            max_value=float(config.MAX_ANOMALY_CONTAMINATION),
            value=float(config.DEFAULT_ANOMALY_CONTAMINATION),
            step=0.01,
        )
        anomaly_df = analytics.detect_message_anomalies(selected_user, df, contamination=contamination)
        if anomaly_df.empty:
            st.info("Not enough data points for anomaly detection.")
        else:
            fig, ax = plt.subplots(figsize=(11, 4))
            ax.plot(anomaly_df['only_date'], anomaly_df['message'], color='navy', label='Daily messages')
            anomalies = anomaly_df[anomaly_df['anomaly'] == 1]
            if not anomalies.empty:
                ax.scatter(
                    anomalies['only_date'],
                    anomalies['message'],
                    color='crimson',
                    s=40,
                    label='Anomaly',
                    zorder=5,
                )
            ax.set_title("Daily Message Volume with Detected Anomalies")
            ax.set_xlabel("Date")
            ax.set_ylabel("Messages")
            ax.legend()
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
            st.caption(f"Detected anomalies: {int(anomaly_df['anomaly'].sum())}")

    with tab3:
        st.write("Decompose daily chat activity into trend, weekly seasonality, and residual noise.")
        decomposition_df = analytics.decompose_daily_messages(selected_user, df)
        if decomposition_df.empty:
            st.info("Need at least 3 weeks of daily data for stable decomposition.")
        else:
            fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
            axes[0].plot(decomposition_df['only_date'], decomposition_df['trend'], color='teal')
            axes[0].set_title("Trend")
            axes[1].plot(decomposition_df['only_date'], decomposition_df['seasonal'], color='purple')
            axes[1].set_title("Seasonality")
            axes[2].plot(decomposition_df['only_date'], decomposition_df['resid'], color='orange')
            axes[2].set_title("Residual")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)


# Main application
def main() -> None:
    """Main application entry point."""
    st.title(config.SIDEBAR_TITLE)
    st.markdown("Analyze WhatsApp chat exports to extract insights about communication patterns.")
    
    # Sidebar
    st.sidebar.title(config.SIDEBAR_TITLE)
    uploaded_file = st.sidebar.file_uploader(config.FILE_UPLOADER_LABEL, type=['txt'])
    
    if uploaded_file is not None:
        try:
            # Load and preprocess data
            bytes_data = uploaded_file.getvalue()
            data = bytes_data.decode("utf-8")
            df = load_and_preprocess(data)
            
            # Display preprocessed data
            with st.expander("📋 View Raw Data"):
                st.dataframe(df, use_container_width=True)
            
            # User selection
            user_list = sorted(df['user'].unique().tolist())
            if config.GROUP_NOTIFICATION_MARKER in user_list:
                user_list.remove(config.GROUP_NOTIFICATION_MARKER)
            user_list.insert(0, "Overall")
            
            selected_user = st.sidebar.selectbox("Analyze for:", user_list)
            if selected_user is None:
                st.warning("Please select a user to continue.")
                return
            
            # Show analysis button
            if st.sidebar.button(config.BUTTON_LABEL, use_container_width=True):
                logger.info(f"Generating analysis for {selected_user}")
                
                display_statistics(selected_user, df)
                display_timelines(selected_user, df)
                display_activity_maps(selected_user, df)
                display_heatmap(selected_user, df)
                
                # Show group-level insights when viewing overall
                if selected_user == "Overall":
                    display_most_busy_users(df)
                
                display_wordcloud(selected_user, df)
                display_phase2_ai_insights(selected_user, df)
                
                st.success("✅ Analysis complete!")
        
        except ValueError as e:
            st.error(f"❌ Error processing file: {e}")
            logger.error(f"File processing error: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            logger.error(f"Unexpected error: {e}")
    
    else:
        st.info("👈 Upload a WhatsApp chat export to begin. Export your chat as TXT format.")


if __name__ == "__main__":
    main()
