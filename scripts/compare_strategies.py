"""
Compare Strategies: Simple DCA vs Buy the Dip
เปรียบเทียบว่าวิธีไหนได้ BTC เยอะกว่ากัน
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

# Import strategies
from simple_dca import SimpleDCA
from buy_the_dip import BuyTheDip


class StrategyComparison:
    """
    เปรียบเทียบกลยุทธ์การลงทุนต่างๆ
    """

    def __init__(self, df, monthly_investment=10000):
        """
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame ที่มีข้อมูลราคา
        monthly_investment : float
            จำนวนเงินที่ลงทุน/ออมต่อเดือน
        """
        self.df = df.copy()
        self.monthly_investment = monthly_investment
        self.results = {}

    def run_all_strategies(self, dip_threshold=-5.0, day_of_month=5):
        """
        รันทุกกลยุทธ์พร้อมกัน

        Parameters:
        -----------
        dip_threshold : float
            เกณฑ์การลดลงสำหรับ Buy the Dip
        day_of_month : int
            วันของเดือนสำหรับ Simple DCA
        """
        print("\n" + "="*100)
        print("RUNNING ALL STRATEGIES...")
        print("="*100)

        # Strategy 1: Simple DCA
        print("\n1️⃣  Running Simple DCA Strategy...")
        simple_dca = SimpleDCA(self.df.copy(),
                               monthly_investment=self.monthly_investment,
                               day_of_month=day_of_month,
                               symbol='BTC')
        simple_dca_results = simple_dca.run_dca()

        # Strategy 2: Buy the Dip
        print("\n2️⃣  Running Buy the Dip Strategy...")
        buy_dip = BuyTheDip(self.df.copy(),
                           monthly_savings=self.monthly_investment,
                           dip_threshold=dip_threshold,
                           symbol='BTC')
        buy_dip_results = buy_dip.run_strategy()

        # เก็บผลลัพธ์
        self.results = {
            'simple_dca': {
                'strategy': simple_dca,
                'results': simple_dca_results
            },
            'buy_the_dip': {
                'strategy': buy_dip,
                'results': buy_dip_results
            }
        }

        print("\n✓ All strategies completed")

    def print_comparison(self):
        """
        แสดงการเปรียบเทียบแบบละเอียด
        """
        if not self.results:
            print("No results available. Run run_all_strategies() first.")
            return

        dca_r = self.results['simple_dca']['results']
        dip_r = self.results['buy_the_dip']['results']

        print("\n" + "="*100)
        print("STRATEGY COMPARISON RESULTS")
        print("="*100)

        print(f"\n📅 Testing Period:")
        print(f"   From: {self.df.index.min().strftime('%Y-%m-%d')}")
        print(f"   To:   {self.df.index.max().strftime('%Y-%m-%d')}")
        print(f"   Days: {len(self.df)}")

        print(f"\n💵 Investment Budget:")
        print(f"   Monthly: {self.monthly_investment:,} THB")

        # สร้างตารางเปรียบเทียบ
        print("\n" + "="*100)
        print("DETAILED COMPARISON")
        print("="*100)

        # Header
        print(f"\n{'Metric':<40} {'Simple DCA':>20} {'Buy the Dip':>20} {'Winner':>15}")
        print("-" * 100)

        # จำนวน BTC ที่ได้
        dca_btc = dca_r['total_coins']
        dip_btc = dip_r['total_coins']
        btc_winner = "Simple DCA" if dca_btc > dip_btc else "Buy the Dip"
        btc_diff_pct = abs(dca_btc - dip_btc) / max(dca_btc, dip_btc) * 100
        print(f"{'🪙 Total BTC Acquired':<40} {dca_btc:>19.8f} {dip_btc:>19.8f} {btc_winner:>15}")
        print(f"{'   (Difference)':<40} {'':<20} {'':<20} {btc_diff_pct:>13.2f}%")

        # เงินลงทุนทั้งหมด
        dca_invested = dca_r['total_invested']
        dip_invested = dip_r['total_invested']
        print(f"{'💰 Total Invested (THB)':<40} {dca_invested:>19,.0f} {dip_invested:>19,.0f}")

        # ราคาเฉลี่ยที่ซื้อ
        dca_avg = dca_r['avg_cost']
        dip_avg = dip_r['avg_cost']
        avg_winner = "Simple DCA" if dca_avg < dip_avg else "Buy the Dip"
        avg_diff = abs(dca_avg - dip_avg)
        print(f"{'📊 Average Buy Price (USD)':<40} {dca_avg:>19,.2f} {dip_avg:>19,.2f} {avg_winner:>15}")
        print(f"{'   (Difference)':<40} {'':<20} {'':<20} ${avg_diff:>12,.2f}")

        # จำนวนครั้งที่ซื้อ
        dca_purchases = dca_r['num_purchases']
        dip_purchases = dip_r['num_purchases']
        print(f"{'🔢 Number of Purchases':<40} {dca_purchases:>20} {dip_purchases:>20}")

        # มูลค่าปัจจุบัน
        dca_value = dca_r['current_value']
        dip_value = dip_r['current_value']
        value_winner = "Simple DCA" if dca_value > dip_value else "Buy the Dip"
        print(f"{'💎 Portfolio Value (THB)':<40} {dca_value:>19,.0f} {dip_value:>19,.0f} {value_winner:>15}")

        # ผลตอบแทน
        dca_return = dca_r['return_pct']
        dip_return = dip_r['return_pct']
        return_winner = "Simple DCA" if dca_return > dip_return else "Buy the Dip"
        print(f"{'📈 Return (%)':<40} {dca_return:>19.2f} {dip_return:>19.2f} {return_winner:>15}")

        # กำไร
        dca_profit = dca_r['total_return']
        dip_profit = dip_r['total_return']
        profit_winner = "Simple DCA" if dca_profit > dip_profit else "Buy the Dip"
        print(f"{'💵 Profit/Loss (THB)':<40} {dca_profit:>19,.0f} {dip_profit:>19,.0f} {profit_winner:>15}")

        # Capital Utilization
        dca_util = (dca_invested / dca_r['total_invested']) * 100 if 'total_invested' in dca_r else 100
        dip_util = (dip_invested / dip_r['total_should_save']) * 100 if 'total_should_save' in dip_r else 100
        print(f"{'⚡ Capital Utilization (%)':<40} {100.0:>19.2f} {dip_util:>19.2f}")

        print("\n" + "="*100)
        print("SUMMARY")
        print("="*100)

        # คำนวณคะแนน
        scores = {
            'Simple DCA': 0,
            'Buy the Dip': 0
        }

        # คะแนนจาก BTC ที่ได้
        if dca_btc > dip_btc:
            scores['Simple DCA'] += 3
            btc_verdict = f"Simple DCA gets {btc_diff_pct:.2f}% MORE BTC"
        else:
            scores['Buy the Dip'] += 3
            btc_verdict = f"Buy the Dip gets {btc_diff_pct:.2f}% MORE BTC"

        # คะแนนจากราคาเฉลี่ย
        if dca_avg < dip_avg:
            scores['Simple DCA'] += 2
        else:
            scores['Buy the Dip'] += 2

        # คะแนนจากผลตอบแทน
        if dca_return > dip_return:
            scores['Simple DCA'] += 2
        else:
            scores['Buy the Dip'] += 2

        # คะแนนจาก Capital Utilization
        if dca_util > dip_util:
            scores['Simple DCA'] += 1
        else:
            scores['Buy the Dip'] += 1

        print(f"\n🏆 WINNER: {max(scores, key=scores.get)}")
        print(f"\n   Scores:")
        print(f"   - Simple DCA:    {scores['Simple DCA']}/8 points")
        print(f"   - Buy the Dip:   {scores['Buy the Dip']}/8 points")

        print(f"\n📌 Key Findings:")
        print(f"   1. {btc_verdict}")
        print(f"   2. Better avg price: {avg_winner} (${min(dca_avg, dip_avg):,.2f} vs ${max(dca_avg, dip_avg):,.2f})")
        print(f"   3. Higher return: {return_winner} ({max(dca_return, dip_return):.2f}%)")
        print(f"   4. More efficient: {'Simple DCA' if dca_util > dip_util else 'Buy the Dip'} ({max(dca_util, dip_util):.1f}% capital used)")

        # BTC per THB efficiency
        dca_efficiency = dca_btc / dca_invested
        dip_efficiency = dip_btc / dip_invested
        better_efficiency = "Simple DCA" if dca_efficiency > dip_efficiency else "Buy the Dip"

        print(f"\n💡 BTC per 10,000 THB:")
        print(f"   - Simple DCA:    {dca_efficiency * 10000:.8f} BTC")
        print(f"   - Buy the Dip:   {dip_efficiency * 10000:.8f} BTC")
        print(f"   → {better_efficiency} is more efficient!")

        print("\n" + "="*100)

    def plot_comparison(self, save_path=None):
        """
        สร้างกราฟเปรียบเทียบ
        """
        if not self.results:
            print("No results available.")
            return

        dca_r = self.results['simple_dca']['results']
        dip_r = self.results['buy_the_dip']['results']
        dca_purchases = self.results['simple_dca']['strategy'].purchases
        dip_purchases = self.results['buy_the_dip']['strategy'].purchases

        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Chart 1: BTC Comparison (BIG)
        ax1 = fig.add_subplot(gs[0, :2])
        strategies = ['Simple DCA', 'Buy the Dip']
        btc_amounts = [dca_r['total_coins'], dip_r['total_coins']]
        colors = ['green' if btc_amounts[0] > btc_amounts[1] else 'orange',
                 'orange' if btc_amounts[0] > btc_amounts[1] else 'green']

        bars = ax1.bar(strategies, btc_amounts, color=colors, edgecolor='black',
                      linewidth=2, alpha=0.7, width=0.6)
        ax1.set_title('Total BTC Acquired', fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel('BTC', fontsize=13)
        ax1.grid(True, alpha=0.3, axis='y')

        # แสดงค่าบน bar
        for bar, amount in zip(bars, btc_amounts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{amount:.6f} BTC',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

        # แสดงความต่าง
        diff = abs(btc_amounts[0] - btc_amounts[1])
        diff_pct = (diff / max(btc_amounts)) * 100
        winner = 'Simple DCA' if btc_amounts[0] > btc_amounts[1] else 'Buy the Dip'
        ax1.text(0.5, max(btc_amounts) * 0.5,
                f'{winner}\ngets {diff_pct:.2f}% more BTC\n({diff:.6f} BTC)',
                ha='center', va='center',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
                fontsize=11, fontweight='bold')

        # Chart 2: Return Comparison
        ax2 = fig.add_subplot(gs[0, 2])
        returns = [dca_r['return_pct'], dip_r['return_pct']]
        colors_ret = ['green' if r > 0 else 'red' for r in returns]
        bars2 = ax2.bar(strategies, returns, color=colors_ret, edgecolor='black',
                       linewidth=2, alpha=0.7)
        ax2.set_title('Return %', fontsize=14, fontweight='bold')
        ax2.set_ylabel('%', fontsize=11)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax2.grid(True, alpha=0.3, axis='y')

        for bar, ret in zip(bars2, returns):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{ret:.1f}%',
                    ha='center', va='bottom' if ret > 0 else 'top',
                    fontsize=10, fontweight='bold')

        # Chart 3: Price chart with purchase points
        ax3 = fig.add_subplot(gs[1, :])
        ax3.plot(self.df.index, self.df['close'], label='BTC Price',
                color='gray', alpha=0.4, linewidth=1)

        # Simple DCA purchases
        df_dca = pd.DataFrame(dca_purchases)
        ax3.scatter(df_dca['date'], df_dca['price'],
                   color='green', s=80, alpha=0.7, label='Simple DCA (37 purchases)',
                   marker='o', edgecolors='darkgreen', linewidth=1)

        # Buy the Dip purchases
        df_dip = pd.DataFrame(dip_purchases)
        ax3.scatter(df_dip['date'], df_dip['price'],
                   color='orange', s=120, alpha=0.7, label='Buy the Dip (24 purchases)',
                   marker='^', edgecolors='darkorange', linewidth=1.5)

        # Average prices
        ax3.axhline(y=dca_r['avg_cost'], color='green', linestyle='--',
                   linewidth=2, alpha=0.7, label=f'DCA Avg: ${dca_r["avg_cost"]:,.0f}')
        ax3.axhline(y=dip_r['avg_cost'], color='orange', linestyle='--',
                   linewidth=2, alpha=0.7, label=f'Dip Avg: ${dip_r["avg_cost"]:,.0f}')

        ax3.set_title('Purchase Points Comparison', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Date', fontsize=11)
        ax3.set_ylabel('Price (USD)', fontsize=11)
        ax3.legend(loc='best', fontsize=9)
        ax3.grid(True, alpha=0.3)

        # Chart 4: Investment Amount
        ax4 = fig.add_subplot(gs[2, 0])
        invested = [dca_r['total_invested'], dip_r['total_invested']]
        ax4.bar(strategies, invested, color=['steelblue', 'coral'],
               edgecolor='black', linewidth=2, alpha=0.7)
        ax4.set_title('Total Invested', fontsize=12, fontweight='bold')
        ax4.set_ylabel('THB', fontsize=10)
        ax4.grid(True, alpha=0.3, axis='y')

        for i, (strat, inv) in enumerate(zip(strategies, invested)):
            ax4.text(i, inv, f'{inv:,.0f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Chart 5: Average Buy Price
        ax5 = fig.add_subplot(gs[2, 1])
        avg_prices = [dca_r['avg_cost'], dip_r['avg_cost']]
        colors_avg = ['green' if avg_prices[0] < avg_prices[1] else 'orange',
                     'orange' if avg_prices[0] < avg_prices[1] else 'green']
        ax5.bar(strategies, avg_prices, color=colors_avg,
               edgecolor='black', linewidth=2, alpha=0.7)
        ax5.axhline(y=dca_r['current_price'], color='blue', linestyle='--',
                   linewidth=2, label=f'Current: ${dca_r["current_price"]:,.0f}')
        ax5.set_title('Average Buy Price', fontsize=12, fontweight='bold')
        ax5.set_ylabel('USD', fontsize=10)
        ax5.legend(fontsize=8)
        ax5.grid(True, alpha=0.3, axis='y')

        for i, (strat, price) in enumerate(zip(strategies, avg_prices)):
            ax5.text(i, price, f'${price:,.0f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Chart 6: Number of Purchases
        ax6 = fig.add_subplot(gs[2, 2])
        num_purchases = [dca_r['num_purchases'], dip_r['num_purchases']]
        ax6.bar(strategies, num_purchases, color=['purple', 'teal'],
               edgecolor='black', linewidth=2, alpha=0.7)
        ax6.set_title('Number of Purchases', fontsize=12, fontweight='bold')
        ax6.set_ylabel('Times', fontsize=10)
        ax6.grid(True, alpha=0.3, axis='y')

        for i, (strat, num) in enumerate(zip(strategies, num_purchases)):
            ax6.text(i, num, f'{num}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.suptitle('Strategy Comparison: Simple DCA vs Buy the Dip',
                    fontsize=18, fontweight='bold', y=0.995)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved comparison chart: {save_path}")

        plt.show()

    def export_comparison(self, output_path):
        """
        บันทึกการเปรียบเทียบเป็น CSV
        """
        if not self.results:
            print("No results available.")
            return

        dca_r = self.results['simple_dca']['results']
        dip_r = self.results['buy_the_dip']['results']

        comparison_data = {
            'Metric': [
                'Total BTC',
                'Total Invested (THB)',
                'Average Buy Price (USD)',
                'Number of Purchases',
                'Current Price (USD)',
                'Portfolio Value (THB)',
                'Return (%)',
                'Profit/Loss (THB)',
                'Capital Utilization (%)'
            ],
            'Simple_DCA': [
                dca_r['total_coins'],
                dca_r['total_invested'],
                dca_r['avg_cost'],
                dca_r['num_purchases'],
                dca_r['current_price'],
                dca_r['current_value'],
                dca_r['return_pct'],
                dca_r['total_return'],
                100.0
            ],
            'Buy_the_Dip': [
                dip_r['total_coins'],
                dip_r['total_invested'],
                dip_r['avg_cost'],
                dip_r['num_purchases'],
                dip_r['current_price'],
                dip_r['current_value'],
                dip_r['return_pct'],
                dip_r['total_return'],
                (dip_r['total_invested'] / dip_r['total_should_save'] * 100)
            ]
        }

        df_comparison = pd.DataFrame(comparison_data)

        # เพิ่มคอลัมน์ Winner
        df_comparison['Winner'] = ''
        df_comparison.loc[0, 'Winner'] = 'Simple DCA' if dca_r['total_coins'] > dip_r['total_coins'] else 'Buy the Dip'
        df_comparison.loc[2, 'Winner'] = 'Simple DCA' if dca_r['avg_cost'] < dip_r['avg_cost'] else 'Buy the Dip'
        df_comparison.loc[6, 'Winner'] = 'Simple DCA' if dca_r['return_pct'] > dip_r['return_pct'] else 'Buy the Dip'

        df_comparison.to_csv(output_path, index=False)
        print(f"✓ Saved comparison data: {output_path}")


def main():
    """
    ฟังก์ชันหลัก
    """
    print("\n" + "="*100)
    print("STRATEGY COMPARISON: SIMPLE DCA vs BUY THE DIP")
    print("="*100)

    # ตั้งค่า
    MONTHLY_INVESTMENT = 10000  # บาท
    DIP_THRESHOLD = -5.0
    DAY_OF_MONTH = 5

    # โหลดข้อมูล
    data_path = Path('../data/raw')
    csv_files = list(data_path.glob('*.csv'))

    if not csv_files:
        print("\n❌ No CSV files found in data/raw/")
        print("Please run binance_historical_data.py first")
        return

    latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
    print(f"\n📂 Loading data from: {latest_file.name}")

    df = pd.read_csv(latest_file, parse_dates=['timestamp'])
    df.set_index('timestamp', inplace=True)

    print(f"✓ Data loaded successfully")
    print(f"   - Period: {df.index.min().strftime('%Y-%m-%d')} to {df.index.max().strftime('%Y-%m-%d')}")
    print(f"   - Total records: {len(df):,}")

    # สร้าง comparison object
    comparison = StrategyComparison(df, monthly_investment=MONTHLY_INVESTMENT)

    # รันทุก strategies
    comparison.run_all_strategies(dip_threshold=DIP_THRESHOLD, day_of_month=DAY_OF_MONTH)

    # แสดงผลเปรียบเทียบ
    comparison.print_comparison()

    # สร้างกราฟ
    print("\n📊 Creating comparison charts...")
    output_dir = Path('../outputs/figures')
    output_dir.mkdir(parents=True, exist_ok=True)

    comparison.plot_comparison(save_path=output_dir / 'strategy_comparison.png')

    # บันทึกผลลัพธ์
    results_dir = Path('../outputs/reports')
    results_dir.mkdir(parents=True, exist_ok=True)

    comparison.export_comparison(results_dir / 'strategy_comparison.csv')

    print("\n" + "="*100)
    print("✓ Comparison completed successfully")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
