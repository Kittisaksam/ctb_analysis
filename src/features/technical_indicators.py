"""
Technical indicators for financial data
"""
import pandas as pd
import numpy as np
from typing import Optional


def calculate_sma(
    df: pd.DataFrame,
    column: str = 'close',
    window: int = 20,
    column_name: Optional[str] = None
) -> pd.DataFrame:
    """
    คำนวณ Simple Moving Average (SMA)

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มีข้อมูลราคา
    column : str
        ชื่อ column ที่ต้องการคำนวณ
    window : int
        ขนาดของ window
    column_name : str, optional
        ชื่อ column ใหม่ (ถ้าไม่ระบุจะใช้ SMA_{window})

    Returns:
    --------
    pd.DataFrame
        DataFrame พร้อม SMA column ใหม่
    """
    if column_name is None:
        column_name = f'SMA_{window}'

    df[column_name] = df[column].rolling(window=window).mean()

    return df


def calculate_ema(
    df: pd.DataFrame,
    column: str = 'close',
    span: int = 20,
    column_name: Optional[str] = None
) -> pd.DataFrame:
    """
    คำนวณ Exponential Moving Average (EMA)

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มีข้อมูลราคา
    column : str
        ชื่อ column ที่ต้องการคำนวณ
    span : int
        span สำหรับ EMA
    column_name : str, optional
        ชื่อ column ใหม่

    Returns:
    --------
    pd.DataFrame
        DataFrame พร้อม EMA column ใหม่
    """
    if column_name is None:
        column_name = f'EMA_{span}'

    df[column_name] = df[column].ewm(span=span, adjust=False).mean()

    return df


def calculate_rsi(
    df: pd.DataFrame,
    column: str = 'close',
    period: int = 14,
    column_name: Optional[str] = None
) -> pd.DataFrame:
    """
    คำนวณ Relative Strength Index (RSI)

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มีข้อมูลราคา
    column : str
        ชื่อ column ที่ต้องการคำนวณ
    period : int
        ช่วงเวลาสำหรับคำนวณ RSI
    column_name : str, optional
        ชื่อ column ใหม่

    Returns:
    --------
    pd.DataFrame
        DataFrame พร้อม RSI column ใหม่
    """
    if column_name is None:
        column_name = f'RSI_{period}'

    # คำนวณการเปลี่ยนแปลงของราคา
    delta = df[column].diff()

    # แยกกำไรและขาดทุน
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # คำนวณค่าเฉลี่ย
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # คำนวณ RS และ RSI
    rs = avg_gain / avg_loss
    df[column_name] = 100 - (100 / (1 + rs))

    return df


def calculate_macd(
    df: pd.DataFrame,
    column: str = 'close',
    fast: int = 12,
    slow: int = 26,
    signal: int = 9
) -> pd.DataFrame:
    """
    คำนวณ Moving Average Convergence Divergence (MACD)

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มีข้อมูลราคา
    column : str
        ชื่อ column ที่ต้องการคำนวณ
    fast : int
        ช่วงเวลาสำหรับ fast EMA
    slow : int
        ช่วงเวลาสำหรับ slow EMA
    signal : int
        ช่วงเวลาสำหรับ signal line

    Returns:
    --------
    pd.DataFrame
        DataFrame พร้อม MACD, Signal, และ Histogram columns
    """
    # คำนวณ EMA
    ema_fast = df[column].ewm(span=fast, adjust=False).mean()
    ema_slow = df[column].ewm(span=slow, adjust=False).mean()

    # คำนวณ MACD
    df['MACD'] = ema_fast - ema_slow

    # คำนวณ Signal line
    df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()

    # คำนวณ Histogram
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    return df


def calculate_bollinger_bands(
    df: pd.DataFrame,
    column: str = 'close',
    window: int = 20,
    num_std: float = 2.0
) -> pd.DataFrame:
    """
    คำนวณ Bollinger Bands

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มีข้อมูลราคา
    column : str
        ชื่อ column ที่ต้องการคำนวณ
    window : int
        ขนาดของ window
    num_std : float
        จำนวน standard deviations

    Returns:
    --------
    pd.DataFrame
        DataFrame พร้อม BB_Upper, BB_Middle, BB_Lower columns
    """
    # คำนวณ middle band (SMA)
    df['BB_Middle'] = df[column].rolling(window=window).mean()

    # คำนวณ standard deviation
    std = df[column].rolling(window=window).std()

    # คำนวณ upper และ lower bands
    df['BB_Upper'] = df['BB_Middle'] + (std * num_std)
    df['BB_Lower'] = df['BB_Middle'] - (std * num_std)

    return df


def calculate_atr(
    df: pd.DataFrame,
    high_col: str = 'high',
    low_col: str = 'low',
    close_col: str = 'close',
    period: int = 14
) -> pd.DataFrame:
    """
    คำนวณ Average True Range (ATR)

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มีข้อมูล high, low, close
    high_col : str
        ชื่อ column ของราคาสูงสุด
    low_col : str
        ชื่อ column ของราคาต่ำสุด
    close_col : str
        ชื่อ column ของราคาปิด
    period : int
        ช่วงเวลาสำหรับคำนวณ ATR

    Returns:
    --------
    pd.DataFrame
        DataFrame พร้อม ATR column
    """
    # คำนวณ True Range
    high_low = df[high_col] - df[low_col]
    high_close = np.abs(df[high_col] - df[close_col].shift())
    low_close = np.abs(df[low_col] - df[close_col].shift())

    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

    # คำนวณ ATR
    df[f'ATR_{period}'] = true_range.rolling(window=period).mean()

    return df


def add_all_indicators(
    df: pd.DataFrame,
    sma_windows: list = [7, 14, 30],
    ema_spans: list = [12, 26],
    rsi_period: int = 14
) -> pd.DataFrame:
    """
    เพิ่ม technical indicators ทั้งหมด

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มีข้อมูลราคา
    sma_windows : list
        รายการ windows สำหรับ SMA
    ema_spans : list
        รายการ spans สำหรับ EMA
    rsi_period : int
        period สำหรับ RSI

    Returns:
    --------
    pd.DataFrame
        DataFrame พร้อม indicators ทั้งหมด
    """
    df = df.copy()

    # SMA
    for window in sma_windows:
        df = calculate_sma(df, window=window)

    # EMA
    for span in ema_spans:
        df = calculate_ema(df, span=span)

    # RSI
    df = calculate_rsi(df, period=rsi_period)

    # MACD
    df = calculate_macd(df)

    # Bollinger Bands
    df = calculate_bollinger_bands(df)

    # ATR
    if all(col in df.columns for col in ['high', 'low', 'close']):
        df = calculate_atr(df)

    print(f"เพิ่ม technical indicators สำเร็จ: {len(df.columns)} columns")

    return df
