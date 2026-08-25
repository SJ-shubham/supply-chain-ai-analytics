import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

CLEANED_DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cleaned_supply_chain.csv")

def impute_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing values based on geographical mode and domain rules.
    """
    df = df.copy()
    print("[Preprocessing] Step 1: Imputing missing values...")
    
    # 1. Product Description: 100% missing -> Drop column
    if 'Product Description' in df.columns:
        df = df.drop(columns=['Product Description'])
        print("  • Dropped 'Product Description' (100% missing).")
        
    # 2. Customer Lname: Impute 8 missing values with 'Unknown'
    if 'Customer Lname' in df.columns:
        df['Customer Lname'] = df['Customer Lname'].fillna('Unknown')
        print("  • Imputed 'Customer Lname' missing values with 'Unknown'.")
        
    # 3. Customer Zipcode: Convert to string, then impute using mode grouped by Customer City / State
    if 'Customer Zipcode' in df.columns:
        # Convert numeric float zipcodes to string (e.g. 725.0 -> '725')
        df['Customer Zipcode'] = df['Customer Zipcode'].apply(lambda x: str(int(x)) if pd.notnull(x) and isinstance(x, (int, float)) and x == x else ('Unknown' if pd.isnull(x) else str(x)))
        if (df['Customer Zipcode'] == 'Unknown').sum() > 0:
            mode_zip = df.groupby(['Customer State', 'Customer City'])['Customer Zipcode'].transform(lambda x: x.mode()[0] if not x.mode().empty and x.mode()[0] != 'Unknown' else '00000')
            df['Customer Zipcode'] = df['Customer Zipcode'].replace('Unknown', np.nan).fillna(mode_zip).fillna('00000')
        print("  • Imputed 'Customer Zipcode' missing values using geographical mode.")
        
    # 4. Order Zipcode: 86% missing -> Convert to string, impute using mode or 'Unknown'
    if 'Order Zipcode' in df.columns:
        df['Order Zipcode'] = df['Order Zipcode'].apply(lambda x: str(int(x)) if pd.notnull(x) and isinstance(x, (int, float)) and x == x else ('Unknown' if pd.isnull(x) else str(x)))
        print("  • Imputed 'Order Zipcode' missing values with location-aware placeholders.")
        
    return df


def sanitize_pii_and_prune(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sanitize sensitive Personally Identifiable Information (PII) and non-analytical columns.
    """
    df = df.copy()
    print("[Preprocessing] Step 2: Sanitizing PII and pruning unnecessary attributes...")
    
    # Merge Customer Fname and Customer Lname into Customer_Full_Name
    if 'Customer Fname' in df.columns and 'Customer Lname' in df.columns:
        df['Customer_Full_Name'] = df['Customer Fname'].astype(str).str.strip() + " " + df['Customer Lname'].astype(str).str.strip()
        
    pii_cols_to_drop = ['Customer Email', 'Customer Password', 'Customer Street', 'Product Image', 'Customer Fname', 'Customer Lname']
    existing_pii_drops = [c for c in pii_cols_to_drop if c in df.columns]
    
    if existing_pii_drops:
        df = df.drop(columns=existing_pii_drops)
        print(f"  • Dropped PII & Non-Analytical Columns: {existing_pii_drops}")
        
    return df


def parse_dates_and_extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse date strings into datetime objects and extract temporal attributes.
    """
    df = df.copy()
    print("[Preprocessing] Step 3: Parsing dates and extracting temporal features...")
    
    if 'order date (DateOrders)' in df.columns:
        df['Order_Date'] = pd.to_datetime(df['order date (DateOrders)'], format='%m/%d/%Y %H:%M', errors='coerce')
        df = df.drop(columns=['order date (DateOrders)'])
        
        # Derive temporal tokens
        df['Order_Year'] = df['Order_Date'].dt.year
        df['Order_Month'] = df['Order_Date'].dt.month
        df['Order_Month_Name'] = df['Order_Date'].dt.strftime('%b')
        df['Order_DayOfWeek'] = df['Order_Date'].dt.dayofweek
        df['Order_Day_Name'] = df['Order_Date'].dt.strftime('%a')
        df['Order_Hour'] = df['Order_Date'].dt.hour
        df['Order_Quarter'] = df['Order_Date'].dt.quarter
        print("  • Extracted temporal features: Order_Year, Order_Month, Order_DayOfWeek, Order_Hour, etc.")
        
    if 'shipping date (DateOrders)' in df.columns:
        df['Shipping_Date'] = pd.to_datetime(df['shipping date (DateOrders)'], format='%m/%d/%Y %H:%M', errors='coerce')
        df = df.drop(columns=['shipping date (DateOrders)'])
        print("  • Standardized 'Shipping_Date' datetime.")
        
    return df


def standardize_text_and_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize text formatting, strip whitespace, and enforce clean data types.
    """
    df = df.copy()
    print("[Preprocessing] Step 4: Standardizing text formatting and data types...")
    
    string_cols = df.select_dtypes(include=['object', 'string']).columns
    for c in string_cols:
        df[c] = df[c].astype(str).str.strip()
        
    if 'Late_delivery_risk' in df.columns:
        df['Late_delivery_risk'] = df['Late_delivery_risk'].astype(int)
        
    return df


