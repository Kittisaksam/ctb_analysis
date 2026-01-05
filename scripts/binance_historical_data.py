import requests
import pandas as pd
from datetime import datetime, timedelta
import time

def get_binance_historical_data(symbol='BTCUSDT', interval='1d', years=3):
    """
    ดึงข้อมูลราคาจาก Binance ย้อนหลัง

    Parameters:
    - symbol: คู่เหรียญ (default: BTCUSDT)
    - interval: ช่วงเวลา (1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M)
    - years: จำนวนปีย้อนหลัง
    """

    url = "https://api.binance.com/api/v3/klines"

    # คำนวณเวลาเริ่มต้น (ย้อนหลัง n ปี)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=years*365)

    # แปลงเป็น timestamp (milliseconds)
    start_timestamp = int(start_time.timestamp() * 1000)
    end_timestamp = int(end_time.timestamp() * 1000)

    all_data = []
    current_start = start_timestamp

    print(f"กำลังดึงข้อมูล {symbol} ตั้งแต่ {start_time.strftime('%Y-%m-%d')} ถึง {end_time.strftime('%Y-%m-%d')}")
    print(f"Interval: {interval}")
    print("กรุณารอสักครู่...\n")

    # Binance จำกัดการดึงข้อมูลครั้งละ 1000 candles
    limit = 1000

    while current_start < end_timestamp:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': current_start,
            'endTime': end_timestamp,
            'limit': limit
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                break

            all_data.extend(data)

            # อัพเดทเวลาเริ่มต้นสำหรับการดึงครั้งต่อไป
            current_start = data[-1][0] + 1

            print(f"ดึงข้อมูลได้ {len(all_data)} รายการแล้ว...")

            # หน่วงเวลาเล็กน้อยเพื่อไม่ให้ถูก rate limit
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            break

    # สร้าง DataFrame
    df = pd.DataFrame(all_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_volume', 'trades', 'taker_buy_base',
        'taker_buy_quote', 'ignore'
    ])

    # แปลง timestamp เป็น datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

    # แปลงข้อมูลราคาเป็น float
    price_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_volume',
                     'taker_buy_base', 'taker_buy_quote']
    df[price_columns] = df[price_columns].astype(float)

    # เรียงลำดับตามเวลา
    df = df.sort_values('timestamp').reset_index(drop=True)

    return df

if __name__ == "__main__":
    # ดึงข้อมูล BTCUSDT ย้อนหลัง 3 ปี (รายวัน)
    df = get_binance_historical_data(symbol='BTCUSDT', interval='1d', years=3)

    # แสดงข้อมูลตัวอย่าง
    print("\n" + "="*80)
    print("ข้อมูลตัวอย่าง (5 แถวแรก):")
    print("="*80)
    print(df.head())

    print("\n" + "="*80)
    print("ข้อมูลตัวอย่าง (5 แถวสุดท้าย):")
    print("="*80)
    print(df.tail())

    print("\n" + "="*80)
    print("สถิติข้อมูล:")
    print("="*80)
    print(f"จำนวนรายการทั้งหมด: {len(df)}")
    print(f"ช่วงเวลา: {df['timestamp'].min()} ถึง {df['timestamp'].max()}")
    print(f"\nราคา:")
    print(f"  - สูงสุด: ${df['high'].max():,.2f}")
    print(f"  - ต่ำสุด: ${df['low'].min():,.2f}")
    print(f"  - ราคาล่าสุด: ${df['close'].iloc[-1]:,.2f}")

    # บันทึกเป็นไฟล์ CSV
    output_file = f"binance_{df['timestamp'].min().strftime('%Y%m%d')}_{df['timestamp'].max().strftime('%Y%m%d')}.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✓ บันทึกข้อมูลลงไฟล์: {output_file}")

    # บันทึกเป็นไฟล์ Excel (ถ้าต้องการ)
    # df.to_excel('binance_btcusdt_3years.xlsx', index=False)
