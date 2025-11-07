"""Exploratory data analysis for the Cars dataset.

Generates several PNG figures into `reports/figures/`:
 - price_hist.png
 - log_price_hist.png
 - horsepower_vs_price.png
 - company_price_boxplot.png
 - numeric_corr_heatmap.png

Run:
    python src/personal_project/eda_cars.py
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
try:
    from personal_project.cleaning import parse_price, extract_number
except Exception:
    # Support running this file directly (python src/personal_project/eda_cars.py)
    # by loading the cleaning module from the same directory.
    import importlib.util, sys
    p = Path(__file__).resolve().parent / 'cleaning.py'
    spec = importlib.util.spec_from_file_location('personal_project.cleaning', str(p))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    parse_price = mod.parse_price
    extract_number = mod.extract_number


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "Cars Datasets 2025.csv"
OUT_DIR = Path(__file__).resolve().parents[2] / "reports" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# parsing functions are provided by personal_project.cleaning


def load_clean():
    df = pd.read_csv(DATA_PATH, encoding='latin1')
    df.columns = [c.strip() for c in df.columns]

    df['price'] = df.get('Cars Prices', '').apply(parse_price)
    df['horsepower'] = df.get('HorsePower', '').apply(extract_number)
    df['cc'] = df.get('CC/Battery Capacity', '').apply(extract_number)
    df['perf_sec'] = df.get('Performance(0 - 100 )KM/H', '').apply(extract_number)
    df['torque'] = df.get('Torque', '').apply(extract_number)
    df['seats'] = pd.to_numeric(df.get('Seats', ''), errors='coerce')

    return df


def plot_price_hist(df: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    sns.histplot(df['price'].dropna(), bins=50)
    plt.title('Price distribution')
    plt.xlabel('Price (USD)')
    plt.tight_layout()
    out = OUT_DIR / 'price_hist.png'
    plt.savefig(out)
    plt.close()


def _format_axis_currency(ax, axis='x', divide=1):
    """Format axis ticks with thousands separator.

    Parameters:
    - ax: matplotlib Axes
    - axis: 'x' or 'y'
    - divide: divide value for scaling (e.g., 1000 to show thousands)
    """
    def _fmt(x, pos):
        try:
            val = x / divide
            if abs(val) >= 1000:
                # keep integer formatting for large numbers
                return f"{int(val):,}"
            # otherwise show without decimals if whole, else 1 decimal
            if float(val).is_integer():
                return f"{int(val):,}"
            return f"{val:,.1f}"
        except Exception:
            return f"{x}"

    fmt = FuncFormatter(_fmt)
    if axis == 'x':
        ax.xaxis.set_major_formatter(fmt)
    else:
        ax.yaxis.set_major_formatter(fmt)


def plot_log_price_hist(df: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    # use log10 for easier interpretation and drop non-positive prices
    price = df['price'].dropna()
    price = price[price > 0]
    log_price = np.log10(price)
    sns.histplot(log_price, bins=50)
    plt.title('Log10(Price) distribution')
    plt.xlabel('log10(Price)')
    plt.tight_layout()
    out = OUT_DIR / 'log_price_hist.png'
    plt.savefig(out)
    plt.close()


def plot_hp_vs_price(df: pd.DataFrame):
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='horsepower', y='price', data=df, alpha=0.6)
    plt.title('Horsepower vs Price')
    plt.xlabel('Horsepower')
    plt.ylabel('Price (USD)')
    plt.tight_layout()
    out = OUT_DIR / 'horsepower_vs_price.png'
    ax = plt.gca()
    # format y-axis with thousands separator
    _format_axis_currency(ax, axis='y', divide=1)
    plt.savefig(out)
    plt.close()


def plot_company_boxplot(df: pd.DataFrame, top_n=10):
    counts = df['Company Names'].value_counts()
    top = counts.nlargest(top_n).index.tolist()
    sub = df[df['Company Names'].isin(top)]
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Company Names', y='price', data=sub)
    plt.xticks(rotation=45)
    plt.title(f'Price distribution by top {top_n} companies')
    plt.tight_layout()
    out = OUT_DIR / 'company_price_boxplot.png'
    ax = plt.gca()
    _format_axis_currency(ax, axis='y', divide=1)
    plt.savefig(out)
    plt.close()


def plot_numeric_corr(df: pd.DataFrame):
    num = df[['price', 'horsepower', 'cc', 'perf_sec', 'torque', 'seats']].copy()
    corr = num.corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm')
    plt.title('Numeric feature correlation')
    plt.tight_layout()
    out = OUT_DIR / 'numeric_corr_heatmap.png'
    plt.savefig(out)
    plt.close()


def main():
    df = load_clean()
    print('Rows loaded:', len(df))
    print('Saving figures to', OUT_DIR)

    plot_price_hist(df)
    plot_log_price_hist(df)
    plot_hp_vs_price(df)
    plot_company_boxplot(df)
    plot_numeric_corr(df)

    print('Done')


if __name__ == '__main__':
    main()
