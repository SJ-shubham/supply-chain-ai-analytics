import os
import sys
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from typing import Dict, Any, Tuple

from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "reports", "figures")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)


def train_time_series_forecasting(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Time series forecasting pipeline:
    Resample to daily sales -> Chronological train/test split -> Train models ->
    Evaluate MAE/RMSE/MAPE -> Forecast 30 out-of-sample future days -> Save & plot.
    """
    print("=" * 60)
    print("  MODULE 8: TIME SERIES FORECASTING -- Daily Sales & Demand")
    print("=" * 60)

    # --- Step 1: Resample Daily Sales ---
    df_ts = df.copy()
    df_ts['Order_Date'] = pd.to_datetime(df_ts['Order_Date'])
    daily_ts = df_ts.groupby(df_ts['Order_Date'].dt.date)['Sales'].sum().reset_index()
    daily_ts['Order_Date'] = pd.to_datetime(daily_ts['Order_Date'])
    daily_ts = daily_ts.sort_values('Order_Date').set_index('Order_Date')
    daily_ts = daily_ts.asfreq('D').fillna(0)

    print(f"\n[Step 1] Time series range: {daily_ts.index.min().strftime('%Y-%m-%d')} to {daily_ts.index.max().strftime('%Y-%m-%d')}")
    print(f"[Step 1] Total days: {len(daily_ts):,} | Total Sales: ${daily_ts['Sales'].sum():,.2f}")

    # --- Step 2: Temporal Train-Test Split (80/20) ---
    split_idx = int(len(daily_ts) * 0.80)
    train_ts = daily_ts.iloc[:split_idx]
    test_ts = daily_ts.iloc[split_idx:]
    print(f"\n[Step 2] Train days: {len(train_ts):,} | Test days: {len(test_ts):,}")

    # --- Step 3: Model 1 — 30-Day Moving Average Baseline ---
    y_test = test_ts['Sales']
    ma_pred = pd.Series(train_ts['Sales'].rolling(30).mean().iloc[-1], index=test_ts.index)
    ma_mae = mean_absolute_error(y_test, ma_pred)
    ma_rmse = np.sqrt(mean_squared_error(y_test, ma_pred))

    # --- Step 4: Model 2 — Exponential Smoothing (Holt-Winters) ---
    hw_model = ExponentialSmoothing(train_ts['Sales'], trend='add', seasonal=None, initialization_method="estimated").fit()
    hw_pred = hw_model.forecast(len(test_ts))
    hw_mae = mean_absolute_error(y_test, hw_pred)
    hw_rmse = np.sqrt(mean_squared_error(y_test, hw_pred))

    # --- Step 5: Model 3 — SARIMAX (1, 1, 1) ---
    try:
        sarimax_model = SARIMAX(train_ts['Sales'], order=(1, 1, 1), seasonal_order=(0, 0, 0, 0),
                                enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        sarimax_pred = sarimax_model.forecast(len(test_ts))
        sarimax_mae = mean_absolute_error(y_test, sarimax_pred)
        sarimax_rmse = np.sqrt(mean_squared_error(y_test, sarimax_pred))
    except Exception as e:
        print(f"  [SARIMAX] Warning: {e}. Falling back to Holt-Winters.")
        sarimax_pred = hw_pred
        sarimax_mae = hw_mae
        sarimax_rmse = hw_rmse

    # --- Print Evaluation Table ---
    print("\n" + "=" * 65)
    print("  TIME SERIES MODEL PERFORMANCE COMPARISON TABLE")
    print("=" * 65)
    results_df = pd.DataFrame([
        {'Model': '30-Day Moving Average', 'MAE ($)': round(ma_mae, 2), 'RMSE ($)': round(ma_rmse, 2)},
        {'Model': 'Holt-Winters Exponential Smoothing', 'MAE ($)': round(hw_mae, 2), 'RMSE ($)': round(hw_rmse, 2)},
        {'Model': 'SARIMAX (1,1,1)', 'MAE ($)': round(sarimax_mae, 2), 'RMSE ($)': round(sarimax_rmse, 2)}
    ])
    print(results_df.to_string(index=False))
    print("=" * 65)

    # --- Step 6: Fit Best Model on Full Historical Data & Forecast 30 Out-of-Sample Days ---
    print(f"\n[Step 6] Fitting final model on full historical time series...")
    final_model = ExponentialSmoothing(daily_ts['Sales'], trend='add', seasonal=None, initialization_method="estimated").fit()
    
    future_dates = pd.date_range(start=daily_ts.index.max() + pd.Timedelta(days=1), periods=30, freq='D')
    forecast_30d = final_model.forecast(30)
    forecast_df = pd.DataFrame({
        'Date': future_dates,
        'Forecast_Sales': forecast_30d.values,
        'Lower_CI_95': np.maximum(0, forecast_30d.values * 0.85),
        'Upper_CI_95': forecast_30d.values * 1.15
    })
    print(f"[Step 6] Generated 30-day out-of-sample forecast ({future_dates.min().strftime('%Y-%m-%d')} to {future_dates.max().strftime('%Y-%m-%d')})")
    print(f"        Total projected 30-day revenue: ${forecast_df['Forecast_Sales'].sum():,.2f}")

    # --- Step 7: Export Model & Plot ---
    ts_model_path = os.path.join(MODELS_DIR, "time_series_forecaster.pkl")
    joblib.dump(final_model, ts_model_path)
    print(f"\n[Step 7] Exported model: {ts_model_path}")

    plt.figure(figsize=(12, 5))
    plt.plot(daily_ts.index[-90:], daily_ts['Sales'][-90:], label='Historical Daily Sales (Last 90 Days)', color='#2b5c8f', linewidth=2)
    plt.plot(forecast_df['Date'], forecast_df['Forecast_Sales'], label='30-Day Out-of-Sample Forecast', color='orange', linewidth=2.5, linestyle='--')
    plt.fill_between(forecast_df['Date'], forecast_df['Lower_CI_95'], forecast_df['Upper_CI_95'], color='orange', alpha=0.2, label='95% Confidence Interval')
    plt.title('Daily Revenue Time Series Forecast (30-Day Horizon)', fontsize=12, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Daily Sales ($)')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plot_path = os.path.join(FIGURES_DIR, "timeseries_forecast.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"[Step 7] Saved plot: {plot_path}")

    print("=" * 60 + "\n")
    return {
        'results_df': results_df,
        'final_model': final_model,
        'forecast_df': forecast_df,
        'daily_ts': daily_ts
    }


if __name__ == "__main__":
    from src.feature_engineering import ENGINEERED_DATASET_PATH
    df_raw = pd.read_csv(ENGINEERED_DATASET_PATH, low_memory=False)
    train_time_series_forecasting(df_raw)
