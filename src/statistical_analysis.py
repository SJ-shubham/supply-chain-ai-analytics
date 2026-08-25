import os
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, Tuple

def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute comprehensive descriptive statistics (Mean, Median, Mode, Std Dev, Variance, IQR, Skewness, Kurtosis).
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    stats_list = []
    
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
            
        mean_val = series.mean()
        median_val = series.median()
        mode_val = series.mode()[0] if not series.mode().empty else np.nan
        std_val = series.std()
        var_val = series.var()
        min_val = series.min()
        max_val = series.max()
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr_val = q3 - q1
        skew_val = series.skew()
        kurt_val = series.kurtosis()
        
        stats_list.append({
            "Feature": col,
            "Count": len(series),
            "Mean": round(mean_val, 2),
            "Median": round(median_val, 2),
            "Mode": round(mode_val, 2) if pd.notnull(mode_val) else np.nan,
            "Std_Dev": round(std_val, 2),
            "Variance": round(var_val, 2),
            "Min": round(min_val, 2),
            "Q1": round(q1, 2),
            "Q3": round(q3, 2),
            "IQR": round(iqr_val, 2),
            "Max": round(max_val, 2),
            "Skewness": round(skew_val, 2),
            "Kurtosis": round(kurt_val, 2)
        })
        
    return pd.DataFrame(stats_list)


def run_chi_square_test(df: pd.DataFrame, cat_col1: str = 'Shipping Mode', cat_col2: str = 'Late_delivery_risk') -> Dict[str, Any]:
    """
    Execute Chi-Square Test of Independence between two categorical attributes.
    H0: cat_col1 and cat_col2 are independent.
    H1: cat_col1 and cat_col2 are significantly dependent.
    """
    print(f"\n[Stats] Running Chi-Square Test: '{cat_col1}' vs '{cat_col2}'...")
    contingency_table = pd.crosstab(df[cat_col1], df[cat_col2])
    chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)
    
    result = {
        "Test_Name": f"Chi-Square Test ({cat_col1} vs {cat_col2})",
        "Chi2_Statistic": round(chi2, 4),
        "P_Value": p_val,
        "Degrees_of_Freedom": dof,
        "Is_Significant_Alpha_05": p_val < 0.05,
        "Null_Hypothesis_Status": "REJECTED (Variables are dependent)" if p_val < 0.05 else "FAIL TO REJECT (Variables are independent)"
    }
    
    print(f"  • Chi2 Statistic: {result['Chi2_Statistic']}, DOF: {dof}, P-Value: {p_val:.4e}")
    print(f"  • Decision at alpha=0.05: {result['Null_Hypothesis_Status']}")
    return result


def run_anova_test(df: pd.DataFrame, num_col: str = 'Days for shipping (real)', cat_col: str = 'Market') -> Dict[str, Any]:
    """
    Execute One-Way ANOVA test across categories of a factor variable.
    H0: Mean of num_col is equal across all categories of cat_col.
    H1: At least one category has a significantly different mean num_col.
    """
    print(f"\n[Stats] Running One-Way ANOVA Test: '{num_col}' across '{cat_col}'...")
    groups = [group[num_col].dropna().values for _, group in df.groupby(cat_col)]
    f_stat, p_val = stats.f_oneway(*groups)
    
    result = {
        "Test_Name": f"One-Way ANOVA ({num_col} by {cat_col})",
        "F_Statistic": round(f_stat, 4),
        "P_Value": p_val,
        "Group_Count": len(groups),
        "Is_Significant_Alpha_05": p_val < 0.05,
        "Null_Hypothesis_Status": "REJECTED (Means differ significantly across groups)" if p_val < 0.05 else "FAIL TO REJECT (Means are equal)"
    }
    
    print(f"  • F-Statistic: {result['F_Statistic']}, Groups: {len(groups)}, P-Value: {p_val:.4e}")
    print(f"  • Decision at alpha=0.05: {result['Null_Hypothesis_Status']}")
    return result


def run_ttest(df: pd.DataFrame, num_col: str = 'Profit_Margin_Pct', discount_col: str = 'Discount_Ratio', threshold: float = 0.15) -> Dict[str, Any]:
    """
    Execute Two-Sample Independent Welch's T-Test comparing high discount vs low discount orders.
    H0: Mean num_col is equal for high discount and low discount orders.
    H1: Mean num_col for high discount orders is significantly lower.
    """
    print(f"\n[Stats] Running Welch's T-Test: '{num_col}' for High Discount (>= {threshold*100}%) vs Low Discount (< {threshold*100}%)...")
    
    high_disc = df[df[discount_col] >= threshold][num_col].dropna()
    low_disc = df[df[discount_col] < threshold][num_col].dropna()
    
    t_stat, p_val = stats.ttest_ind(high_disc, low_disc, equal_var=False)
    
    result = {
        "Test_Name": f"Welch's T-Test ({num_col} by High/Low Discount)",
        "High_Discount_Mean": round(high_disc.mean(), 2),
        "Low_Discount_Mean": round(low_disc.mean(), 2),
        "T_Statistic": round(t_stat, 4),
        "P_Value": p_val,
        "Is_Significant_Alpha_05": p_val < 0.05,
        "Null_Hypothesis_Status": "REJECTED (High discount orders have significantly lower margins)" if p_val < 0.05 else "FAIL TO REJECT"
    }
    
    print(f"  • High Discount Margin Mean: {result['High_Discount_Mean']}%, Low Discount Mean: {result['Low_Discount_Mean']}%")
    print(f"  • T-Statistic: {result['T_Statistic']}, P-Value: {p_val:.4e}")
    print(f"  • Decision at alpha=0.05: {result['Null_Hypothesis_Status']}")
    return result


def run_full_statistical_pipeline(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run the full descriptive and inferential statistical analysis pipeline.
    """
    print("==================================================")
    print("      STARTING INFERENTIAL STATISTICAL PIPELINE    ")
    print("==================================================")
    
    desc_stats = compute_descriptive_stats(df)
    
    chi2_result = run_chi_square_test(df, 'Shipping Mode', 'Late_delivery_risk')
    anova_result = run_anova_test(df, 'Days for shipping (real)', 'Market')
    ttest_result = run_ttest(df, 'Profit_Margin_Pct', 'Discount_Ratio', threshold=0.15)
    
    hypothesis_summary = {
        "Chi_Square": chi2_result,
        "ANOVA": anova_result,
        "T_Test": ttest_result
    }
    
    print("==================================================\n")
    return desc_stats, hypothesis_summary
