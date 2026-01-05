"""
Analyze Worst Price Drops
Target File: data/raw/binance_20230107_20260105.csv
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Use a nice style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("RdYlGn")

def calculate_max_drawdown(prices):
    """
    Calculate Max Drawdown for a series of prices.
    Ref: (Running Max - Current Value) / Running Max
    """
    # Use 'high' for running max and 'low' for current value to catch intra-day crashes?
    # Or just use 'close' for simplicity?
    # Let's use High and Low for intra-month accuracy if passed dataframe, 
    # but here we might just get a series.
    # To be safe and simple for monthly resolution:
    # We will compute Peak-to-Trough using daily highs and lows if available.
    return 0.0

def plot_drops(results_df, output_dir):
    """
    Generate visualizations for price drops
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Bar Chart: Worst Monthly Returns
    plt.figure(figsize=(12, 6))
    worst_returns = results_df.sort_values('Return (%)', ascending=True).head(10)
    
    sns.barplot(x='Return (%)', y='Period', data=worst_returns, palette='Reds_r')
    plt.title('Top 10 Months with Worst Returns', fontsize=14, fontweight='bold')
    plt.xlabel('Return (%)')
    plt.ylabel('Month')
    plt.axvline(0, color='black', linewidth=1)
    
    for i, v in enumerate(worst_returns['Return (%)']):
        plt.text(v - 0.5, i, f'{v:.2f}%', va='center', fontweight='bold', color='black') # adjust x offset

    plt.tight_layout()
    plt.savefig(output_dir / 'worst_monthly_returns.png', dpi=300)
    print(f"✓ Saved chart: {output_dir / 'worst_monthly_returns.png'}")
    plt.close()

    # 2. Bar Chart: Deepest Drawdowns
    plt.figure(figsize=(12, 6))
    worst_drawdowns = results_df.sort_values('Max Drawdown (%)', ascending=True).head(10)
    
    sns.barplot(x='Max Drawdown (%)', y='Period', data=worst_drawdowns, palette='Oranges_r')
    plt.title('Top 10 Months with Deepest Max Drawdowns', fontsize=14, fontweight='bold')
    plt.xlabel('Max Drawdown (%)')
    plt.ylabel('Month')
    
    for i, v in enumerate(worst_drawdowns['Max Drawdown (%)']):
        plt.text(v - 0.5, i, f'{v:.2f}%', va='center', fontweight='bold', color='black')

    plt.tight_layout()
    plt.savefig(output_dir / 'deepest_drawdowns.png', dpi=300)
    print(f"✓ Saved chart: {output_dir / 'deepest_drawdowns.png'}")
    plt.close()

    # 3. Scatter Plot: Risk vs Reward (Drawdown vs Return)
    plt.figure(figsize=(10, 8))
    sns.scatterplot(x='Max Drawdown (%)', y='Return (%)', data=results_df, 
                    hue='Return (%)', palette='RdYlGn', s=100, edgecolor='black', alpha=0.8)
    
    plt.title('Monthly Risk vs Reward (Max Drawdown vs Return)', fontsize=14, fontweight='bold')
    plt.xlabel('Max Drawdown (%)')
    plt.ylabel('Monthly Return (%)')
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.grid(True, alpha=0.3)
    
    # Label outliers (e.g., worst return, best return)
    worst_return = results_df.nsmallest(1, 'Return (%)').iloc[0]
    best_return = results_df.nlargest(1, 'Return (%)').iloc[0]
    worst_drawdown = results_df.nsmallest(1, 'Max Drawdown (%)').iloc[0]

    plt.annotate(f"{worst_return['Period']}\n{worst_return['Return (%)']:.1f}%", 
                 (worst_return['Max Drawdown (%)'], worst_return['Return (%)']),
                 xytext=(10, 10), textcoords='offset points', arrowprops=dict(arrowstyle="->", color='red'))
                 
    plt.annotate(f"{best_return['Period']}\n+{best_return['Return (%)']:.1f}%", 
                 (best_return['Max Drawdown (%)'], best_return['Return (%)']),
                 xytext=(10, -20), textcoords='offset points', arrowprops=dict(arrowstyle="->", color='green'))

    plt.tight_layout()
    plt.savefig(output_dir / 'risk_vs_reward_scatter.png', dpi=300)
    print(f"✓ Saved chart: {output_dir / 'risk_vs_reward_scatter.png'}")
    plt.close()


def analyze_drops(file_path):
    print(f"\n📂 Loading data from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
        # Ensure we have required columns
        required_cols = ['open', 'high', 'low', 'close']
        if not all(col in df.columns for col in required_cols):
            print("❌ Missing required columns (open, high, low, close)")
            return

        # Add Year-Month column
        df['year_month'] = df.index.to_period('M')
        
        results = []
        
        # Group by Month
        for period, group in df.groupby('year_month'):
            # 1. Monthly Return (Close vs Open)
            open_price = group['open'].iloc[0]
            close_price = group['close'].iloc[-1]
            monthly_return = ((close_price - open_price) / open_price) * 100
            
            # 2. Max Drawdown (Peak to Trough within the month)
            # We calculate rolling max of 'high', then find max % drop to 'low'
            rolling_max = group['high'].cummax()
            daily_drawdown = (group['low'] - rolling_max) / rolling_max * 100
            max_drawdown = daily_drawdown.min() # min because it's negative
            
            # 3. Max Single Day Drop
            group = group.copy() # Avoid SettingWithCopyWarning
            group['daily_drop'] = ((group['close'] - group['open']) / group['open']) * 100
            max_daily_drop = group['daily_drop'].min()
            
            results.append({
                'Period': str(period),
                'Open': open_price,
                'Close': close_price,
                'Return (%)': monthly_return,
                'Max Drawdown (%)': max_drawdown,
                'Max Daily Drop (%)': max_daily_drop
            })
            
        # Create DataFrame
        results_df = pd.DataFrame(results)
        
        # Sort by Worst Return
        worst_returns = results_df.sort_values('Return (%)', ascending=True)
        
        print("\n" + "="*80)
        print("📉 TOP 10 MONTHS WITH WORST RETURNS (ราคาปิด ย่ำแย่ที่สุดเมื่อเทียบกับเปิดเดือน)")
        print("="*80)
        print(worst_returns[['Period', 'Return (%)', 'Max Drawdown (%)', 'Open', 'Close']].head(10).to_string(index=False))
        
        # Sort by Max Drawdown
        worst_drawdowns = results_df.sort_values('Max Drawdown (%)', ascending=True)
        
        print("\n" + "="*80)
        print("🎢 TOP 10 MONTHS WITH WORST DRAWDOWNS (ราคาร่วงหนักสุดระหว่างเดือน)")
        print("="*80)
        print(worst_drawdowns[['Period', 'Max Drawdown (%)', 'Return (%)', 'Max Daily Drop (%)']].head(10).to_string(index=False))
        
        # Export
        output_path = Path('../outputs/reports/monthly_drops_analysis.csv')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(output_path, index=False)
        print(f"\n✓ Saved full report to: {output_path}")

        # Visualization
        print("\n📊 Generating visualization charts...")
        plot_drops(results_df, '../outputs/eda_figures')

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    TARGET_FILE = "../data/raw/binance_20230107_20260105.csv"
    analyze_drops(TARGET_FILE)
