"""
Analyze August Performance - Deep Dive
Target File: data/raw/binance_20230107_20260105.csv
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Use a nice style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("tab10")

def analyze_august(file_path):
    print(f"\n📂 Loading data from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)

        # 1. Filter for August Data
        august_data = df[df.index.month == 8].copy()
        not_august_data = df[df.index.month != 8].copy()
        
        # Add day of month for analysis
        august_data['day'] = august_data.index.day
        august_data['year'] = august_data.index.year
        
        # Calculate Daily Returns
        august_data['daily_return'] = august_data['close'].pct_change() * 100
        # For the first day of August, pct_change might be NaN or wrong if it uses prev day (July 31).
        # But we want daily return relative to previous day close, so using whole df first is better.
        df['daily_return'] = df['close'].pct_change() * 100
        august_data['daily_return'] = df.loc[august_data.index, 'daily_return']
        not_august_data['daily_return'] = df.loc[not_august_data.index, 'daily_return']
        
        print("\n" + "="*60)
        print("📊 AUGUST VS REST OF YEAR STATS")
        print("="*60)
        
        avg_aug = august_data['daily_return'].mean()
        avg_rest = not_august_data['daily_return'].mean()
        vol_aug = august_data['daily_return'].std()
        vol_rest = not_august_data['daily_return'].std()
        
        print(f"Avg Daily Return (August): {avg_aug:.3f}%")
        print(f"Avg Daily Return (Rest):   {avg_rest:.3f}%")
        print(f"Volatility (August):       {vol_aug:.3f}%")
        print(f"Volatility (Rest):         {vol_rest:.3f}%")

        # --- Cumulative Return Analysis ---
        # Calculate cumulative return starting from Day 1 of August
        years = august_data['year'].unique()
        
        output_dir = Path('../outputs/eda_figures/august_analysis')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Cumulative Return Line Chart
        plt.figure(figsize=(12, 6))
        
        for year in years:
            year_data = august_data[august_data['year'] == year].copy()
            # Normalize to start at 0% change
            # Actually we want cumulative compound return
            # (1 + r1) * (1 + r2) ...
            cumulative_returns = (1 + year_data['daily_return'] / 100).cumprod() - 1
            cumulative_returns *= 100
            
            # Reindex to Day 1-31
            # Note: Available data might not start exactly at 1 or end at 31 if missing
            plt.plot(year_data['day'], cumulative_returns, marker='o', label=str(year), linewidth=2)
            
            final_return = cumulative_returns.iloc[-1]
            print(f"August {year} Total Return: {final_return:.2f}%")
        
        plt.title('August Cumulative Returns (Month-to-Date)', fontsize=14, fontweight='bold')
        plt.xlabel('Day of Month')
        plt.ylabel('Cumulative Return (%)')
        plt.axhline(0, color='black', linestyle='--')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(output_dir / 'august_cumulative_trend.png', dpi=300)
        print(f"✓ Saved chart: {output_dir / 'august_cumulative_trend.png'}")
        plt.close()
        
        # 2. Daily Seasonality (Avg Return per Day of Month)
        # Group by Day (1-31) and take mean
        daily_seasonality = august_data.groupby('day')['daily_return'].mean()
        
        plt.figure(figsize=(12, 6))
        colors = ['red' if x < 0 else 'green' for x in daily_seasonality]
        plt.bar(daily_seasonality.index, daily_seasonality, color=colors, alpha=0.7, edgecolor='black')
        plt.axhline(0, color='black', linewidth=1)
        plt.title('Average Daily Return in August (by Day of Month)', fontsize=14, fontweight='bold')
        plt.xlabel('Day of Month (1st - 31st)')
        plt.ylabel('Average Daily Return (%)')
        plt.xticks(range(1, 32))
        plt.grid(True, alpha=0.3, axis='y')
        
        # Highlight worst days
        worst_day = daily_seasonality.idxmin()
        worst_val = daily_seasonality.min()
        plt.annotate(f"Worst Day: {worst_day}th ({worst_val:.2f}%)", 
                     (worst_day, worst_val), xytext=(0, -20), textcoords='offset points', 
                     ha='center', arrowprops=dict(arrowstyle="->", color='red'))

        plt.savefig(output_dir / 'august_daily_seasonality.png', dpi=300)
        print(f"✓ Saved chart: {output_dir / 'august_daily_seasonality.png'}")
        plt.close()

        # 3. Volume Analysis (August vs Rest)
        # Normalize volume? Volume usually grows over years.
        # Let's compare Volume Mean of Aug vs Volume Mean of Rest *for each year*
        
        vol_stats = []
        for year in years:
            aug_vol = df[(df.index.month == 8) & (df.index.year == year)]['volume'].mean()
            rest_vol = df[(df.index.month != 8) & (df.index.year == year)]['volume'].mean()
            vol_stats.append({'Year': year, 'August Vol': aug_vol, 'Rest Vol': rest_vol})
            
        vol_df = pd.DataFrame(vol_stats)
        
        # Melt for seaborn barplot
        vol_melted = vol_df.melt(id_vars='Year', var_name='Period', value_name='Avg Volume')
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Year', y='Avg Volume', hue='Period', data=vol_melted, palette='Blues')
        plt.title('Trading Volume: August vs Rest of Year', fontsize=14, fontweight='bold')
        plt.ylabel('Average Daily Volume')
        plt.tight_layout()
        plt.savefig(output_dir / 'august_volume_comparison.png', dpi=300)
        print(f"✓ Saved chart: {output_dir / 'august_volume_comparison.png'}")
        plt.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    TARGET_FILE = "../data/raw/binance_20230107_20260105.csv"
    analyze_august(TARGET_FILE)
