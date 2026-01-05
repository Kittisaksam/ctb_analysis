"""
DCA (Dollar Cost Averaging) Backtest
ทดสอบว่าการ DCA ในเดือนไหนของปีจะให้ผลตอบแทนดีที่สุด
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import sys

# เพิ่ม path เพื่อ import modules
sys.path.append('..')


class DCABacktest:
    """
    Backtest DCA strategy โดยทดสอบการลงทุนในเดือนต่างๆ
    """

    def __init__(self, df, monthly_investment=10000, symbol='BTC'):
        """
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame ที่มีข้อมูลราคา (index เป็น datetime)
        monthly_investment : float
            จำนวนเงินที่ลงทุนต่อเดือน (บาท)
        symbol : str
            สัญลักษณ์สินทรัพย์
        """
        self.df = df.copy()
        self.monthly_investment = monthly_investment
        self.symbol = symbol
        self.results = {}

        # เพิ่ม year และ month columns
        if not isinstance(self.df.index, pd.DatetimeIndex):
            if 'timestamp' in self.df.columns:
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                self.df.set_index('timestamp', inplace=True)

        self.df['year'] = self.df.index.year
        self.df['month'] = self.df.index.month

    def run_dca_strategy(self, target_month):
        """
        จำลอง DCA strategy โดยลงทุนในเดือนที่กำหนดของทุกปี
        เดือนที่ไม่ได้ลงทุนจะเก็บเงินทบไปเดือนถัดไป

        Parameters:
        -----------
        target_month : int
            เดือนที่ต้องการลงทุน (1-12)

        Returns:
        --------
        dict : ผลลัพธ์การ backtest
        """
        # เตรียมข้อมูลทุกเดือน (วันแรกของแต่ละเดือน)
        all_monthly_data = self.df.groupby(['year', 'month']).first().reset_index()

        if len(all_monthly_data) == 0:
            return None

        # จำลองการซื้อ
        total_invested = 0
        total_coins = 0
        accumulated_cash = 0  # เงินที่เก็บสะสมไว้
        purchases = []

        for idx, row in all_monthly_data.iterrows():
            current_month = row['month']
            price = row['close']

            # เพิ่มเงินออมเดือนละ 10,000 บาท
            accumulated_cash += self.monthly_investment

            # ถ้าเป็นเดือนที่กำหนด ให้ลงทุนด้วยเงินที่สะสมไว้ทั้งหมด
            if current_month == target_month:
                investment_amount = accumulated_cash
                coins_bought = investment_amount / price
                total_coins += coins_bought
                total_invested += investment_amount

                purchases.append({
                    'date': pd.Timestamp(year=row['year'], month=row['month'], day=1),
                    'price': price,
                    'investment_amount': investment_amount,
                    'coins_bought': coins_bought,
                    'total_invested': total_invested,
                    'total_coins': total_coins,
                    'months_accumulated': int(investment_amount / self.monthly_investment)
                })

                # Reset เงินสะสมหลังจากลงทุน
                accumulated_cash = 0

        # คำนวณผลตอบแทน
        if len(purchases) > 0:
            current_price = self.df['close'].iloc[-1]
            current_value = total_coins * current_price

            # บวกเงินที่ยังเก็บอยู่ (ยังไม่ได้ลงทุน) เข้าไปในมูลค่าปัจจุบัน
            current_value_with_cash = current_value + accumulated_cash

            # คำนวณเงินออมทั้งหมดที่ควรจะมี (ทุกเดือนตั้งแต่เริ่มต้น)
            total_months = len(all_monthly_data)
            total_should_save = total_months * self.monthly_investment

            total_return = current_value_with_cash - total_should_save
            return_pct = (total_return / total_should_save) * 100 if total_should_save > 0 else 0
            avg_cost = total_invested / total_coins if total_coins > 0 else 0

            return {
                'month': target_month,
                'total_invested': total_invested,
                'total_coins': total_coins,
                'avg_cost': avg_cost,
                'current_price': current_price,
                'current_value': current_value,
                'accumulated_cash': accumulated_cash,
                'current_value_with_cash': current_value_with_cash,
                'total_return': total_return,
                'return_pct': return_pct,
                'num_purchases': len(purchases),
                'total_months': total_months,
                'total_should_save': total_should_save,
                'purchases': purchases
            }

        return None

    def run_all_months(self):
        """
        ทดสอบ DCA strategy สำหรับทุกเดือน (1-12)

        Returns:
        --------
        pd.DataFrame : สรุปผลลัพธ์ทุกเดือน
        """
        month_names_th = {
            1: 'มกราคม', 2: 'กุมภาพันธ์', 3: 'มีนาคม',
            4: 'เมษายน', 5: 'พฤษภาคม', 6: 'มิถุนายน',
            7: 'กรกฎาคม', 8: 'สิงหาคม', 9: 'กันยายน',
            10: 'ตุลาคม', 11: 'พฤศจิกายน', 12: 'ธันวาคม'
        }

        results_list = []

        for month in range(1, 13):
            result = self.run_dca_strategy(month)
            if result:
                result['month_name'] = month_names_th[month]
                results_list.append(result)
                self.results[month] = result

        # สร้าง DataFrame สรุปผล
        summary_df = pd.DataFrame(results_list)
        summary_df = summary_df.sort_values('return_pct', ascending=False)

        return summary_df

    def plot_comparison(self, save_path=None):
        """
        Display comparison chart of returns for each month
        """
        month_names_en = {
            1: 'Jan', 2: 'Feb', 3: 'Mar',
            4: 'Apr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Aug', 9: 'Sep',
            10: 'Oct', 11: 'Nov', 12: 'Dec'
        }

        months = sorted(self.results.keys())
        returns = [self.results[m]['return_pct'] for m in months]
        month_labels = [month_names_en[m] for m in months]

        # Create charts
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # Chart 1: % Return
        colors = ['green' if r > 0 else 'red' for r in returns]
        bars1 = ax1.bar(month_labels, returns, color=colors, alpha=0.7, edgecolor='black')
        ax1.set_title(f'DCA Monthly Returns Comparison - {self.symbol}',
                     fontsize=14, fontweight='bold', pad=15)
        ax1.set_xlabel('DCA Month', fontsize=12)
        ax1.set_ylabel('Return (%)', fontsize=12)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.grid(True, alpha=0.3, axis='y')

        # Show values on bars
        for bar, return_val in zip(bars1, returns):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{return_val:.1f}%',
                    ha='center', va='bottom' if height > 0 else 'top',
                    fontsize=9, fontweight='bold')

        # Chart 2: Total Value (with cash)
        current_values = [self.results[m]['current_value_with_cash'] for m in months]
        bars2 = ax2.bar(month_labels, current_values, color='steelblue', alpha=0.7, edgecolor='black')
        ax2.set_title('Total Portfolio Value (Crypto + Cash)', fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlabel('DCA Month', fontsize=12)
        ax2.set_ylabel('Value (THB)', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')

        # Show values on bars
        for bar, value in zip(bars2, current_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:,.0f}',
                    ha='center', va='bottom',
                    fontsize=8)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved chart: {save_path}")

        plt.show()

    def plot_detailed_analysis(self, save_path=None):
        """
        Display detailed analysis charts
        """
        months = sorted(self.results.keys())

        # Prepare data
        total_invested = [self.results[m]['total_invested'] for m in months]
        total_return = [self.results[m]['total_return'] for m in months]
        avg_costs = [self.results[m]['avg_cost'] for m in months]
        num_purchases = [self.results[m]['num_purchases'] for m in months]
        accumulated_cash = [self.results[m]['accumulated_cash'] for m in months]

        month_names_en = {
            1: 'Jan', 2: 'Feb', 3: 'Mar',
            4: 'Apr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Aug', 9: 'Sep',
            10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
        month_labels = [month_names_en[m] for m in months]

        # Create charts
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Chart 1: Total Invested
        ax1.bar(month_labels, total_invested, color='lightblue', edgecolor='black')
        ax1.set_title('Total Amount Invested', fontsize=12, fontweight='bold')
        ax1.set_ylabel('THB', fontsize=10)
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3, axis='y')

        # Chart 2: Profit/Loss
        colors = ['green' if r > 0 else 'red' for r in total_return]
        ax2.bar(month_labels, total_return, color=colors, alpha=0.7, edgecolor='black')
        ax2.set_title('Profit/Loss', fontsize=12, fontweight='bold')
        ax2.set_ylabel('THB', fontsize=10)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')

        # Chart 3: Average Buy Price
        current_price = self.results[1]['current_price']
        colors = ['green' if cost < current_price else 'red' for cost in avg_costs]
        ax3.bar(month_labels, avg_costs, color=colors, alpha=0.7, edgecolor='black')
        ax3.axhline(y=current_price, color='blue', linestyle='--', linewidth=2,
                   label=f'Current Price: ${current_price:,.2f}')
        ax3.set_title('Average Buy Price', fontsize=12, fontweight='bold')
        ax3.set_ylabel('USD', fontsize=10)
        ax3.tick_params(axis='x', rotation=45)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        # Chart 4: Accumulated Cash
        ax4.bar(month_labels, accumulated_cash, color='gold', alpha=0.7, edgecolor='black')
        ax4.set_title('Accumulated Cash (Not Yet Invested)', fontsize=12, fontweight='bold')
        ax4.set_ylabel('THB', fontsize=10)
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3, axis='y')

        # Show values on bars if there is accumulated cash
        for label, cash in zip(month_labels, accumulated_cash):
            if cash > 0:
                idx = month_labels.index(label)
                ax4.text(idx, cash, f'{cash:,.0f}', ha='center', va='bottom', fontsize=8)

        plt.suptitle(f'DCA Strategy Detailed Analysis - {self.symbol}',
                    fontsize=16, fontweight='bold', y=1.00)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved chart: {save_path}")

        plt.show()

    def print_summary(self, summary_df):
        """
        แสดงสรุปผลแบบละเอียด
        """
        print("\n" + "="*100)
        print(f"สรุปผล DCA Backtest - {self.symbol}")
        print(f"เงินลงทุนต่อเดือน: {self.monthly_investment:,.0f} บาท")
        print(f"ช่วงเวลา: {self.df.index.min().strftime('%Y-%m-%d')} ถึง {self.df.index.max().strftime('%Y-%m-%d')}")
        print("="*100)

        # แสดงตาราง
        display_df = summary_df[[
            'month_name', 'num_purchases', 'total_invested', 'accumulated_cash',
            'avg_cost', 'current_value_with_cash', 'total_return', 'return_pct'
        ]].copy()

        display_df.columns = [
            'เดือน', 'จำนวนครั้ง', 'ลงทุนแล้ว (บาท)', 'เงินคงเหลือ (บาท)',
            'ราคาเฉลี่ย (USD)', 'มูลค่ารวม (บาท)',
            'กำไร/ขาดทุน (บาท)', '% ผลตอบแทน'
        ]

        # Format numbers
        display_df['ลงทุนแล้ว (บาท)'] = display_df['ลงทุนแล้ว (บาท)'].apply(lambda x: f'{x:,.0f}')
        display_df['เงินคงเหลือ (บาท)'] = display_df['เงินคงเหลือ (บาท)'].apply(lambda x: f'{x:,.0f}')
        display_df['ราคาเฉลี่ย (USD)'] = display_df['ราคาเฉลี่ย (USD)'].apply(lambda x: f'${x:,.2f}')
        display_df['มูลค่ารวม (บาท)'] = display_df['มูลค่ารวม (บาท)'].apply(lambda x: f'{x:,.0f}')
        display_df['กำไร/ขาดทุน (บาท)'] = display_df['กำไร/ขาดทุน (บาท)'].apply(
            lambda x: f'+{x:,.0f}' if x > 0 else f'{x:,.0f}'
        )
        display_df['% ผลตอบแทน'] = display_df['% ผลตอบแทน'].apply(
            lambda x: f'+{x:.2f}%' if x > 0 else f'{x:.2f}%'
        )

        print(display_df.to_string(index=False))
        print("="*100)

        # คำอธิบายวิธีการทำงาน
        print("\n📝 หมายเหตุ:")
        print(f"   - ออมเงินทุกเดือน {self.monthly_investment:,.0f} บาท")
        print("   - เดือนที่ไม่ได้ลงทุนจะเก็บเงินสะสมไปลงทุนในเดือนถัดไป")
        print(f"   - เงินออมทั้งหมด {summary_df.iloc[0]['total_should_save']:,.0f} บาท ({summary_df.iloc[0]['total_months']} เดือน)")
        print("   - มูลค่ารวม = มูลค่า crypto + เงินสดคงเหลือ")

        # แสดง Top 3
        print("\n🏆 TOP 3 เดือนที่ให้ผลตอบแทนดีที่สุด:")
        for i, row in summary_df.head(3).iterrows():
            print(f"   {row['month_name']:>12} - ผลตอบแทน: {row['return_pct']:>7.2f}% | "
                  f"กำไร: {row['total_return']:>12,.0f} บาท | "
                  f"ราคาเฉลี่ย: ${row['avg_cost']:>8,.2f} | "
                  f"เงินคงเหลือ: {row['accumulated_cash']:>10,.0f} บาท")

        print("\n📉 Bottom 3 เดือนที่ให้ผลตอบแทนต่ำที่สุด:")
        for i, row in summary_df.tail(3).iterrows():
            print(f"   {row['month_name']:>12} - ผลตอบแทน: {row['return_pct']:>7.2f}% | "
                  f"กำไร: {row['total_return']:>12,.0f} บาท | "
                  f"ราคาเฉลี่ย: ${row['avg_cost']:>8,.2f} | "
                  f"เงินคงเหลือ: {row['accumulated_cash']:>10,.0f} บาท")

        print("\n" + "="*100)


def main():
    """
    ฟังก์ชันหลักสำหรับรัน backtest
    """
    print("\n" + "="*100)
    print("DCA BACKTEST - ทดสอบว่าการ DCA ในเดือนไหนของปีดีที่สุด")
    print("="*100)

    # ตั้งค่า
    MONTHLY_INVESTMENT = 10000  # บาท
    SYMBOL = 'BTCUSDT'

    # โหลดข้อมูล
    data_path = Path('../data/raw')
    csv_files = list(data_path.glob('*.csv'))

    if not csv_files:
        print("\n❌ ไม่พบไฟล์ CSV ใน data/raw/")
        print("กรุณารันสคริปต์ binance_historical_data.py ก่อน")
        return

    # ใช้ไฟล์ล่าสุด
    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
    print(f"\n📂 กำลังโหลดข้อมูลจาก: {latest_file.name}")

    # โหลดข้อมูล
    df = pd.read_csv(latest_file, parse_dates=['timestamp'])
    df.set_index('timestamp', inplace=True)

    print(f"✓ โหลดข้อมูลสำเร็จ")
    print(f"   - ช่วงเวลา: {df.index.min().strftime('%Y-%m-%d')} ถึง {df.index.max().strftime('%Y-%m-%d')}")
    print(f"   - จำนวนข้อมูล: {len(df):,} แถว")

    # สร้าง backtest object
    backtest = DCABacktest(df, monthly_investment=MONTHLY_INVESTMENT, symbol='BTC')

    # รัน backtest ทุกเดือน
    print("\n⏳ กำลังรัน backtest...")
    summary_df = backtest.run_all_months()

    # แสดงผล
    backtest.print_summary(summary_df)

    # สร้างกราฟ
    print("\n📊 กำลังสร้างกราฟ...")

    output_dir = Path('../outputs/figures')
    output_dir.mkdir(parents=True, exist_ok=True)

    backtest.plot_comparison(save_path=output_dir / 'dca_comparison.png')
    backtest.plot_detailed_analysis(save_path=output_dir / 'dca_detailed_analysis.png')

    # บันทึกผลลัพธ์
    results_dir = Path('../outputs/reports')
    results_dir.mkdir(parents=True, exist_ok=True)

    summary_df.to_csv(results_dir / 'dca_backtest_results.csv', index=False)
    print(f"\n✓ บันทึกผลลัพธ์ที่: {results_dir / 'dca_backtest_results.csv'}")

    print("\n" + "="*100)
    print("✓ เสร็จสิ้นการ backtest")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
