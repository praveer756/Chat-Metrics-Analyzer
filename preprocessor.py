"""WhatsApp chat data preprocessing module.

This module handles parsing and preprocessing WhatsApp chat exports
into a structured pandas DataFrame with temporal and user information.
"""

import re
import logging
import pandas as pd
import config

logger = logging.getLogger(__name__)


def preprocess(data: str) -> pd.DataFrame:
    """Parse and preprocess WhatsApp chat export data.
    
    Converts raw WhatsApp export text into a structured DataFrame with
    extracted temporal features, user names, and message content.
    Supports standard WhatsApp export format: [date, time] - user: message
    
    Args:
        data: Raw WhatsApp chat export as a string.
        
    Returns:
        pd.DataFrame: Preprocessed chat data with columns:
            - date: datetime of message
            - user: sender name
            - message: message content
            - only_date: date only (for grouping)
            - year, month_num, month: temporal breakdowns
            - day, day_name: day information
            - hour, minute: time components
            - period: hour range (e.g., "14-15")
            
    Raises:
        ValueError: If data format is invalid or no messages found.
        
    Example:
        >>> df = preprocess(export_text)
        >>> print(df.shape[0], "messages parsed")
    """
    if not isinstance(data, str) or not data.strip():
        logger.error("Invalid input: data must be non-empty string")
        raise ValueError("Input data cannot be empty")
    
    # Extract messages and dates using regex
    messages = re.split(config.WHATSAPP_DATE_PATTERN, data)[1:]
    dates = re.findall(config.WHATSAPP_DATE_PATTERN, data)
    
    if not messages or not dates:
        logger.error("No messages found matching WhatsApp format")
        raise ValueError("Could not parse WhatsApp export format. Check file format.")
    
    if len(messages) != len(dates):
        logger.warning(f"Message count ({len(messages)}) != date count ({len(dates)})")
        messages = messages[:len(dates)]
    
    # Clean dates (handle special Unicode space character)
    dates = [date.replace('\u202f', ' ') for date in dates]
    
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    
    # Convert to datetime
    df['message_date'] = pd.to_datetime(dates, format='%d/%m/%y, %I:%M %p - ', dayfirst=True)
    df.rename(columns={'message_date': 'date'}, inplace=True)
    
    # Extract user and message content
    users: list[str] = []
    message_list: list[str] = []
    
    for message in df['user_message']:
        entry = re.split(config.WHATSAPP_USER_PATTERN, message)
        if entry[1:]:  # User name found
            users.append(entry[1])
            message_list.append(entry[2])
        else:  # System message (no user)
            users.append(config.GROUP_NOTIFICATION_MARKER)
            message_list.append(entry[0])
    
    df['user'] = users
    df['message'] = message_list
    df.drop(columns=['user_message'], inplace=True)
    
    # Extract temporal features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    
    # Create period (hour range)
    period: list[str] = []
    for hour in df['hour']:
        if hour == 23:
            period.append(f"{hour}-00")
        elif hour == 0:
            period.append(f"00-{hour + 1}")
        else:
            period.append(f"{hour}-{hour + 1}")
    
    df['period'] = period
    
    logger.info(f"Successfully preprocessed {len(df)} messages from {len(df['user'].unique())} users")
    return df


def validate_dataframe(df: pd.DataFrame) -> None:
    """Validate that preprocessed DataFrame has required structure.
    
    Args:
        df: DataFrame to validate.
        
    Raises:
        ValueError: If required columns are missing or DataFrame is empty.
    """
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    missing_cols = config.REQUIRED_DATAFRAME_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    logger.debug(f"DataFrame validation passed: {df.shape[0]} rows, {df.shape[1]} columns")