# Quick Start Guide

คู่มือเริ่มต้นใช้งาน CTB Data Science Project

## การติดตั้ง

### 1. สร้าง Virtual Environment

```bash
# สร้าง venv
python -m venv venv

# Activate venv
# สำหรับ Mac/Linux:
source venv/bin/activate

# สำหรับ Windows:
venv\Scripts\activate
```

### 2. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

## การใช้งาน

### 1. ดึงข้อมูลจาก Binance

```bash
cd scripts
python binance_historical_data.py
```

ข้อมูลจะถูกบันทึกไว้ใน `data/raw/` เป็นไฟล์ CSV

### 2. Data Exploration

เปิด Jupyter Notebook:

```bash
jupyter notebook
```

จากนั้นเปิดไฟล์ `notebooks/01_data_exploration.ipynb`

### 3. ใช้งาน Utility Functions

#### โหลดข้อมูล

```python
from src.data.data_loader import load_binance_data

# โหลดข้อมูล
df = load_binance_data('data/raw/your_file.csv')
```

#### คำนวณ Technical Indicators

```python
from src.features.technical_indicators import add_all_indicators

# เพิ่ม indicators
df = add_all_indicators(df)
```

#### Visualization

```python
from src.visualization.plotting import plot_price_chart, plot_volume

# วาดกราฟราคา
plot_price_chart(df, save_path='outputs/figures/price_chart.png')

# วาดกราฟ volume
plot_volume(df, save_path='outputs/figures/volume.png')
```

## ตัวอย่างการใช้งานแบบเต็ม

```python
import pandas as pd
from src.data.data_loader import load_binance_data, save_processed_data
from src.features.technical_indicators import add_all_indicators
from src.visualization.plotting import plot_price_chart

# 1. โหลดข้อมูล
df = load_binance_data('data/raw/binance_data.csv')

# 2. เพิ่ม features
df = add_all_indicators(df)

# 3. บันทึกข้อมูลที่ประมวลผลแล้ว
save_processed_data(df, 'processed_data.csv')

# 4. Visualization
plot_price_chart(
    df,
    title='BTC/USDT Price Chart',
    save_path='outputs/figures/btc_price.png'
)

print("เสร็จสิ้น!")
```

## โครงสร้างโปรเจค

```
ctb_dev/
├── data/           # ข้อมูลทั้งหมด
├── notebooks/      # Jupyter notebooks
├── src/            # Source code
├── scripts/        # Utility scripts
├── models/         # Trained models
├── outputs/        # Results และ figures
├── config/         # Configuration files
└── docs/           # Documentation
```

## Tips

1. **เก็บข้อมูลดิบ**: อย่าแก้ไขไฟล์ใน `data/raw/` โดยตรง ให้ใช้ `data/processed/` แทน
2. **Version Control**: ใช้ git แต่ไม่ต้อง commit ไฟล์ข้อมูลขนาดใหญ่ (มี .gitignore ไว้แล้ว)
3. **Notebooks**: ตั้งชื่อ notebook ด้วยเลขนำหน้า (01_, 02_) เพื่อความเป็นระเบียบ
4. **Configuration**: เก็บค่า config ไว้ใน `config/config.yaml` แทนการ hard-code

## ปัญหาที่พบบ่อย

### Import Error

ถ้าเจอ import error ให้เพิ่ม project root ใน PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/ctb_dev"
```

หรือใน notebook:

```python
import sys
sys.path.append('..')
```

### API Rate Limit

ถ้าดึงข้อมูลจาก Binance ติด rate limit ให้เพิ่มเวลารอใน `binance_historical_data.py`

## ทรัพยากรเพิ่มเติม

- [Binance API Documentation](https://binance-docs.github.io/apidocs/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