def detect_and_handle_outliers(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Perform statistical outlier auditing using IQR and Z-Score, and validate domain bounds.
    """
    df = df.copy()
    print("[Preprocessing] Step 5: Outlier auditing and domain validation...")
    
    outlier_audit = {}
    numeric_cols_to_check = ['Sales', 'Order Profit Per Order', 'Order Item Quantity', 'Days for shipping (real)']
    
    for col in numeric_cols_to_check:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            iqr_outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            
            mean_val = df[col].mean()
            std_val = df[col].std()
            z_scores = (df[col] - mean_val) / (std_val + 1e-9)
            z_outliers = df[np.abs(z_scores) > 3.0]
            
            outlier_audit[col] = {
                "Q1": round(Q1, 2),
                "Q3": round(Q3, 2),
                "IQR": round(IQR, 2),
                "IQR_Lower_Bound": round(lower_bound, 2),
                "IQR_Upper_Bound": round(upper_bound, 2),
                "IQR_Outliers_Count": len(iqr_outliers),
                "IQR_Outliers_Pct": round(len(iqr_outliers) / len(df) * 100, 2),
                "ZScore_Outliers_Count": len(z_outliers)
            }
            print(f"  • {col}: IQR Bounds [{lower_bound:.2f}, {upper_bound:.2f}] -> {len(iqr_outliers):,} outliers ({outlier_audit[col]['IQR_Outliers_Pct']}%)")
            
    # Domain Integrity Rule Validation:
    invalid_shipping = df[df['Days for shipping (real)'] < 0]
    if len(invalid_shipping) > 0:
        print(f"  [Warning] Found {len(invalid_shipping)} records with negative shipping days. Filtering invalid records.")
        df = df[df['Days for shipping (real)'] >= 0]
        
    invalid_sales = df[df['Sales'] < 0]
    if len(invalid_sales) > 0:
        print(f"  [Warning] Found {len(invalid_sales)} records with negative sales. Filtering invalid records.")
        df = df[df['Sales'] >= 0]
        
    return df, outlier_audit


def run_full_cleaning_pipeline(raw_df: pd.DataFrame, save_output: bool = True, output_path: str = CLEANED_DATASET_PATH) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run the full end-to-end data cleaning pipeline.
    """
    print("\n==================================================")
    print("      STARTING END-TO-END DATA CLEANING PIPELINE  ")
    print("==================================================")
    
    df = raw_df.copy()
    df = impute_missing_values(df)
    df = sanitize_pii_and_prune(df)
    df = parse_dates_and_extract_features(df)
    df = standardize_text_and_types(df)
    df, outlier_report = detect_and_handle_outliers(df)
    
    total_nulls = df.isnull().sum().sum()
    print("\n--------------------------------------------------")
    print(f"Pipeline Complete! Final Dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns.")
    print(f"Total Remaining Null Values: {total_nulls}")
    print("--------------------------------------------------")
    
    if save_output:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"[Preprocessing] Exporting cleaned dataset to: {output_path}")
        df.to_csv(output_path, index=False)
        print("[Preprocessing] Export completed successfully!")
        
    print("==================================================\n")
    return df, outlier_report


if __name__ == "__main__":
    from data_loader import load_raw_dataset
    raw_df = load_raw_dataset()
    cleaned_df, report = run_full_cleaning_pipeline(raw_df)
