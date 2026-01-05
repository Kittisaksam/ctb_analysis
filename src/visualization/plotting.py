"""
Visualization utilities
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from typing import Optional, Tuple


def setup_plot_style(style: str = 'seaborn-v0_8-darkgrid'):
    """
    ตั้งค่า plot style

    Parameters:
    -----------
    style : str
        matplotlib style
    """
    plt.style.use(style)
    sns.set_palette('husl')


def plot_price_chart(
    df: pd.DataFrame,
    price_col: str = 'close',
    figsize: Tuple[int, int] = (15, 6),
    title: str = 'Price Chart',
    save_path: Optional[Path] = None
):
    """
    วาดกราฟราคา

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มีข้อมูลราคา (index เป็น datetime)
    price_col : str
        ชื่อ column ของราคา
    figsize : tuple
        ขนาดของ figure
    title : str
        ชื่อกราฟ
    save_path : Path, optional
        path สำหรับบันทึกกราฟ
    """
    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(df.index, df[price_col], linewidth=2)
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price (USDT)', fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"บันทึกกราฟที่: {save_path}")

    plt.show()


def plot_candlestick(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (15, 8),
    title: str = 'Candlestick Chart',
    save_path: Optional[Path] = None
):
    """
    วาดกราฟแท่งเทียน (Candlestick)

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มี columns: open, high, low, close
    figsize : tuple
        ขนาดของ figure
    title : str
        ชื่อกราฟ
    save_path : Path, optional
        path สำหรับบันทึกกราฟ
    """
    from matplotlib.patches import Rectangle

    fig, ax = plt.subplots(figsize=figsize)

    # สำหรับแสดงแท่งเทียนแบบง่าย
    up = df[df.close >= df.open]
    down = df[df.close < df.open]

    # Plot up prices
    ax.bar(up.index, up.close - up.open, bottom=up.open,
           color='g', alpha=0.8, width=0.8)
    ax.bar(up.index, up.high - up.close, bottom=up.close,
           color='g', alpha=0.4, width=0.1)
    ax.bar(up.index, up.open - up.low, bottom=up.low,
           color='g', alpha=0.4, width=0.1)

    # Plot down prices
    ax.bar(down.index, down.close - down.open, bottom=down.open,
           color='r', alpha=0.8, width=0.8)
    ax.bar(down.index, down.high - down.open, bottom=down.open,
           color='r', alpha=0.4, width=0.1)
    ax.bar(down.index, down.close - down.low, bottom=down.low,
           color='r', alpha=0.4, width=0.1)

    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Price (USDT)', fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"บันทึกกราฟที่: {save_path}")

    plt.show()


def plot_volume(
    df: pd.DataFrame,
    volume_col: str = 'volume',
    figsize: Tuple[int, int] = (15, 4),
    title: str = 'Trading Volume',
    save_path: Optional[Path] = None
):
    """
    วาดกราฟปริมาณการซื้อขาย

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame ที่มีข้อมูล volume
    volume_col : str
        ชื่อ column ของ volume
    figsize : tuple
        ขนาดของ figure
    title : str
        ชื่อกราฟ
    save_path : Path, optional
        path สำหรับบันทึกกราฟ
    """
    fig, ax = plt.subplots(figsize=figsize)

    ax.bar(df.index, df[volume_col], alpha=0.7, color='steelblue')
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Volume', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')

    plt.xticks(rotation=45)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"บันทึกกราฟที่: {save_path}")

    plt.show()


def plot_correlation_matrix(
    df: pd.DataFrame,
    figsize: Tuple[int, int] = (12, 10),
    title: str = 'Correlation Matrix',
    save_path: Optional[Path] = None
):
    """
    วาด correlation matrix

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame
    figsize : tuple
        ขนาดของ figure
    title : str
        ชื่อกราฟ
    save_path : Path, optional
        path สำหรับบันทึกกราฟ
    """
    fig, ax = plt.subplots(figsize=figsize)

    # คำนวณ correlation
    corr = df.corr()

    # Plot heatmap
    sns.heatmap(
        corr,
        annot=True,
        fmt='.2f',
        cmap='coolwarm',
        center=0,
        square=True,
        linewidths=1,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )

    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"บันทึกกราฟที่: {save_path}")

    plt.show()
