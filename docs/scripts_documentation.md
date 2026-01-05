# Documentation for Python Scripts in `ctb_dev/scripts`

เอกสารนี้อธิบายการทำงานของ Python scripts ภายในโฟลเดอร์ `/Users/coraline/Documents/ctb_dev/scripts` ซึ่งเป็นชุดเครื่องมือสำหรับดึงข้อมูลและทดสอบกลยุทธ์การลงทุน (Backtesting) ในตลาดคริปโตเคอร์เรนซี

## Overview

Scripts ชุดนี้ถูกออกแบบมาเพื่อทำงานร่วมกันเป็น Pipeline ดังนี้:
1.  **ดึงข้อมูล**: `binance_historical_data.py` ดึงข้อมูลราคาจาก Binance มาเก็บไว้
2.  **ทดสอบกลยุทธ์**:
    *   `simple_dca.py`: ทดสอบการลงทุนแบบเฉลี่ยต้นทุน (DCA) รายเดือน
    *   `buy_the_dip.py`: ทดสอบการลงทุนเมื่อราคาตกลง (Buy the Dip)
    *   `dca_backtest.py`: ทดสอบว่า DCA เดือนไหนของปีดีที่สุด (Annual DCA)
3.  **เปรียบเทียบผลลัพธ์**: `compare_strategies.py` เปรียบเทียบผลตอบแทนระหว่าง Simple DCA และ Buy the Dip

---

## Detailed Description

### 1. `binance_historical_data.py`
**หน้าที่หลัก:** ดึงข้อมูลราคา (Candlestick/Kline data) ย้อนหลังจา Binance API และบันทึกเป็นไฟล์ CSV เพื่อใช้ในสคริปต์อื่นๆ

*   **ฟังก์ชันสำคัญ:**
    *   `get_binance_historical_data(symbol, interval, years)`:
        *   ดึงข้อมูลเป็น batch (ครั้งละ 1000 candles) เพื่อเลี่ยงข้อจำกัดของ API
        *   แปลง Timestamp เป็น Datetime ที่อ่านง่าย
        *   จัดการ Rate Limiting โดยการหน่วงเวลา (`time.sleep`)
*   **การใช้งาน:**
    *   แก้ไขค่าใน `if __name__ == "__main__":` เพื่อเปลี่ยนคู่เหรียญ (`BTCUSDT`), timeframe (`1d`), หรือจำนวนปีย้อนหลัง
    *   รันสคริปต์เพื่อสร้างไฟล์ CSV (ชื่อไฟล์จะมี timestamp ระบุช่วงเวลา)

### 2. `simple_dca.py`
**หน้าที่หลัก:** จำลองกลยุทธ์ **Dollar Cost Averaging (DCA)** แบบพื้นฐาน คือการลงทุนด้วยจำนวนเงินเท่ากันทุกๆ เดือน ในวันที่กำหนด

*   **คลาส `SimpleDCA`:**
    *   `__init__`: รับข้อมูลราคาและตั้งค่าเงินลงทุนรายเดือน (`monthly_investment`), วันที่ลงทุน (`day_of_month`)
    *   `run_dca()`: วนลูปตามเดือนเพื่อจำลองการซื้อ:
        *   หาราคาปิด (`close`) ของวันที่กำหนด (หรือวันถัดไปที่มีข้อมูล)
        *   คำนวณจำนวนเหรียญที่ซื้อได้และสะสมเข้าพอร์ต
    *   `print_summary()`: แสดงสรุปผลตอบแทน (Profit/Loss, ROI) เทียบกับวิธี Buy & Hold
    *   `plot_dca_history()` & `plot_purchase_distribution()`: สร้างกราฟแสดงจุดที่ซื้อและการเติบโตของพอร์ต
*   **Output:** ไฟล์ CSV ประวัติการซื้อและกราฟ PNG

### 3. `buy_the_dip.py`
**หน้าที่หลัก:** จำลองกลยุทธ์ **Buy the Dip** คือการเก็บเงินออมไว้ และจะซื้อก็ต่อเมื่อราคาในวันนั้นลดลงต่ำกว่าเกณฑ์ที่กำหนด (เช่น -5%)

