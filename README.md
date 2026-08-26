# Data-Driven Supply Chain Analytics & Predictive Platform

An enterprise-grade **Data Science, Predictive Machine Learning, Business Intelligence (BI), and Time Series Analytics Platform** built on the **DataCo Smart Supply Chain Dataset** (180,519 transaction records across global logistics markets).

---

## Executive Project Summary

Global supply chain and e-commerce leaders (e.g., Amazon, DHL, FedEx, Walmart, Reliance) face multi-million dollar margin erosion due to delivery delays, inventory friction, stockout risks, and unoptimized customer discounting.

This project delivers an end-to-end analytical and machine learning system that:
1. **Predicts Late Delivery Risk** at order placement with **78.2% ROC-AUC** and **85.7% Precision** using tuned XGBoost.
2. **Estimates Shipping Duration** with a Mean Absolute Error of **less than 1 day (0.985 Days MAE)**.
3. **Segments 20,652 Customers** into 6 distinct behavioral personas using RFM K-Means clustering.
4. **Forecasts 30-Day Out-of-Sample Daily Sales & Demand** ($427,604.57 projected revenue) via Holt-Winters and SARIMAX time series models.
5. **Provides a 6-Page Interactive Power BI Command Center** driven by a 5-table Star Schema data model and 19 custom DAX measures.

---

## 1. Core Platform Capabilities & Technical Stack

| System Capability | Implementation Module | Technology Stack |
| :--- | :--- | :--- |
| **Data Ingestion & Cleaning** | PII sanitization, zipcode imputation, outlier filtering | Python 3.12, `pandas`, `scipy` |
| **Feature Engineering** | 14 domain metrics (Delay variance, profit margin %, RFM) | `pandas`, `numpy` |
| **Exploratory Data Analysis** | Multidimensional geographic & operational visualization | `seaborn`, `matplotlib` |
| **Statistical Hypothesis Testing** | Chi-Square, ANOVA, and T-Test statistical validation | `scipy.stats`, `statsmodels` |
| **Classification Machine Learning** | Late Delivery Risk Prediction (`Late_delivery_risk`) | `scikit-learn`, `xgboost` |
| **Regression Machine Learning** | Delivery Duration Prediction (`Days for shipping (real)`) | `scikit-learn` |
| **Unsupervised Clustering** | Customer RFM Behavioral Segmentation (6 Personas) | `scikit-learn` |
| **Time Series Demand Forecasting** | Daily Sales & Demand Forecasting (30-Day Horizon) | `statsmodels` |
| **Business Intelligence** | 6-Page Interactive Command Center (Star Schema, DAX) | Power BI Desktop |

---

