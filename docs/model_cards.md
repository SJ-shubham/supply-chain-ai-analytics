# Machine Learning Model Cards Specification

This document provides formal **Model Scorecards** for all machine learning models trained, evaluated, and deployed in the **Supply Chain AI Analytics Platform**.

---

## Model Card 1: XGBoost Late Delivery Risk Classifier

### Model Details
- **Model Name**: XGBoost Late Delivery Risk Classifier
- **Model Version**: v1.0.0
- **Model Type**: Supervised Binary Classification (`XGBClassifier`)
- **Developer**: Advanced Data Science Team
- **Release Date**: August 2026
- **Artifact Files**: `models/late_delivery_xgboost.pkl`, `models/classification_preprocessor.pkl`

### Intended Use
- **Primary Objective**: Predict whether an incoming order will experience a shipping delay (`Late_delivery_risk = 1`) at the exact moment of order placement, enabling logistics managers to proactively re-route high-risk shipments.
- **Out-of-Scope Uses**: Must NOT be used to auto-cancel orders without human operational review.

### Training Data & Preprocessing
- **Training Dataset**: 180,519 order records from the DataCo Supply Chain dataset.
- **Train/Test Split**: 80% Train (144,415 samples), 20% Test (36,104 samples) using Stratified 5-Fold Cross Validation.
- **Engineered Features**:
  - Temporal: `order_month`, `order_dayofweek`, `order_hour`
  - Categorical: `Shipping Mode`, `Market`, `Order Region`, `Category Name`
  - Domain Interactions: `Regional_Late_Rate`, `Shipping_Mode_Late_Rate`, `Regional_Late_Rate * Shipping_Mode_Late_Rate`
- **Data Leakage Safeguards**: Strict exclusion of post-dispatch columns (e.g., `Days for shipping (real)`, `Delivery Status`).

### Hyperparameter Configuration
```python
XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='logloss'
)
```

### Performance Evaluation
| Metric | Score | Benchmark Target | Status |
| :--- | :---: | :---: | :---: |
| **ROC-AUC Score** | **78.2%** | >= 75.0% | **PASSED** |
| **Precision (Late Class)** | **85.7%** | >= 80.0% | **PASSED** |
| **Overall Accuracy** | **72.1%** | >= 70.0% | **PASSED** |
| **F1 Score** | **0.7073** | >= 0.6800 | **PASSED** |
| **5-Fold CV Train Acc** | **71.83%** | Zero Overfitting | **PASSED** |
| **5-Fold CV Test Acc** | **72.06%** | Zero Overfitting | **PASSED** |

### Feature Importance (SHAP Value Ranking)
1. `Days for shipment (scheduled)` (42.1% impact)
2. `Shipping_Mode_Late_Rate` (21.4% impact)
3. `Regional_Late_Rate` (18.6% impact)
4. `Order Item Product Price` (9.3% impact)
5. `Order Item Discount Rate` (8.6% impact)

---

## Model Card 2: Delivery Duration Regressor

### Model Details
- **Model Name**: Shipping Duration Linear Regressor
- **Model Version**: v1.0.0
- **Model Type**: Supervised Continuous Regression (`LinearRegression`)
- **Artifact Files**: `models/delivery_time_regressor.pkl`, `models/regression_preprocessor.pkl`

### Intended Use
- **Primary Objective**: Predict the expected actual shipping duration (`Days for shipping (real)`) in days for incoming customer orders.

### Performance Evaluation
| Metric | Score | Unit | Status |
| :--- | :---: | :---: | :---: |
| **Mean Absolute Error (MAE)** | **0.9853** | Days | **PASSED (< 1.0 Day)** |
| **Root Mean Squared Error (RMSE)** | **1.3412** | Days | **PASSED** |
| **Coefficient of Determination (R²)** | **0.3915** | Percentage | **PASSED** |

---

## Model Card 3: Customer K-Means Segmentation Engine

### Model Details
- **Model Name**: Customer RFM Segmentation Clusterer
- **Model Version**: v1.0.0
- **Model Type**: Unsupervised Clustering (`KMeans`)
- **Artifact Files**: `models/customer_kmeans_model.pkl`, `models/kmeans_scaler.pkl`

### Intended Use
- **Primary Objective**: Group 20,652 unique customer profiles into 6 distinct behavioral personas using RFM (Recency, Frequency, Monetary, AOV, Profit) metrics.

### Persona Specifications ($k=6$, Silhouette Score = 0.4242)
1. **VIP Champions (Cluster 0)**: High frequency, top monetary spend, lowest recency days.
2. **Loyal Regular Buyers (Cluster 1)**: Consistent orders, solid profitability, moderate AOV.
3. **At-Risk / Churned (Cluster 2)**: High recency days (> 200 days inactive), declining purchase volume.
4. **High-AOV Spenders (Cluster 3)**: Low order count but extremely large basket order values.
5. **Unprofitable Bulk Returners (Cluster 4)**: High order volume with negative net profit margins.
6. **Low-Spend One-Time (Cluster 5)**: Single purchase customers with low basket size.

---

## Model Card 4: Daily Sales & Demand Time Series Forecaster

### Model Details
- **Model Name**: Holt-Winters Exponential Smoothing & SARIMAX Demand Forecaster
- **Model Version**: v1.0.0
- **Model Type**: Time Series Forecasting (`ExponentialSmoothing` / `SARIMAX`)
- **Artifact Files**: `models/time_series_forecaster.pkl`, `reports/figures/timeseries_forecast.png`

### Intended Use
- **Primary Objective**: Forecast daily revenue and order volume 30 days into the future.

### Performance Evaluation (1,127 Days Historical Data)
| Forecasting Model | MAE ($) | RMSE ($) | Status |
| :--- | :---: | :---: | :---: |
| **30-Day Moving Average** | $12,921.42 | $18,948.51 | Baseline |
| **Holt-Winters Exponential Smoothing** | $13,369.43 | $19,465.25 | Alternative |
| **SARIMAX (1,1,1) (Best Model)** | **$12,875.59** | **$18,887.97** | **SELECTED** |

- **30-Day Projected Revenue**: $427,604.57 (with 95% confidence bands).
