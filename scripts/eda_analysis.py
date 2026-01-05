"""
EDA Analysis for Binance Historical Data
Target File: data/raw/binance_20230107_20260105.csv
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# ตั้งค่า Font ให้รองรับภาษาไทย (ถ้ามี) หรือใช้ default สวยๆ
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")

class CryptoEDA:
    def __init__(self, file_path):
        """
        Initialize with path to CSV file
        """
        self.file_path = Path(file_path)
        self.df = None
        self.output_dir = Path('../outputs/eda_figures')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_data(self):
        """
        Load and prepare data
        """
        print(f"📂 Loading data from: {self.file_path}")
        try:
            self.df = pd.read_csv(self.file_path)
            
            # Convert timestamp to datetime
            if 'timestamp' in self.df.columns:
                self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
                self.df.set_index('timestamp', inplace=True)
                
            # Calculate Return
            self.df['daily_return'] = self.df['close'].pct_change() * 100
            
            # Extract date features
            self.df['year'] = self.df.index.year
            self.df['month'] = self.df.index.month
            self.df['day_name'] = self.df.index.day_name()
            
            print(f"✓ Data loaded. Shape: {self.df.shape}")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False

    def generate_basic_stats(self):
        """
        Generate and print basic statistics
        """
        print("\n" + "="*50)
        print("📊 Basic Statistics")
        print("="*50)
        
        print(f"Period: {self.df.index.min().date()} to {self.df.index.max().date()}")
        print(f"Total Days: {len(self.df)}")
        
        print("\nPrice Statistics (USDT):")
        print(self.df[['open', 'high', 'low', 'close']].describe().round(2))
        
        print("\nChange Statistics:")
        print(f"Max Daily ROI: {self.df['daily_return'].max():.2f}%")
        print(f"Min Daily ROI: {self.df['daily_return'].min():.2f}%")
        print(f"Avg Daily ROI: {self.df['daily_return'].mean():.2f}%")
        print(f"Volatility (Std): {self.df['daily_return'].std():.2f}%")

    def plot_price_history(self):
        """
        Plot price history with Volume
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [3, 1]})
        
        # Price
        ax1.plot(self.df.index, self.df['close'], label='Close Price', color='#2E86C1')
        
        # Moving Averages
        self.df['MA7'] = self.df['close'].rolling(window=7).mean()
        self.df['MA30'] = self.df['close'].rolling(window=30).mean()
        
        ax1.plot(self.df.index, self.df['MA7'], label='7-Day MA', color='#E67E22', alpha=0.8, linewidth=1.5)
        ax1.plot(self.df.index, self.df['MA30'], label='30-Day MA', color='#C0392B', alpha=0.8, linewidth=1.5)
        
        ax1.set_title('BTC Price History with Moving Averages', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price (USDT)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Volume
        ax2.bar(self.df.index, self.df['volume'], color='gray', alpha=0.5, label='Volume')
        ax2.set_ylabel('Volume')
        ax2.set_xlabel('Date')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'price_history.png', dpi=300)
        print("✓ Saved price_history.png")
        plt.close()

    def plot_returns_distribution(self):
        """
        Plot distribution of daily returns
        """
        plt.figure(figsize=(12, 6))
        
        sns.histplot(self.df['daily_return'].dropna(), bins=50, kde=True, color='#27AE60')
        plt.axvline(x=0, color='black', linestyle='--', alpha=0.5)
        
        plt.title('Distribution of Daily Returns', fontsize=14, fontweight='bold')
        plt.xlabel('Daily Return (%)')
        plt.ylabel('Frequency')
        
        # Add stats box
        stats_text = (f"Mean: {self.df['daily_return'].mean():.2f}%\n"
                      f"Std: {self.df['daily_return'].std():.2f}%\n"
                      f"Skew: {self.df['daily_return'].skew():.2f}")
        
        plt.gca().text(0.95, 0.95, stats_text, transform=plt.gca().transAxes,
                       verticalalignment='top', horizontalalignment='right',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'returns_distribution.png', dpi=300)
        print("✓ Saved returns_distribution.png")
        plt.close()

    def plot_monthly_heatmap(self):
        """
        Plot monthly returns heatmap
        """
        # Calculate monthly returns
        monthly_returns = self.df['close'].resample('M').last().pct_change() * 100
        
        # Prepare pivot table for heatmap
        pivot_data = pd.DataFrame({
            'Year': monthly_returns.index.year,
            'Month': monthly_returns.index.month,
            'Return': monthly_returns.values
        })
        
        pivot_table = pivot_data.pivot(index='Year', columns='Month', values='Return')
        
        # Remap month numbers to names
        month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
                     7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        pivot_table.rename(columns=month_map, inplace=True)
        
        plt.figure(figsize=(12, 6))
        sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='RdYlGn', center=0, 
                    cbar_kws={'label': 'Return (%)'})
        
        plt.title('BTC Monthly Returns Heatmap (%)', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'monthly_heatmap.png', dpi=300)
        print("✓ Saved monthly_heatmap.png")
        plt.close()

    def plot_day_of_week_analysis(self):
        """
        Analyze returns by day of week
        """
        # Order days
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        avg_returns = self.df.groupby('day_name')['daily_return'].mean().reindex(days_order)
        volatility = self.df.groupby('day_name')['daily_return'].std().reindex(days_order)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Avg Return
        colors = ['green' if x > 0 else 'red' for x in avg_returns]
        avg_returns.plot(kind='bar', ax=ax1, color=colors, alpha=0.7)
        ax1.set_title('Average Return by Day of Week', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Average Return (%)')
        ax1.axhline(0, color='black', linewidth=0.5)
        
        # Volatility
        volatility.plot(kind='bar', ax=ax2, color='orange', alpha=0.7)
        ax2.set_title('Volatility (Risk) by Day of Week', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Standard Deviation (%)')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'day_of_week_analysis.png', dpi=300)
        print("✓ Saved day_of_week_analysis.png")
        plt.close()

    def run_analysis(self):
        """
        Run full analysis pipeline
        """
        if self.load_data():
            self.generate_basic_stats()
            
            print("\n📈 Generating plots...")
            self.plot_price_history()
            self.plot_returns_distribution()
            self.plot_monthly_heatmap()
            self.plot_day_of_week_analysis()
            
            print("\n" + "="*50)
            print(f"✨ Analysis Complete! Check outputs in: {self.output_dir}")
            print("="*50 + "\n")

if __name__ == "__main__":
    # Target File
    TARGET_FILE = "../data/raw/binance_20230107_20260105.csv"
    
    # Run EDA
    eda = CryptoEDA(TARGET_FILE)
    eda.run_analysis()
