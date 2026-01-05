"""
Buy the Dip Strategy
ซื้อทุกครั้งที่ BTC ลดลง 5% ในหนึ่งวัน
โดยมีเงินออม 10,000 บาท/เดือน
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


class BuyTheDip:
    """
    Buy the Dip Strategy - ซื้อเมื่อราคาลดลงตามเปอร์เซ็นต์ที่กำหนด
    """

    def __init__(self, df, monthly_savings=10000, dip_threshold=-5.0, symbol='BTC'):
        """
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame ที่มีข้อมูลราคา (index เป็น datetime)
        monthly_savings : float
            จำนวนเงินที่ออมต่อเดือน (บาท)
        dip_threshold : float
            เปอร์เซ็นต์การลดลงที่จะซื้อ (เช่น -5.0 = ลดลง 5%)
        symbol : str
            สัญลักษณ์สินทรัพย์
        """
        self.df = df.copy()
        self.monthly_savings = monthly_savings
        self.dip_threshold = dip_threshold
        self.symbol = symbol
        self.purchases = []
        self.results = {}

        # เพิ่ม date columns
        if not isinstance(self.df.index, pd.DatetimeIndex):
            if 'timestamp' in self.df.columns:
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                self.df.set_index('timestamp', inplace=True)

        # คำนวณ daily return
        self.df['daily_return'] = ((self.df['close'] - self.df['open']) /
                                    self.df['open'] * 100)

    def run_strategy(self):
        """
        จำลอง Buy the Dip strategy

        Returns:
        --------
        dict : ผลลัพธ์การ backtest
        """
        self.df['year'] = self.df.index.year
        self.df['month'] = self.df.index.month
        self.df['day'] = self.df.index.day

        total_invested = 0
        total_coins = 0
        accumulated_cash = 0
        purchases = []
        daily_savings = 0

        # คำนวณเงินออมรายวัน
        total_days = len(self.df)
        total_months = total_days / 30  # ประมาณการ
        daily_savings = self.monthly_savings / 30  # เฉลี่ยเงินออมต่อวัน

        print(f"\n⏳ Running Buy the Dip simulation...")
        print(f"   - Monthly savings: {self.monthly_savings:,.0f} THB")
        print(f"   - Daily savings: ~{daily_savings:,.2f} THB")
        print(f"   - Dip threshold: {self.dip_threshold}%")
        print(f"   - Period: {self.df.index.min().strftime('%Y-%m-%d')} to {self.df.index.max().strftime('%Y-%m-%d')}\n")

        dip_days = 0
        missed_opportunities = 0

        for idx, row in self.df.iterrows():
            # เพิ่มเงินออมทุกวัน
            accumulated_cash += daily_savings

            # ตรวจสอบว่าวันนี้ราคาลดลงเกินเกณฑ์หรือไม่
            if row['daily_return'] <= self.dip_threshold:
                dip_days += 1

                # ถ้ามีเงินสะสมอยู่ ให้ซื้อ
                if accumulated_cash >= 100:  # ขั้นต่ำในการซื้อ 100 บาท
                    price = row['close']
                    investment = accumulated_cash
                    coins_bought = investment / price

                    total_coins += coins_bought
                    total_invested += investment

                    purchase = {
                        'date': idx,
                        'price': price,
                        'daily_return': row['daily_return'],
                        'investment': investment,
                        'coins_bought': coins_bought,
                        'total_invested': total_invested,
                        'total_coins': total_coins,
                        'avg_price': total_invested / total_coins if total_coins > 0 else 0
                    }
                    purchases.append(purchase)

                    # Reset เงินสะสม
                    accumulated_cash = 0
                else:
                    missed_opportunities += 1

        print(f"   ✓ Completed simulation")
        print(f"   - Dip days (≤{self.dip_threshold}%): {dip_days}")
        print(f"   - Purchases made: {len(purchases)}")
        print(f"   - Missed opportunities (no cash): {missed_opportunities}")

        # คำนวณผลตอบแทน
        if len(purchases) > 0:
            current_price = self.df['close'].iloc[-1]
            current_value = total_coins * current_price

            # เงินออมทั้งหมดที่ควรมี
            total_should_save = total_days * daily_savings

            # มูลค่ารวม (crypto + เงินสดคงเหลือ)
            current_value_with_cash = current_value + accumulated_cash

            total_return = current_value_with_cash - total_should_save
            return_pct = (total_return / total_should_save) * 100 if total_should_save > 0 else 0
            avg_cost = total_invested / total_coins if total_coins > 0 else 0

            self.results = {
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
                'total_days': total_days,
                'total_should_save': total_should_save,
                'dip_days': dip_days,
                'missed_opportunities': missed_opportunities,
                'first_purchase': purchases[0]['date'] if purchases else None,
                'last_purchase': purchases[-1]['date'] if purchases else None,
                'purchases': purchases
            }

            self.purchases = purchases

            return self.results

        return None

    def print_summary(self):
        """
        แสดงสรุปผลแบบละเอียด
        """
        if not self.results:
            print("No results available. Run run_strategy() first.")
            return

        print("\n" + "="*100)
        print(f"BUY THE DIP STRATEGY RESULTS - {self.symbol}")
        print(f"Strategy: Buy when price drops ≤{self.dip_threshold}% in a day")
        print(f"Monthly Savings: {self.monthly_savings:,.0f} THB")
        print("="*100)

        print(f"\n📅 Period:")
        print(f"   First purchase: {self.results['first_purchase'].strftime('%Y-%m-%d')}")
        print(f"   Last purchase:  {self.results['last_purchase'].strftime('%Y-%m-%d')}")
        print(f"   Total days:     {self.results['total_days']}")

        print(f"\n📊 Strategy Statistics:")
        print(f"   Dip days (≤{self.dip_threshold}%):    {self.results['dip_days']}")
        print(f"   Purchases made:       {self.results['num_purchases']}")
        print(f"   Missed opportunities: {self.results['missed_opportunities']} (no cash available)")
        print(f"   Purchase rate:        {self.results['num_purchases']/self.results['dip_days']*100:.1f}% of dip days")

        print(f"\n💰 Investment Summary:")
        print(f"   Total should save:    {self.results['total_should_save']:>15,.0f} THB")
        print(f"   Actually invested:    {self.results['total_invested']:>15,.0f} THB")
        print(f"   Cash remaining:       {self.results['accumulated_cash']:>15,.0f} THB")
        print(f"   Investment rate:      {self.results['total_invested']/self.results['total_should_save']*100:>14.1f} %")

        print(f"\n🪙 {self.symbol} Holdings:")
        print(f"   Total {self.symbol} bought:   {self.results['total_coins']:>15,.8f} {self.symbol}")
        print(f"   Average buy price: {self.results['avg_cost']:>15,.2f} USD")

        print(f"\n📊 Current Status:")
        print(f"   Current price:     {self.results['current_price']:>15,.2f} USD")
        print(f"   {self.symbol} value:        {self.results['current_value']:>15,.0f} THB")
        print(f"   Cash:              {self.results['accumulated_cash']:>15,.0f} THB")
        print(f"   Total value:       {self.results['current_value_with_cash']:>15,.0f} THB")

        print(f"\n🎯 Performance:")
        profit_symbol = "+" if self.results['total_return'] >= 0 else ""
        print(f"   Profit/Loss:       {profit_symbol}{self.results['total_return']:>14,.0f} THB")
        print(f"   Return:            {profit_symbol}{self.results['return_pct']:>14,.2f} %")

        # เปรียบเทียบกับ Simple DCA
        print(f"\n💡 Key Insight:")
        utilization = self.results['total_invested'] / self.results['total_should_save'] * 100
        if utilization < 50:
            print(f"   ⚠️  Low capital utilization ({utilization:.1f}%)")
            print(f"   💵 Most of your savings ({self.results['accumulated_cash']:,.0f} THB) remain as cash")
            print(f"   📉 This happens when dip opportunities are rare")
        else:
            print(f"   ✓ Good capital utilization ({utilization:.1f}%)")
            print(f"   ✓ Successfully bought the dip {self.results['num_purchases']} times")

        print("\n" + "="*100)

    def plot_strategy_analysis(self, save_path=None):
        """
        แสดงกราฟวิเคราะห์กลยุทธ์
        """
        if not self.purchases:
            print("No purchase history available.")
            return

        df_purchases = pd.DataFrame(self.purchases)

        fig = plt.figure(figsize=(18, 14))
        gs = fig.add_gridspec(4, 2, hspace=0.3, wspace=0.25)

        # Chart 1: Price chart with purchase points
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(self.df.index, self.df['close'], label='BTC Price',
                color='gray', alpha=0.5, linewidth=1)

        # แสดงวันที่ลดลงเกิน threshold
        dip_days = self.df[self.df['daily_return'] <= self.dip_threshold]
        ax1.scatter(dip_days.index, dip_days['close'],
                   color='lightcoral', s=20, alpha=0.3, label=f'Dip Days (≤{self.dip_threshold}%)', zorder=3)

        # แสดงจุดที่ซื้อจริง
        ax1.scatter(df_purchases['date'], df_purchases['price'],
                   color='green', s=100, alpha=0.8, label='Actual Purchases',
                   marker='^', edgecolors='darkgreen', linewidth=1.5, zorder=5)

        ax1.axhline(y=self.results['avg_cost'], color='red', linestyle='--',
                   linewidth=2, label=f'Avg Buy Price: ${self.results["avg_cost"]:,.0f}')
        ax1.set_title(f'{self.symbol} Price & Buy the Dip Purchase Points',
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=11)
        ax1.set_ylabel('Price (USD)', fontsize=11)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)

        # Chart 2: Daily returns distribution
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.hist(self.df['daily_return'], bins=50, color='steelblue',
                edgecolor='black', alpha=0.7)
        ax2.axvline(x=self.dip_threshold, color='red', linestyle='--',
                   linewidth=2, label=f'Threshold: {self.dip_threshold}%')
        ax2.set_title('Daily Return Distribution', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Daily Return (%)', fontsize=10)
        ax2.set_ylabel('Frequency', fontsize=10)
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        # Chart 3: Purchase sizes
        ax3 = fig.add_subplot(gs[1, 1])
        colors_invest = ['green' if x > self.monthly_savings else 'orange'
                        for x in df_purchases['investment']]
        ax3.bar(range(len(df_purchases)), df_purchases['investment'],
               color=colors_invest, edgecolor='black', alpha=0.7)
        ax3.axhline(y=self.monthly_savings, color='red', linestyle='--',
                   linewidth=2, label=f'Monthly Savings: {self.monthly_savings:,.0f}')
        ax3.set_title('Investment Amount per Purchase', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Purchase #', fontsize=10)
        ax3.set_ylabel('Amount (THB)', fontsize=10)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')

        # Chart 4: Accumulated cash over time
        ax4 = fig.add_subplot(gs[2, :])

        # สร้างข้อมูล accumulated cash over time
        cash_history = []
        accumulated_cash = 0
        daily_savings = self.monthly_savings / 30
        purchase_idx = 0

        for idx, row in self.df.iterrows():
            accumulated_cash += daily_savings

            # ตรวจสอบว่ามีการซื้อวันนี้หรือไม่
            if purchase_idx < len(self.purchases):
                if self.purchases[purchase_idx]['date'] == idx:
                    accumulated_cash = 0  # ใช้เงินหมด
                    purchase_idx += 1

            cash_history.append({'date': idx, 'cash': accumulated_cash})

        df_cash = pd.DataFrame(cash_history)
        ax4.fill_between(df_cash['date'], df_cash['cash'], alpha=0.3, color='gold')
        ax4.plot(df_cash['date'], df_cash['cash'], color='orange', linewidth=2)
        ax4.scatter(df_purchases['date'], [0]*len(df_purchases),
                   color='green', s=100, marker='v', label='Purchases (Cash → 0)', zorder=5)
        ax4.set_title('Accumulated Cash Over Time', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Date', fontsize=10)
        ax4.set_ylabel('Cash (THB)', fontsize=10)
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        # Chart 5: Portfolio value evolution
        ax5 = fig.add_subplot(gs[3, :])

        # คำนวณมูลค่าพอร์ตโฟลิโอตลอดเวลา
        portfolio_values = []
        for purchase in self.purchases:
            value = purchase['total_coins'] * self.df.loc[purchase['date'], 'close']
            portfolio_values.append({
                'date': purchase['date'],
                'portfolio_value': value,
                'invested': purchase['total_invested'],
                'profit': value - purchase['total_invested']
            })

        if portfolio_values:
            df_portfolio = pd.DataFrame(portfolio_values)
            ax5.plot(df_portfolio['date'], df_portfolio['portfolio_value'],
                    color='green', linewidth=2, label='Portfolio Value', marker='o', markersize=4)
            ax5.plot(df_portfolio['date'], df_portfolio['invested'],
                    color='blue', linewidth=2, linestyle='--', label='Total Invested', alpha=0.7)
            ax5.fill_between(df_portfolio['date'], df_portfolio['portfolio_value'],
                            df_portfolio['invested'],
                            where=(df_portfolio['portfolio_value'] >= df_portfolio['invested']),
                            color='green', alpha=0.2, label='Profit')
            ax5.fill_between(df_portfolio['date'], df_portfolio['portfolio_value'],
                            df_portfolio['invested'],
                            where=(df_portfolio['portfolio_value'] < df_portfolio['invested']),
                            color='red', alpha=0.2, label='Loss')
            ax5.set_title('Portfolio Value vs Investment', fontsize=12, fontweight='bold')
            ax5.set_xlabel('Date', fontsize=10)
            ax5.set_ylabel('Value (THB)', fontsize=10)
            ax5.legend(loc='best')
            ax5.grid(True, alpha=0.3)

        plt.suptitle(f'Buy the Dip Strategy Analysis - {self.symbol}',
                    fontsize=16, fontweight='bold', y=0.995)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved chart: {save_path}")

        plt.show()

    def export_results(self, output_path):
        """
        บันทึกผลลัพธ์เป็น CSV
        """
        if not self.purchases:
            print("No purchase history available.")
            return

        df_purchases = pd.DataFrame(self.purchases)
        df_purchases['date'] = df_purchases['date'].dt.strftime('%Y-%m-%d')

        # Add current portfolio value
        df_purchases['current_value'] = df_purchases['total_coins'] * self.results['current_price']
        df_purchases['current_profit'] = df_purchases['current_value'] - df_purchases['total_invested']
        df_purchases['current_return_pct'] = (df_purchases['current_profit'] /
                                              df_purchases['total_invested'] * 100)

        df_purchases.to_csv(output_path, index=False)
        print(f"✓ Saved purchase history: {output_path}")


def main():
    """
    ฟังก์ชันหลักสำหรับรัน Buy the Dip backtest
    """
    print("\n" + "="*100)
    print("BUY THE DIP STRATEGY BACKTEST")
    print("="*100)

    # ตั้งค่า
    MONTHLY_SAVINGS = 10000  # บาท
    DIP_THRESHOLD = -5.0     # เปอร์เซ็นต์
    SYMBOL = 'BTCUSDT'

    # โหลดข้อมูล
    data_path = Path('../data/raw')
    csv_files = list(data_path.glob('*.csv'))

    if not csv_files:
        print("\n❌ No CSV files found in data/raw/")
        print("Please run binance_historical_data.py first")
        return

    # ใช้ไฟล์ล่าสุด
    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
    print(f"\n📂 Loading data from: {latest_file.name}")

    # โหลดข้อมูล
    df = pd.read_csv(latest_file, parse_dates=['timestamp'])
    df.set_index('timestamp', inplace=True)

    print(f"✓ Data loaded successfully")
    print(f"   - Period: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    print(f"   - Total records: {len(df):,}")

    # สร้าง Buy the Dip object
    btd = BuyTheDip(df, monthly_savings=MONTHLY_SAVINGS,
                    dip_threshold=DIP_THRESHOLD, symbol='BTC')

    # รัน backtest
    results = btd.run_strategy()

    if results:
        # แสดงผล
        btd.print_summary()

        # สร้างกราฟ
        print("\n📊 Creating charts...")

        output_dir = Path('../outputs/figures')
        output_dir.mkdir(parents=True, exist_ok=True)

        btd.plot_strategy_analysis(save_path=output_dir / 'buy_the_dip_analysis.png')

        # บันทึกผลลัพธ์
        results_dir = Path('../outputs/reports')
        results_dir.mkdir(parents=True, exist_ok=True)

        btd.export_results(results_dir / 'buy_the_dip_purchases.csv')

        print("\n" + "="*100)
        print("✓ Backtest completed successfully")
        print("="*100 + "\n")
    else:
        print("\n❌ No results generated")


if __name__ == "__main__":
    main()