*   **คลาส `BuyTheDip`:**
    *   `__init__`: ตั้งค่าเงินออมต่อเดือน (`monthly_savings`) และเกณฑ์ราคาตก (`dip_threshold`)
    *   `run_strategy()`: วนลูปรายวัน:
        *   สะสมเงินออมรายวันเข้า `accumulated_cash`
        *   ตรวจสอบ `daily_return` ถ้าต่ำกว่า `dip_threshold` และมีเงินสดพอ ให้ทำการซื้อด้วยเงินสดทั้งหมดทันที ("All-in on dip")
        *   ถ้าไม่ถึงเกณฑ์ ก็เก็บเงินสะสมต่อไป
    *   `plot_strategy_analysis()`: แสดงกราฟจังหวะที่ราคาตก (Dip days) เทียบกับวันที่ซื้อจริง (เพราะบางครั้งราคาตกแต่ไม่มีเงินซื้อ)
*   **Insight:** สคริปต์นี้ช่วยวิเคราะห์ "Capital Utilization" (ประสิทธิภาพการใช้เงิน) เพราะถ้าตั้งเกณฑ์ยากเกินไป อาจจะมีเงินสดกองอยู่เฉยๆ ไม่ได้ลงทุน

### 4. `dca_backtest.py`
**หน้าที่หลัก:** ทดสอบสมมติฐานเกี่ยวกับการ DCA รายปี (Invest Once a Year) เพื่อดูว่า "เดือนไหน" ของปีที่ลงทุนแล้วให้ผลตอบแทนดีที่สุด

*   **คลาส `DCABacktest`:**
    *   `run_dca_strategy(target_month)`: จำลองการลงทุนเฉพาะในเดือน `target_month` ของทุกปี (เดือนอื่นเก็บเงินสะสมรอ)
    *   `run_all_months()`: รัน Loop ทดสอบตั้งแต่เดือน 1 ถึง 12 เพื่อหาเดือนที่ดีที่สุด
*   **Output:** ตาราง Ranking จัดอันดับเดือนที่ลงทุนแล้วเวิร์คที่สุด พร้อมกราฟเปรียบเทียบ

### 5. `compare_strategies.py`
**หน้าที่หลัก:** เป็นสคริปต์รวม ("Master Script") ที่นำ `SimpleDCA` และ `BuyTheDip` มารันพร้อมกันด้วยข้อมูลชุดเดียวกันเพื่อเปรียบเทียบ

*   **คลาส `StrategyComparison`:**
    *   `run_all_strategies()`: เรียกใช้ Instance ของทั้งสองกลยุทธ์
    *   `print_comparison()`: แสดงตารางเปรียบเทียบ Head-to-Head ในมิติต่างๆ:
        *   จำนวน BTC ที่ได้
        *   ราคาเฉลี่ยที่ซื้อ (Average Cost)
        *   ผลตอบแทนรวม (%)
        *   Capital Utilization
    *   มีระบบ Scoring ให้คะแนนว่าใครชนะในแต่ละด้าน
*   **การใช้งาน:** ใช้เพื่อหาคำตอบว่า "รอซื้อตอนย่อ" (Timing the market) คุ้มค่ากว่า "ซื้อถัวเฉลี่ย" (Time in the market) หรือไม่ สำหรับ dataset นั้นๆ

---

## Recommended Workflow

หากต้องการเริ่มใช้งาน แนะนำให้ทำตามลำดับดังนี้:

1.  **Prepare Data:**
    ```bash
    python binance_historical_data.py
    ```
    *   ตรวจสอบว่าได้ไฟล์ `.csv` ในโฟลเดอร์ (หรือโฟลเดอร์ที่กำหนด)

2.  **Compare Strategies:**
    ```bash
    python compare_strategies.py
    ```
    *   สคริปต์จะโหลดไฟล์ CSV ล่าสุดอัตโนมัติ และรันการเปรียบเทียบ
    *   ดูผลลัพธ์ที่ Terminal และไฟล์ใน `../outputs/figures` หรือ `../outputs/reports`

3.  **Deep Dive (Optional):**
    *   หากสนใจรายละเอียด DCA รายเดือน: รัน `simple_dca.py`
    *   หากสนใจพฤติกรรม Buy the Dip: รัน `buy_the_dip.py`
    *   หากอยากรู้ Seasonality (เดือนไหนดีสุด): รัน `dca_backtest.py`
