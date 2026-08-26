# Technical System Architecture Specification

This document details the end-to-end software architecture, data processing lifecycle, schema dictionary, module dependencies, and security controls for the **Data-Driven Supply Chain Analytics & Predictive Platform**.

---

## 1. High-Level System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     DATA INGESTION LAYER                                         │
│                       DataCo Smart Supply Chain Dataset (180,519 × 53 Schema)                    │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PREPROCESSING & QA ENGINE                                      │
│                       • PII Sanitization (Email, Passwords, Product Images)                      │
│                       • Missing Value Imputation (Zipcodes, Order Status)                        │
│                       • Outlier Removal (IQR 1.5× & Z-Score Filtering)                           │
│                       • File: src/preprocessing.py                                              │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                FEATURE ENGINEERING MODULE                                       │
│                       • 14 Domain Ratios (Delivery Delay, Profit Margin %)                       │
│                       • RFM Aggregations (Recency, Frequency, Monetary, AOV)                     │
│                       • File: src/feature_engineering.py                                         │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌────────────────────────────────────────────────┴─────────────────────────────────────────────────┐
│                                                                                                  │
│  ┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────────┐  │
│  │         STATISTICAL ANALYSIS ENGINE          │  │        TIME SERIES FORECAST ENGINE       │  │
│  │ • Chi-Square Tests & ANOVA Hypothesis Tests  │  │ • Daily Sales Aggregation (1,127 Days)   │  │
│  │ • Correlation Matrices & Feature Drift       │  │ • Holt-Winters & SARIMAX (30-Day Proj)   │  │
│  │ • File: src/statistical_analysis.py          │  │ • File: src/time_series.py               │  │
│  └──────────────────────────────────────────────┘  └──────────────────────────────────────────┘  │
│                                                                                                  │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MACHINE LEARNING PIPELINE LAYER                                  │
│ • Classification: XGBoost Late Delivery Risk Predictor (ROC-AUC: 78.2%, Precision: 85.7%)        │
│ • Regression: Delivery Duration Predictor (MAE: 0.98 Days, R²: 0.3915)                          │
│ • Clustering: K-Means Customer Persona Segmentation (6 Clusters, Silhouette: 0.4242)             │
│ • File: src/ml_pipeline.py                                                                       │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌────────────────────────────────────────────────┴─────────────────────────────────────────────────┐
│                                                                                                  │
│  ┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────────┐  │
│  │        POWER BI STAR SCHEMA DATA MODEL       │  │       FULL-STACK FLASK WEB PLATFORM      │  │
│  │ • 5 Relational Tables (1 Fact, 4 Dimensions) │  │ • REST API Endpoints (/api/predict/*)    │  │
│  │ • 19 DAX Measures Library                    │  │ • Premium UI with Embedded Power BI Hub  │  │
│  │ • Directory: data/powerbi/                   │  │ • Directory: web_app/                    │  │
│  └──────────────────────────────────────────────┘  └──────────────────────────────────────────┘  │
│                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Preprocessing & Data Quality Module (`src/preprocessing.py`)
- **Objective**: Standardizes data types, removes non-essential PII attributes, and cleans numerical anomalies.
- **Inputs**: Raw Kaggle CSV (`DataCoSupplyChainDataset.csv`).
- **Processing Steps**:
  1. **PII Removal**: Drops `Customer Email`, `Customer Password`, `Customer Street`, `Product Image`.
  2. **Zipcode Handling**: Converts float zipcodes to 5-digit zero-padded string codes, imputing missing values with modal region zipcodes.
  3. **Outlier Filtering**: Applies IQR thresholding to `Order Item Discount Rate` and `Sales`.
  4. **Date Standardization**: Parses `order date` and `shipping date` into ISO-8601 datetime format.
- **Output**: Cleaned dataset saved to `data/cleaned_supply_chain.csv` (180,519 rows × 54 columns, 0 nulls).

### 2.2 Domain Feature Engineering Module (`src/feature_engineering.py`)
- **Objective**: Computes supply chain operational indicators and customer RFM profiles.
- **Engineered Attributes**:
  - `Delivery_Delay_Days` = `Days for shipping (real)` - `Days for shipment (scheduled)`
  - `Profit Margin Pct` = `Order Profit Per Order` / `Sales`
  - `Customer_Recency` = Days since last order date
  - `Customer_Frequency` = Total distinct order count per customer
  - `Customer_Monetary` = Cumulative net spend per customer
  - `Regional_Late_Rate` = Historical late delivery percentage per Order Region
- **Output**: Dataset saved to `data/engineered_features.csv` (180,519 rows × 68 columns).

### 2.3 Machine Learning Pipeline Module (`src/ml_pipeline.py`)
- **Objective**: Trains, tunes, and evaluates 3 distinct ML models.
- **Models Implemented**:
  1. **Late Delivery Risk Classifier**:
     - Algorithm: Tuned XGBoost Classifier (`n_estimators=100`, `max_depth=6`, `learning_rate=0.1`).
     - Preprocessor: OneHotEncoder for categorical features, StandardScaler for numeric features.
     - Validation: 5-Fold Stratified Cross-Validation (Zero overfitting: Train 71.83% vs Test 72.06%).
  2. **Delivery Duration Regressor**:
     - Algorithm: Linear Regression / Random Forest Regressor.
     - Evaluation Metrics: MAE = 0.9853 days, RMSE = 1.3412 days.
  3. **Customer K-Means Clustering**:
     - Algorithm: K-Means ($k=6$ clusters selected via Elbow & Silhouette analysis).
     - Scaler: StandardScaler on RFM attributes.
     - Output Labels: *VIP Champions*, *Loyal Regular Buyers*, *At-Risk / Churned*, *High-AOV Spenders*, *Unprofitable Bulk Returners*, *Low-Spend One-Time*.

### 2.4 Time Series Forecasting Module (`src/time_series.py`)
- **Objective**: Resamples daily sales revenue ($36.78M across 1,127 days) and generates out-of-sample future revenue projections.
- **Models Implemented**: 30-Day Moving Average, Holt-Winters Exponential Smoothing, SARIMAX(1,1,1).
- **Projections**: 30-day future demand forecast ($427,604.57 projected revenue) with 95% confidence bands.

### 2.5 Power BI Data Modeling Engine (`data/powerbi/`)
- **Star Schema Schema**:
  - `fact_orders.csv` (180,519 rows × 25 attributes)
  - `dim_customers.csv` (20,652 rows × 8 attributes)
  - `dim_products.csv` (118 rows × 5 attributes)
  - `dim_geography.csv` (164 rows × 4 attributes — 100% unique countries)
  - `dim_date.csv` (65,752 rows × 7 attributes)
- **DAX Measures**: 19 production DAX measures across Financial, Operational, AI Risk, and Time Intelligence dimensions.

---

## 3. Data Dictionary

### Core Fact Table (`fact_orders`)
| Attribute Name | Data Type | Description |
| :--- | :--- | :--- |
| `Order Item Id` | INTEGER | Primary Surrogate Key for each transaction line item |
| `Order Id` | INTEGER | Business Order Identifier |
| `Order_Date` | DATETIME | ISO timestamp when the order was placed |
| `Shipping_Date` | DATETIME | ISO timestamp when the order was dispatched |
| `Customer Id` | INTEGER | Foreign Key referencing `dim_customers` |
| `Product Card Id` | INTEGER | Foreign Key referencing `dim_products` |
| `Order Country` | STRING | Foreign Key referencing `dim_geography` |
| `Shipping Mode` | STRING | Shipping method (Standard Class, First Class, Second Class, Same Day) |
| `Delivery Status` | STRING | Status (Late Delivery, Advance Shipping, Shipping On Time, Canceled) |
| `Sales` | FLOAT | Total revenue collected for the line item ($) |
| `Order Profit Per Order` | FLOAT | Net profit earned per line item ($) |
| `Late_delivery_risk` | INTEGER | Binary ground truth flag (1 = Late, 0 = On Time) |
| `late_probability` | FLOAT | XGBoost model output probability of late delivery |
| `risk_level` | STRING | AI Risk Classification (HIGH RISK if probability >= 0.5, else LOW RISK) |
| `predicted_days` | FLOAT | Linear Regression model output for expected shipping duration (days) |

---

## 4. Security & Compliance Controls

1. **PII Sanitization**: Sensitive user attributes (`Customer Email`, `Customer Password`, `Customer Street`) are dropped prior to persistence to ensure compliance with GDPR/CCPA.
2. **Data Integrity**: Foreign key constraints between `fact_orders` and all 4 dimension tables are validated to guarantee zero orphan records.
3. **Model Artifact Integrity**: All trained models are serialized as standard Python `.pkl` files using `joblib` with pre-fit encoders and scalers bundled alongside.