## 2. Deployed Machine Learning Models Scorecard

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                DEPLOYED AI MODEL PERFORMANCE SUMMARY                              │
├──────────────────────┬──────────────────────┬────────────────────────┬─────────────┬──────────────┤
│ Model Name           │ Predictive Task      │ Primary Metric         │ Score       │ Status       │
├──────────────────────┼──────────────────────┼────────────────────────┼─────────────┼──────────────┤
│ XGBoost Classifier   │ Late Delivery Risk   │ ROC-AUC / Precision    │ 78.2% / 85.7%│ Production   │
│ Linear Regressor     │ Delivery Duration    │ MAE / RMSE             │ 0.985 Days  │ Production   │
│ K-Means Clustering   │ Customer Personas    │ Silhouette Score ($k=6$)│ 0.4242      │ Production   │
│ SARIMAX / Holt-Winter│ 30-Day Sales Forecast│ Out-of-Sample MAE      │ $12,875.59  │ Production   │
└──────────────────────┴──────────────────────┴────────────────────────┴─────────────┴──────────────┘
```

---

## 3. Project Directory Structure

```
DSProject/
├── data/
│   ├── cleaned_supply_chain.csv        # Cleaned dataset (PII removed, 0 nulls)
│   ├── engineered_features.csv         # Feature dataset with 68 attributes
│   └── powerbi/                        # Star Schema ready-to-import CSVs
│       ├── fact_orders.csv             # Fact table (180,519 rows × 25 attributes)
│       ├── dim_customers.csv           # Customer dimension (20,652 rows)
│       ├── dim_products.csv            # Product dimension (118 rows)
│       ├── dim_geography.csv           # Geography dimension (164 unique countries)
│       └── dim_date.csv                # Date dimension (65,752 dates)
│
├── docs/
│   ├── architecture.md                 # System architecture & data dictionary
│   └── model_cards.md                  # IEEE/Google-standard ML Model Cards
│
├── models/                             # Trained model binaries (.pkl)
│   ├── late_delivery_xgboost.pkl
│   ├── delivery_time_regressor.pkl
│   └── customer_kmeans_model.pkl
│
├── notebooks/                          # 8 Production Jupyter Notebooks
│   ├── 01_data_cleaning.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_eda_visualization.ipynb
│   ├── 04_statistical_analysis.ipynb
│   ├── 05_classification_delay_risk.ipynb
│   ├── 06_regression_shipping_days.ipynb
│   ├── 07_customer_clustering.ipynb
│   └── 08_business_forecasting.ipynb
│
├── reports/
│   ├── POWERBI_SETUP_GUIDE.md          # Power BI DAX & Star Schema manual
│   ├── POWERBI_STEP_BY_STEP_MANUAL.md  # Click-by-click dashboard construction guide
│   ├── EXECUTIVE_BUSINESS_REPORT.md    # Automated business report
│   └── figures/                        # 20 high-res visual charts & plots
│
├── src/                                # Core Modular Source Code
│   ├── data_loader.py                  # Dataset loading & schema audit
│   ├── preprocessing.py                 # Data cleaning & PII sanitization
│   ├── feature_engineering.py          # Metrics & RFM calculation
│   ├── statistical_analysis.py         # Statistical tests & EDA helpers
│   ├── ml_pipeline.py                  # ML model training & prediction functions
│   ├── time_series.py                  # Sales & demand forecasting engine
│   └── report_generator.py             # Automated report generator engine
│
├── requirements.txt                    # Project dependency list
└── README.md                           # Repository documentation
```

---

## 4. Power BI 6-Page Interactive Dashboard

The Star Schema datasets in `data/powerbi/` power a **6-Page Executive Dashboard** in Power BI Desktop:

1. **Page 1: Executive Overview Dashboard** (Revenue, Profit Margin, Global Revenue Map, Segment Share, Waterfall Chart).
2. **Page 2: Supply Chain & Logistics Operations** (On-Time Target SLA Gauge, Late Risk Decomposition Tree, Regional Delay Heatmap).
3. **Page 3: Customer Intelligence & Segmentation** (RFM Recency vs Monetary Matrix, Key Influencers AI Visual, Customer Directory).
4. **Page 4: Product Catalog & Profitability Analytics** (Pareto 80/20 Revenue Chart, Top 10 Products, Discount Sensitivity Scatter).
5. **Page 5: Regional & Market Intelligence** (Global Late Risk Shape Map, Market Order Volume Funnel, Hierarchy Matrix with Data Bars).
6. **Page 6: AI Predictions & Demand Forecasting** (Sales vs AI Probability Combo, 30-Day Forecast Line with 95% Confidence Band, Model Scorecard).

*Follow `reports/POWERBI_STEP_BY_STEP_MANUAL.md` for complete step-by-step setup instructions.*

---

## 5. Quickstart & Local Installation

### Prerequisites
- Python 3.10+
- Power BI Desktop (for dashboard visualization)

### Setup Instructions

1. **Clone Repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/supply-chain-ai-analytics.git
   cd supply-chain-ai-analytics
   ```

2. **Create & Activate Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate Automated Business Report**:
   ```bash
   python src/report_generator.py
   ```

---

## License & Citation

This project is designed as an enterprise Data Science & Supply Chain Analytics portfolio platform. Feel free to use and cite this codebase.
