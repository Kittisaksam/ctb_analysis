"""
Analyze Monthly Seasonality Patterns
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

def analyze_seasonality(file_path):
    print(f"\n📂 Loading data from: {file_path}")
    try:
        df = pd.read_csv(file_path)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)

        # Resample to Monthly Returns
        # We need end of month close vs previous end of month close
        monthly_close = df['close'].resample('ME').last()
        monthly_returns = monthly_close.pct_change() * 100
        
        # Create DataFrame for Pivot
        seasonality_df = pd.DataFrame({
            'Return': monthly_returns,
            'Year': monthly_returns.index.year,
            'Month': monthly_returns.index.month,
            'Month Name': monthly_returns.index.strftime('%b')
        })
        
        # Remove first row (NaN from pct_change)
        seasonality_df.dropna(inplace=True)

        # Pivot: Month vs Year
        pivot_table = seasonality_df.pivot(index='Month', columns='Year', values='Return')
        
        # Map element numbers to names for display
        month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
                       7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        pivot_table.index = pivot_table.index.map(month_names)

        # Calculate Statistics
        stats = pd.DataFrame(index=pivot_table.index)
        stats['Win Rate (%)'] = pivot_table.apply(lambda x: (x > 0).sum() / x.count() * 100, axis=1)
        stats['Avg Return (%)'] = pivot_table.mean(axis=1)
        stats['Median Return (%)'] = pivot_table.median(axis=1)
        
        print("\n" + "="*60)
        print("📊 MONTHLY SEASONALITY STATISTICS")
        print("="*60)
        print(stats.round(2).to_string())
        
        # Export Stats
        output_report = Path('../outputs/reports/monthly_seasonality.csv')
        output_report.parent.mkdir(parents=True, exist_ok=True)
        stats.to_csv(output_report)
        print(f"\n✓ Saved stats to: {output_report}")

        # --- Visualizations ---
        output_dir = Path('../outputs/eda_figures')
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='RdYlGn', center=0, 
                    linewidths=1, linecolor='white')
        plt.title('Bitcoin Monthly Returns Heatmap (%)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_dir / 'seasonality_heatmap.png', dpi=300)
        print(f"✓ Saved chart: {output_dir / 'seasonality_heatmap.png'}")
        plt.close()

        # 2. Win Rate Bar Chart
        plt.figure(figsize=(10, 6))
        
        # Color bars based on win rate intensity
        colors = plt.cm.RdYlGn(stats['Win Rate (%)'] / 100)
        
        bars = plt.bar(stats.index, stats['Win Rate (%)'], color=colors, edgecolor='black', alpha=0.8)
        plt.axhline(50, color='black', linestyle='--', linewidth=1, alpha=0.5)
        plt.title('Monthly Win Rate (% of Positive Years)', fontsize=14, fontweight='bold')
        plt.ylabel('Win Rate (%)')
        plt.ylim(0, 100)
        
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.0f}%', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_dir / 'monthly_win_rate.png', dpi=300)
        print(f"✓ Saved chart: {output_dir / 'monthly_win_rate.png'}")
        plt.close()

        # 3. Avg Return Bar Chart
        plt.figure(figsize=(10, 6))
        colors = ['#2ECC71' if x > 0 else '#E74C3C' for x in stats['Avg Return (%)']]
        
        bars = plt.bar(stats.index, stats['Avg Return (%)'], color=colors, edgecolor='black', alpha=0.8)
        plt.axhline(0, color='black', linewidth=1)
        plt.title('Average Monthly Return (%)', fontsize=14, fontweight='bold')
        plt.ylabel('Average Return (%)')
        
        for bar, val in zip(bars, stats['Avg Return (%)']):
            height = bar.get_height()
            xy_pos = height if height > 0 else 0
            va_pos = 'bottom' if height > 0 else 'bottom' # Put text above 0 line for negative? No, put near bar end
            
            # Simple offset label
            label_y = height if height > 0 else height - 1.5
            plt.text(bar.get_x() + bar.get_width()/2., label_y,
                     f'{val:.1f}%', ha='center', va='bottom' if height > 0 else 'top', 
                     fontweight='bold', color='black')

        plt.tight_layout()
        plt.savefig(output_dir / 'monthly_avg_return.png', dpi=300)
        print(f"✓ Saved chart: {output_dir / 'monthly_avg_return.png'}")
        plt.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    TARGET_FILE = "../data/raw/binance_20230107_20260105.csv"
    analyze_seasonality(TARGET_FILE)
