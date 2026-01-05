"""
Data loading utilities
"""
import pandas as pd
from pathlib import Path
from typing import Optional, Union


def load_csv_data(
    file_path: Union[str, Path],
    parse_dates: Optional[list] = None,
    index_col: Optional[str] = None
) -> pd.DataFrame:
    """
    โหลดข้อมูลจากไฟล์ CSV

    Parameters:
    -----------
    file_path : str or Path
        path ของไฟล์ CSV
    parse_dates : list, optional
        รายชื่อ columns ที่ต้องการแปลงเป็น datetime
    index_col : str, optional
        column ที่ต้องการใช้เป็น index

    Returns:
    --------
    pd.DataFrame
        DataFrame ที่โหลดข้อมูลแล้ว
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์: {file_path}")

    df = pd.read_csv(
        file_path,
        parse_dates=parse_dates,
        index_col=index_col
    )

    print(f"โหลดข้อมูลสำเร็จ: {file_path.name}")
    print(f"Shape: {df.shape}")

    return df


def load_binance_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    โหลดข้อมูลจาก Binance CSV file

    Parameters:
    -----------
    file_path : str or Path
        path ของไฟล์ CSV

    Returns:
    --------
    pd.DataFrame
        DataFrame พร้อม timestamp เป็น datetime index
    """
    df = load_csv_data(
        file_path,
        parse_dates=['timestamp', 'close_time']
    )

    # Set timestamp as index
    if 'timestamp' in df.columns:
        df.set_index('timestamp', inplace=True)

    return df


def save_processed_data(
    df: pd.DataFrame,
    file_name: str,
    output_dir: Union[str, Path] = 'data/processed'
) -> Path:
    """
    บันทึกข้อมูลที่ประมวลผลแล้ว

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่ต้องการบันทึก
    file_name : str
        ชื่อไฟล์
    output_dir : str or Path
        directory ที่ต้องการบันทึก

    Returns:
    --------
    Path
        path ของไฟล์ที่บันทึก
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / file_name
    df.to_csv(output_path)

    print(f"บันทึกข้อมูลสำเร็จ: {output_path}")

    return output_path
