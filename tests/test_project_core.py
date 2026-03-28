import pandas as pd

import analytics
import preprocessor


def sample_chat_text() -> str:
    return (
        "27/03/26, 9:00 am - Alice: Good morning team\n"
        "27/03/26, 9:05 am - Bob: That is awesome\n"
        "27/03/26, 9:06 am - Alice: <Media omitted>\n"
        "27/03/26, 9:10 am - Bob: bad internet today\n"
        "27/03/26, 9:15 am - Messages and calls are end-to-end encrypted.\n"
    )


def test_preprocess_creates_required_columns() -> None:
    df = preprocessor.preprocess(sample_chat_text())
    expected = {
        "date", "user", "message", "only_date", "year", "month_num",
        "month", "day", "day_name", "hour", "minute", "period",
    }
    assert expected.issubset(df.columns)
    assert len(df) == 5


def test_fetch_stats_overall() -> None:
    df = preprocessor.preprocess(sample_chat_text())
    num_messages, total_words, media_count, links_count = analytics.fetch_stats("Overall", df)
    assert num_messages == 5
    assert total_words > 0
    assert media_count == 1
    assert links_count == 0


def test_sentiment_over_time_returns_expected_shape() -> None:
    df = preprocessor.preprocess(sample_chat_text())
    sentiment_df = analytics.sentiment_over_time("Overall", df)
    assert not sentiment_df.empty
    assert {"only_date", "positive", "neutral", "negative"}.issubset(sentiment_df.columns)


def test_anomaly_detection_small_data_has_flags() -> None:
    df = preprocessor.preprocess(sample_chat_text())
    out = analytics.detect_message_anomalies("Overall", df)
    assert "anomaly" in out.columns
    assert "anomaly_score" in out.columns


def test_decomposition_small_data_returns_empty() -> None:
    df = preprocessor.preprocess(sample_chat_text())
    out = analytics.decompose_daily_messages("Overall", df)
    assert isinstance(out, pd.DataFrame)
