import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

def load_raw_dataset(file_path: str = None, encoding: str = 'latin1') -> pd.DataFrame:
    """
    Load raw DataCo Smart Supply Chain Dataset from CSV.
    """
    if file_path is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate_paths = [
            os.path.join(root_dir, "data", "DataCoSupplyChainDataset.csv"),
            os.path.join(root_dir, "DataCoSupplyChainDataset.csv"),
            os.path.join(os.getcwd(), "data", "DataCoSupplyChainDataset.csv"),
            os.path.join(os.getcwd(), "DataCoSupplyChainDataset.csv")
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                file_path = p
                break
                
    if file_path is None or not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file 'DataCoSupplyChainDataset.csv' not found. Checked candidate paths.")
        
    print(f"[DataLoader] Ingesting dataset from: {file_path}")
    df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
    print(f"[DataLoader] Successfully loaded dataset. Dimensions: {df.shape[0]:,} rows × {df.shape[1]} columns.")
    return df


def audit_dataset_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform a complete schema and quality audit on the loaded DataFrame.
    
    Parameters:
        df (pd.DataFrame): Dataset to audit
        
    Returns:
        dict: High-level dataset summary metrics
    """
    total_rows, total_cols = df.shape
    missing_summary = df.isnull().sum()
    missing_cols = missing_summary[missing_summary > 0].to_dict()
    
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    
    audit_results = {
        "total_rows": total_rows,
        "total_columns": total_cols,
        "numerical_column_count": len(num_cols),
        "categorical_column_count": len(cat_cols),
        "missing_columns_count": len(missing_cols),
        "missing_columns_detail": missing_cols,
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    }
    
    print("\n" + "="*50)
    print("      DATACO SUPPLY CHAIN DATASET AUDIT REPORT      ")
    print("="*50)
    print(f"Total Transactions (Rows) : {audit_results['total_rows']:,}")
    print(f"Total Attributes (Cols)  : {audit_results['total_columns']}")
    print(f"Numerical Columns        : {audit_results['numerical_column_count']}")
    print(f"Categorical Columns      : {audit_results['categorical_column_count']}")
    print(f"Memory Footprint         : {audit_results['memory_usage_mb']} MB")
    print(f"Columns with Missing Values: {audit_results['missing_columns_count']}")
    
    if missing_cols:
        print("\n--- Missing Value Breakdown ---")
        for col, count in missing_cols.items():
            pct = (count / total_rows) * 100
            print(f"  • {col}: {count:,} missing ({pct:.2f}%)")
    print("="*50 + "\n")
    
    return audit_results


if __name__ == "__main__":
    df = load_raw_dataset()
    audit_dataset_schema(df)