import os
import pandas as pd
import numpy as np
from typing import Tuple

ENGINEERED_DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "engineered_features.csv")

def add_delivery_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer delivery delay variance, shipping speed ratio, and delay flags.
    """
    df = df.copy()
    print("[FeatureEngineering] Step 1: Adding Delivery & Logistics Metrics...")
    
    # 1. Delivery Delay Days
    if 'Days for shipping (real)' in df.columns and 'Days for shipment (scheduled)' in df.columns:
        df['Delivery_Delay_Days'] = df['Days for shipping (real)'] - df['Days for shipment (scheduled)']
        df['Is_Delayed'] = (df['Delivery_Delay_Days'] > 0).astype(int)
        df['Shipping_Speed_Ratio'] = (df['Days for shipping (real)'] / (df['Days for shipment (scheduled)'] + 0.001)).round(4)
        print("  • Added 'Delivery_Delay_Days', 'Is_Delayed', and 'Shipping_Speed_Ratio'.")
        
    return df


def add_financial_ratios(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer profit margins, discount impact ratios, unit price, and profitability flags.
    """
    df = df.copy()
    print("[FeatureEngineering] Step 2: Adding Financial & Profitability Ratios...")
    
    # 1. Profit Margin Percentage
    if 'Order Profit Per Order' in df.columns and 'Sales' in df.columns:
        df['Profit_Margin_Pct'] = np.where(df['Sales'] != 0, (df['Order Profit Per Order'] / df['Sales']) * 100, 0.0).round(2)
        df['Is_Profitable'] = (df['Order Profit Per Order'] > 0).astype(int)
        
    # 2. Discount Impact Ratio
    if 'Order Item Discount' in df.columns and 'Order Item Product Price' in df.columns and 'Order Item Quantity' in df.columns:
        total_list_price = df['Order Item Product Price'] * df['Order Item Quantity']
        df['Discount_Ratio'] = np.where(total_list_price != 0, df['Order Item Discount'] / total_list_price, 0.0).round(4)
        
    # 3. Effective Unit Price
    if 'Sales' in df.columns and 'Order Item Quantity' in df.columns:
        df['Effective_Unit_Price'] = np.where(df['Order Item Quantity'] != 0, df['Sales'] / df['Order Item Quantity'], df['Sales']).round(2)
        
    print("  • Added 'Profit_Margin_Pct', 'Is_Profitable', 'Discount_Ratio', and 'Effective_Unit_Price'.")
    return df


def add_customer_rfm_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer customer lifetime behavioral RFM features (Recency, Frequency, Monetary, AOV).
    """
    df = df.copy()
    print("[FeatureEngineering] Step 3: Computing Customer RFM & Lifetime Aggregations...")
    
    if 'Customer Id' in df.columns and 'Order_Date' in df.columns and 'Sales' in df.columns:
        # Convert Order_Date to datetime if needed
        df['Order_Date'] = pd.to_datetime(df['Order_Date'])
        max_date = df['Order_Date'].max()
        
        # Calculate RFM per customer
        customer_rfm = df.groupby('Customer Id').agg(
            Customer_Last_Date=('Order_Date', 'max'),
            Customer_Frequency=('Order Id', 'nunique'),
            Customer_Monetary=('Sales', 'sum'),
            Customer_Profit=('Order Profit Per Order', 'sum') if 'Order Profit Per Order' in df.columns else ('Sales', 'count')
        ).reset_index()
        
        # Recency in days
        customer_rfm['Customer_Recency'] = (max_date - customer_rfm['Customer_Last_Date']).dt.days
        customer_rfm['Customer_AOV'] = (customer_rfm['Customer_Monetary'] / customer_rfm['Customer_Frequency']).round(2)
        
        # Merge back to transaction dataframe
        rfm_cols_to_merge = ['Customer Id', 'Customer_Recency', 'Customer_Frequency', 'Customer_Monetary', 'Customer_AOV', 'Customer_Profit']
        df = df.merge(customer_rfm[rfm_cols_to_merge], on='Customer Id', how='left')
        print("  • Computed and merged Customer RFM Metrics: Customer_Recency, Customer_Frequency, Customer_Monetary, Customer_AOV.")
        
    return df


def add_operational_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer regional and mode late delivery rate scores.
    """
    df = df.copy()
    print("[FeatureEngineering] Step 4: Computing Regional & Node Operational Risk Scores...")
    
    # 1. Regional Late Delivery Rate
    if 'Order Region' in df.columns and 'Is_Delayed' in df.columns:
        regional_risk = df.groupby('Order Region')['Is_Delayed'].mean().reset_index().rename(columns={'Is_Delayed': 'Regional_Late_Rate'})
        regional_risk['Regional_Late_Rate'] = regional_risk['Regional_Late_Rate'].round(4)
        df = df.merge(regional_risk, on='Order Region', how='left')
        
    # 2. Shipping Mode Late Rate
    if 'Shipping Mode' in df.columns and 'Is_Delayed' in df.columns:
        mode_risk = df.groupby('Shipping Mode')['Is_Delayed'].mean().reset_index().rename(columns={'Is_Delayed': 'Shipping_Mode_Late_Rate'})
        mode_risk['Shipping_Mode_Late_Rate'] = mode_risk['Shipping_Mode_Late_Rate'].round(4)
        df = df.merge(mode_risk, on='Shipping Mode', how='left')
        
    print("  • Merged Operational Risk Indicators: Regional_Late_Rate, Shipping_Mode_Late_Rate.")
    return df


def run_full_feature_engineering_pipeline(cleaned_df: pd.DataFrame, save_output: bool = True, output_path: str = ENGINEERED_DATASET_PATH) -> pd.DataFrame:
    """
    Execute the full end-to-end feature engineering pipeline.
    """
    print("\n==================================================")
    print("  STARTING DOMAIN FEATURE ENGINEERING PIPELINE    ")
    print("==================================================")
    
    df = cleaned_df.copy()
    df = add_delivery_metrics(df)
    df = add_financial_ratios(df)
    df = add_customer_rfm_metrics(df)
    df = add_operational_risk_scores(df)
    
    print("\n--------------------------------------------------")
    print(f"Pipeline Complete! Final Dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns.")
    print("--------------------------------------------------")
    
    if save_output:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"[FeatureEngineering] Exporting engineered dataset to: {output_path}")
        df.to_csv(output_path, index=False)
        print("[FeatureEngineering] Export completed successfully!")
        
    print("==================================================\n")
    return df


if __name__ == "__main__":
    from preprocessing import CLEANED_DATASET_PATH
    if os.path.exists(CLEANED_DATASET_PATH):
        cleaned_df = pd.read_csv(CLEANED_DATASET_PATH, low_memory=False)
        run_full_feature_engineering_pipeline(cleaned_df)
    else:
        print(f"[Error] Cleaned dataset not found at: {CLEANED_DATASET_PATH}")