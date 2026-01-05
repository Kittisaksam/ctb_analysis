# CTB Data Science Project

โปรเจค Data Science สำหรับการวิเคราะห์และพัฒนาโมเดล

## โครงสร้างโปรเจค

```
ctb_dev/
│
├── data/                   # ข้อมูลทั้งหมด
│   ├── raw/               # ข้อมูลดิบที่ยังไม่ผ่านการประมวลผล
│   ├── processed/         # ข้อมูลที่ประมวลผลแล้ว พร้อมใช้งาน
│   ├── interim/           # ข้อมูลระหว่างการประมวลผล
│   └── external/          # ข้อมูลจากแหล่งภายนอก
│
├── notebooks/             # Jupyter notebooks สำหรับ exploration และ analysis
│
├── src/                   # Source code หลักของโปรเจค
│   ├── data/             # โค้ดสำหรับโหลดและประมวลผลข้อมูล
│   ├── features/         # โค้ดสำหรับสร้าง features
│   ├── models/           # โค้ดสำหรับ train และ evaluate models
│   └── visualization/    # โค้ดสำหรับสร้างกราฟและ visualizations
│
├── models/                # โมเดลที่ train แล้ว, model predictions, model summaries
│
├── outputs/               # ผลลัพธ์ที่ได้จากการวิเคราะห์
│   ├── figures/          # กราฟและรูปภาพ
│   └── reports/          # รายงานและเอกสารผลลัพธ์
│
├── scripts/               # สคริปต์สำหรับดึงข้อมูลและงานอื่นๆ
│
├── config/                # Configuration files
│
├── tests/                 # Unit tests และ integration tests
│
└── docs/                  # เอกสารโปรเจค
```

## การติดตั้ง

```bash
# สร้าง virtual environment
python -m venv venv
source venv/bin/activate  # สำหรับ Mac/Linux
# หรือ venv\Scripts\activate  # สำหรับ Windows

# ติดตั้ง dependencies
pip install -r requirements.txt
```

## การใช้งาน

### 1. ดึงข้อมูลจาก Binance
```bash
python scripts/binance_historical_data.py
```

### 2. เปิด Jupyter Notebook
```bash
jupyter notebook
```

## Dependencies

ดูรายการ dependencies ใน `requirements.txt`

## License

MIT
