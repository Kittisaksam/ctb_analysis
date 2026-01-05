"""
Simple DCA Strategy - Monthly Investment
ลงทุนทุกเดือนในวันที่ 5 เดือนละ 10,000 บาท ไม่เคยขาด
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


class SimpleDCA:
    """
    Simple DCA Strategy - ลงทุนทุกเดือนแบบสม่ำเสมอ
    """

    def __init__(self, df, monthly_investment=10000, day_of_month=5, symbol='BTC'):
        """
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame ที่มีข้อมูลราคา (index เป็น datetime)
        monthly_investment : float
            จำนวนเงินที่ลงทุนต่อเดือน (บาท)
        day_of_month : int
            วันที่ของเดือนที่ทำ DCA (1-31)
        symbol : str
            สัญลักษณ์สินทรัพย์
        """
        self.df = df.copy()
        self.monthly_investment = monthly_investment
        self.day_of_month = day_of_month
        self.symbol = symbol
        self.purchases = []
        self.results = {}

        # เพิ่ม date columns
        if not isinstance(self.df.index, pd.DatetimeIndex):
            if 'timestamp' in self.df.columns:
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                self.df.set_index('timestamp', inplace=True)

    def run_dca(self):
        """
        จำลอง DCA strategy โดยลงทุนทุกเดือนในวันที่กำหนด

        Returns:
        --------
        dict : ผลลัพธ์การ backtest
        """
        # หา unique year-month combinations
        self.df['year'] = self.df.index.year
        self.df['month'] = self.df.index.month
        self.df['day'] = self.df.index.day

        unique_months = self.df.groupby(['year', 'month']).size().reset_index()[['year', 'month']]

        total_invested = 0
        total_coins = 0
        purchases = []

        print(f"\n⏳ Running DCA simulation...")
        print(f"   - Investment: {self.monthly_investment:,.0f} THB/month")
        print(f"   - Day of month: {self.day_of_month}")
        print(f"   - Period: {self.df.index.min().strftime('%Y-%m-%d')} to {self.df.index.max().strftime('%Y-%m-%d')}\n")

        for idx, row in unique_months.iterrows():
            year = row['year']
            month = row['month']

            # หาข้อมูลในเดือนนั้น
            month_data = self.df[(self.df['year'] == year) & (self.df['month'] == month)]

            if len(month_data) == 0:
                continue

            # หาวันที่ใกล้เคียงกับวันที่กำหนดมากที่สุด (หรือวันถัดไปถ้าไม่มีข้อมูลวันนั้น)
            target_date = pd.Timestamp(year=year, month=month, day=self.day_of_month)

            # หาวันที่มีข้อมูลที่ใกล้เคียงที่สุด (หลังจากหรือเท่ากับวันที่กำหนด)
            available_dates = month_data.index
            matching_dates = available_dates[available_dates >= target_date]

            if len(matching_dates) > 0:
                buy_date = matching_dates[0]
            else:
                # ถ้าไม่มีวันที่หลังจากวันที่กำหนด ใช้วันสุดท้ายของเดือน
                buy_date = available_dates[-1]

            # ดึงข้อมูลราคา
            price = self.df.loc[buy_date, 'close']
            coins_bought = self.monthly_investment / price
            total_coins += coins_bought
            total_invested += self.monthly_investment

            purchase = {
                'date': buy_date,
                'year': year,
                'month': month,
                'price': price,
                'investment': self.monthly_investment,
                'coins_bought': coins_bought,
                'total_invested': total_invested,
                'total_coins': total_coins,
                'avg_price': total_invested / total_coins
            }
            purchases.append(purchase)

        # คำนวณผลตอบแทน
        if len(purchases) > 0:
            current_price = self.df['close'].iloc[-1]
            current_value = total_coins * current_price
            total_return = current_value - total_invested
            return_pct = (total_return / total_invested) * 100 if total_invested > 0 else 0
            avg_cost = total_invested / total_coins if total_coins > 0 else 0

            self.results = {
                'total_invested': total_invested,
                'total_coins': total_coins,
                'avg_cost': avg_cost,
                'current_price': current_price,
                'current_value': current_value,
                'total_return': total_return,
                'return_pct': return_pct,
                'num_purchases': len(purchases),
                'first_purchase': purchases[0]['date'],
                'last_purchase': purchases[-1]['date'],
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
            print("No results available. Run run_dca() first.")
            return

        print("\n" + "="*100)
        print(f"SIMPLE DCA BACKTEST RESULTS - {self.symbol}")
        print(f"Strategy: Monthly DCA on day {self.day_of_month} of each month")
        print(f"Investment: {self.monthly_investment:,.0f} THB/month")
        print("="*100)

        print(f"\n📅 Period:")
        print(f"   First purchase: {self.results['first_purchase'].strftime('%Y-%m-%d')}")
        print(f"   Last purchase:  {self.results['last_purchase'].strftime('%Y-%m-%d')}")
        print(f"   Total months:   {self.results['num_purchases']}")

        print(f"\n💰 Investment Summary:")
        print(f"   Total invested:    {self.results['total_invested']:>15,.0f} THB")
        print(f"   Total {self.symbol} bought:   {self.results['total_coins']:>15,.8f} {self.symbol}")
        print(f"   Average buy price: {self.results['avg_cost']:>15,.2f} USD")

        print(f"\n📊 Current Status:")
        print(f"   Current price:     {self.results['current_price']:>15,.2f} USD")
        print(f"   Portfolio value:   {self.results['current_value']:>15,.0f} THB")

        print(f"\n🎯 Performance:")
        profit_symbol = "+" if self.results['total_return'] >= 0 else ""
        print(f"   Profit/Loss:       {profit_symbol}{self.results['total_return']:>14,.0f} THB")
        print(f"   Return:            {profit_symbol}{self.results['return_pct']:>14,.2f} %")

        # ROI comparison
        buy_hold_return = ((self.results['current_price'] - self.purchases[0]['price']) /
                          self.purchases[0]['price'] * 100)
        print(f"\n📈 Comparison:")
        print(f"   DCA Return:        {profit_symbol}{self.results['return_pct']:>14,.2f} %")
        print(f"   Buy & Hold Return: {'+' if buy_hold_return >= 0 else ''}{buy_hold_return:>14,.2f} %")
        print(f"   (if bought all {self.results['total_invested']:,.0f} THB on {self.purchases[0]['date'].strftime('%Y-%m-%d')})")

        print("\n" + "="*100)

    def plot_dca_history(self, save_path=None):
        """
        แสดงกราฟประวัติการ DCA
        """
        if not self.purchases:
            print("No purchase history available.")
            return

        df_purchases = pd.DataFrame(self.purchases)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 12))

        # Chart 1: Price and DCA purchases
        ax1.plot(self.df.index, self.df['close'], label='BTC Price', color='gray', alpha=0.5, linewidth=1)
        ax1.scatter(df_purchases['date'], df_purchases['price'],
                   color='green', s=50, alpha=0.6, label='DCA Purchases', zorder=5)
        ax1.axhline(y=self.results['avg_cost'], color='red', linestyle='--',
                   linewidth=2, label=f'Avg Buy Price: ${self.results["avg_cost"]:,.0f}')
        ax1.set_title(f'{self.symbol} Price & DCA Purchase Points', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Date', fontsize=11)
        ax1.set_ylabel('Price (USD)', fontsize=11)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)

        # Chart 2: Accumulated Investment
        ax2.plot(df_purchases['date'], df_purchases['total_invested'],
                color='blue', linewidth=2, marker='o', markersize=4)
        ax2.fill_between(df_purchases['date'], df_purchases['total_invested'],
                        alpha=0.3, color='blue')
        ax2.set_title('Accumulated Investment', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=11)
        ax2.set_ylabel('Total Invested (THB)', fontsize=11)
        ax2.grid(True, alpha=0.3)

        # Chart 3: Accumulated Coins
        ax3.plot(df_purchases['date'], df_purchases['total_coins'],
                color='orange', linewidth=2, marker='o', markersize=4)
        ax3.fill_between(df_purchases['date'], df_purchases['total_coins'],
                        alpha=0.3, color='orange')
        ax3.set_title(f'Accumulated {self.symbol}', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Date', fontsize=11)
        ax3.set_ylabel(f'Total {self.symbol}', fontsize=11)
        ax3.grid(True, alpha=0.3)

        # Chart 4: Portfolio Value over time
        portfolio_values = []
        for purchase in self.purchases:
            # คำนวณมูลค่าพอร์ตโฟลิโอ ณ เวลานั้น
            value = purchase['total_coins'] * self.df.loc[purchase['date'], 'close']
            portfolio_values.append({
                'date': purchase['date'],
                'portfolio_value': value,
                'invested': purchase['total_invested'],
                'profit': value - purchase['total_invested']
            })

        df_portfolio = pd.DataFrame(portfolio_values)
        ax4.plot(df_portfolio['date'], df_portfolio['portfolio_value'],
                color='green', linewidth=2, label='Portfolio Value', marker='o', markersize=4)
        ax4.plot(df_portfolio['date'], df_portfolio['invested'],
                color='blue', linewidth=2, linestyle='--', label='Total Invested', alpha=0.7)
        ax4.fill_between(df_portfolio['date'], df_portfolio['portfolio_value'],
                        df_portfolio['invested'],
                        where=(df_portfolio['portfolio_value'] >= df_portfolio['invested']),
                        color='green', alpha=0.2, label='Profit')
        ax4.fill_between(df_portfolio['date'], df_portfolio['portfolio_value'],
                        df_portfolio['invested'],
                        where=(df_portfolio['portfolio_value'] < df_portfolio['invested']),
                        color='red', alpha=0.2, label='Loss')
        ax4.set_title('Portfolio Value vs Investment', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Date', fontsize=11)
        ax4.set_ylabel('Value (THB)', fontsize=11)
        ax4.legend(loc='best')
        ax4.grid(True, alpha=0.3)

        plt.suptitle(f'Simple DCA Strategy Analysis - {self.symbol}',
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved chart: {save_path}")

        plt.show()

    def plot_purchase_distribution(self, save_path=None):
        """
        แสดงกราฟการกระจายตัวของการซื้อ
        """
        if not self.purchases:
            print("No purchase history available.")
            return

        df_purchases = pd.DataFrame(self.purchases)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Chart 1: Purchase prices distribution
        ax1.hist(df_purchases['price'], bins=30, color='steelblue',
                edgecolor='black', alpha=0.7)
        ax1.axvline(x=self.results['avg_cost'], color='red', linestyle='--',
                   linewidth=2, label=f'Average: ${self.results["avg_cost"]:,.0f}')
        ax1.axvline(x=self.results['current_price'], color='green', linestyle='--',
                   linewidth=2, label=f'Current: ${self.results["current_price"]:,.0f}')
        ax1.set_title('Purchase Price Distribution', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Price (USD)', fontsize=10)
        ax1.set_ylabel('Frequency', fontsize=10)
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        # Chart 2: Coins bought per purchase
        ax2.bar(range(len(df_purchases)), df_purchases['coins_bought'],
               color='orange', edgecolor='black', alpha=0.7)
        ax2.set_title('Coins Bought Each Month', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Purchase #', fontsize=10)
        ax2.set_ylabel(f'{self.symbol} Bought', fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')

        # Chart 3: Running average price
        ax3.plot(df_purchases['date'], df_purchases['avg_price'],
                color='purple', linewidth=2, marker='o', markersize=4)
        ax3.plot(df_purchases['date'], df_purchases['price'],
                color='gray', linewidth=1, alpha=0.5, label='Spot Price')
        ax3.axhline(y=self.results['current_price'], color='green',
                   linestyle='--', linewidth=2, label=f'Current: ${self.results["current_price"]:,.0f}')
        ax3.set_title('Average Buy Price Evolution', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Date', fontsize=10)
        ax3.set_ylabel('Price (USD)', fontsize=10)
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Chart 4: Monthly statistics
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_counts = df_purchases['month'].value_counts().sort_index()

        ax4.bar(monthly_counts.index, monthly_counts.values,
               color='teal', edgecolor='black', alpha=0.7)
        ax4.set_title('Purchases by Month', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Month', fontsize=10)
        ax4.set_ylabel('Number of Purchases', fontsize=10)
        ax4.set_xticks(range(1, 13))
        ax4.set_xticklabels(month_names)
        ax4.grid(True, alpha=0.3, axis='y')

        plt.suptitle(f'DCA Purchase Distribution Analysis - {self.symbol}',
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved chart: {save_path}")

        plt.show()

    def export_purchase_history(self, output_path):
        """
        บันทึกประวัติการซื้อเป็น CSV
        """
        if not self.purchases:
            print("No purchase history available.")
            return

        df_purchases = pd.DataFrame(self.purchases)
        df_purchases['date'] = df_purchases['date'].dt.strftime('%Y-%m-%d')

        # Add portfolio value at each purchase
        df_purchases['portfolio_value'] = df_purchases['total_coins'] * df_purchases['price']
        df_purchases['profit_loss'] = df_purchases['portfolio_value'] - df_purchases['total_invested']
        df_purchases['return_pct'] = (df_purchases['profit_loss'] / df_purchases['total_invested'] * 100)

        # Reorder columns
        df_purchases = df_purchases[[
            'date', 'year', 'month', 'price', 'investment',
            'coins_bought', 'total_coins', 'total_invested',
            'avg_price', 'portfolio_value', 'profit_loss', 'return_pct'
        ]]

        df_purchases.to_csv(output_path, index=False)
        print(f"✓ Saved purchase history: {output_path}")


def main():
    """
    ฟังก์ชันหลักสำหรับรัน Simple DCA backtest
    """
    print("\n" + "="*100)
    print("SIMPLE DCA BACKTEST - Monthly Investment Strategy")
    print("="*100)

    # ตั้งค่า
    MONTHLY_INVESTMENT = 10000  # บาท
    DAY_OF_MONTH = 5
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

    # สร้าง DCA object
    dca = SimpleDCA(df, monthly_investment=MONTHLY_INVESTMENT,
                    day_of_month=DAY_OF_MONTH, symbol='BTC')

    # รัน backtest
    results = dca.run_dca()

    if results:
        # แสดงผล
        dca.print_summary()

        # สร้างกราฟ
        print("\n📊 Creating charts...")

        output_dir = Path('../outputs/figures')
        output_dir.mkdir(parents=True, exist_ok=True)

        dca.plot_dca_history(save_path=output_dir / 'simple_dca_history.png')
        dca.plot_purchase_distribution(save_path=output_dir / 'simple_dca_distribution.png')

        # บันทึกผลลัพธ์
        results_dir = Path('../outputs/reports')
        results_dir.mkdir(parents=True, exist_ok=True)

        dca.export_purchase_history(results_dir / 'simple_dca_purchases.csv')

        print("\n" + "="*100)
        print("✓ Backtest completed successfully")
        print("="*100 + "\n")
    else:
        print("\n❌ No results generated")


if __name__ == "__main__":
    main()
