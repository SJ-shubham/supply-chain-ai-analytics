# Master End-to-End Implementation Plan: Data-Driven Supply Chain Analytics for Business Decision Support

## Project Overview & Objectives
This project delivers a production-grade **Data Science, Predictive Machine Learning, Business Intelligence (BI), and Full-Stack Web Platform** based on the **DataCo Smart Supply Chain Dataset** (180,519 transaction records, 53 attributes).

The objective is to address supply chain operational challenges faced by global logistics and e-commerce companies (e.g., Amazon, Flipkart, Walmart, Reliance, DHL, FedEx) including delivery delays, stockouts, inventory friction, profit erosion, and supplier SLA breaches.

### Primary Project Capabilities:
1. **Data Cleaning & Quality Audit**: Standardize dates, handle missing values, sanitize PII, and analyze outliers.
2. **Domain Feature Engineering**: Create 12+ supply chain metrics (Delivery Delay Variance, Profit Margin %, SLA Ratios, RFM Customer Metrics).
3. **Exploratory Data Analysis (EDA)**: Multidimensional visual insights across sales, profit, logistics, suppliers, and customer geography.
4. **Statistical Hypothesis Testing**: Rigorous mathematical validation via Chi-Square Tests, One-Way ANOVA, and T-Tests.
5. **Machine Learning Pipeline**:
   * **Classification Model**: Predict `Late_delivery_risk` ($0 = \text{On-Time}, 1 = \text{Late}$) using XGBoost/Random Forest with SHAP explainability.
   * **Regression Model**: Predict `Days for shipping (real)` (actual delivery duration).
   * **Clustering Model**: Unsupervised K-Means Customer Segmentation (VIP, Wholesale, Regular, At-Risk).
6. **Time-Series Business Forecasting**: Demand, revenue, and order volume forecasting using ARIMA and Facebook Prophet.
7. **Automated Recommendation Engine**: Rule-based alert system mapping analytical flags to logistics interventions.
8. **Power BI Executive Dashboard**: 6-page interactive report with custom DAX measures, slicers, drill-downs, and tooltips.
9. **Full-Stack Web Application**: Flask web application hosting the embedded 6-page Power BI dashboard + live interactive ML prediction web forms.

---

## 1. Academic Syllabus Coverage (100% Mapping)

| Syllabus Topic | Project Feature / Module | Tools & Libraries Used |
| :--- | :--- | :--- |
| **Data Science Lifecycle** | End-to-End pipeline formulation, execution, and deployment | Python, VS Code, Power BI, Flask |
| **Data Cleaning** | Imputation, PII sanitization, duplicate removal, outlier handling | `pandas`, `numpy`, `scipy` |
| **Feature Engineering** | Operational delay indicators, profit margins, SLA ratios, RFM metrics | `pandas`, `numpy` |
| **EDA & Visualization** | Multidimensional analysis across geography, logistics, financial metrics | `seaborn`, `matplotlib`, `plotly` |
| **Statistics** | Descriptive statistics, Pearson correlation, Chi-Square, ANOVA, T-Tests | `scipy.stats`, `statsmodels` |
| **Classification ML** | Late Delivery Risk Prediction (`Late_delivery_risk`) | `scikit-learn`, `xgboost` |
| **Regression ML** | Delivery Duration Prediction (`Days for shipping (real)`) | `scikit-learn`, `xgboost` |
| **Clustering ML** | Customer Segmentation via K-Means (Elbow method, Silhouette score) | `scikit-learn` |
| **Business Forecasting** | Time-series forecasting for sales and order volumes | `statsmodels`, `prophet` |
| **Business Analytics** | Automated Rule-Based Decision & Alert Engine | Python custom engine |
| **Dashboarding** | 6-Page Interactive Executive Dashboard (DAX, Slicers, Tooltips) | Power BI Desktop |
| **Web Integration** | Web Application with embedded Power BI & live ML APIs | Python Flask, HTML5, CSS3, JS |

---

## 2. Dataset Schema & Column Audit

The project uses `DataCoSupplyChainDataset.csv` containing **180,519 rows and 53 attributes**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DATASET COLUMNS (53 TOTAL)                              │
├───────────────────────┬───────────────────────┬───────────────────┬────────────────────┤
│ Customer Demographics │ Order & Logistics     │ Product & Items   │ Financials         │
├───────────────────────┼───────────────────────┼───────────────────┼────────────────────┤
│ • Customer Id         │ • Order Id            │ • Product Card Id │ • Sales            │
│ • Customer Fname/Lname│ • Order Item Id       │ • Product Name    │ • Order Item Total │
│ • Customer Segment    │ • order date          │ • Product Price   │ • Profit Per Order │
│ • Customer City/State │ • shipping date       │ • Category Name   │ • Order Profit Ratio│
│ • Customer Zipcode    │ • Shipping Mode       │ • Department Name │ • Benefit per order│
│ • Latitude/Longitude  │ • Delivery Status     │ • Product Image*  │ • Item Discount    │
│ • Customer Email*     │ • Days shipping real  │ • Product Status  │ • Item Discount Rate│
│ • Customer Password*  │ • Days shipping sched │                   │                    │
│                       │ • Late_delivery_risk  │                   │                    │
│                       │ • Market / Order Region│                  │                    │
└───────────────────────┴───────────────────────┴───────────────────┴────────────────────┘
* Note: PII fields (Customer Email, Password, Street, Product Image) will be sanitized and removed.
```

---

## 3. End-to-End System Architecture

```
                                  ┌─────────────────────────────────────────┐
                                  │   Raw DataCo Supply Chain CSV Dataset   │
                                  │           (180,519 × 53 Schema)          │
                                  └────────────────────┬────────────────────┘
                                                       │
                                                       ▼
                                  ┌─────────────────────────────────────────┐
                                  │      MODULE 1: Data Cleaning & QA       │
                                  │   (Imputation, PII Removal, Outliers)   │
                                  └────────────────────┬────────────────────┘
                                                       │
                                                       ▼
                                  ┌─────────────────────────────────────────┐
                                  │    MODULE 2: Feature Engineering        │
                                  │ (Delay Metrics, Profit Margins, Ratios) │
                                  └────────────────────┬────────────────────┘
                                                       │
                                                       ▼
                             ┌─────────────────────────┴─────────────────────────┐
                             ▼                                                   ▼
              ┌──────────────────────────────┐                   ┌──────────────────────────────┐
              │   MODULE 3: Exploratory Data │                   │ MODULE 4: Hypothesis Testing │
              │         Analysis (EDA)       │                   │    & Statistical Analysis   │
              └──────────────┬───────────────┘                   └──────────────┬───────────────┘
                             │                                                   │
                             └─────────────────────────┬─────────────────────────┘
                                                       │
                                                       ▼
   ┌───────────────────────┬───────────────────────────┼───────────────────────────┬──────────────────────┐
   ▼                       ▼                           ▼                           ▼                      ▼
┌──────────────────┐  ┌──────────────────┐    ┌──────────────────┐        ┌──────────────────┐  ┌──────────────────┐
│    MODULE 5:     │  │    MODULE 6:     │    │    MODULE 7:     │        │    MODULE 8:     │  │    MODULE 9:     │
│  Classification  │  │    Regression    │    │ Customer Cluster │        │ Operational SLA  │  │   Time-Series    │
│  (Late Delivery) │  │  (Delivery Days) │    │     (K-Means)    │        │  (Supplier/WH)   │  │   Forecasting    │
└──────────┬───────┘  └────────┬─────────┘    └────────┬─────────┘        └────────┬─────────┘  └────────┬─────────┘
           │                   │                       │                           │                     │
           └───────────────────┴───────────────────────┼───────────────────────────┴─────────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │   MODULE 10: Recommendation     │
                                      │        Engine (Rule-Based)      │
                                      └────────────────┬────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │  MODULE 11: Power BI Dashboard  │
                                      │      (6-Page Executive Suite)   │
                                      └────────────────┬────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │   MODULE 12: Full-Stack Web App │
                                      │  (Flask Server + Power BI Embed │
                                      │     + Live ML Prediction UI)    │
                                      └─────────────────────────────────┘
```

---

## 4. Comprehensive Module Specifications

### Module 1: Data Cleaning & Preprocessing
* **Missing Value Imputation**:
  * Impute missing zipcodes (`Order Zipcode`, `Customer Zipcode`) using geographical mode aggregation (`Order City`, `Customer State`).
* **PII Sanitization & Column Pruning**:
  * Drop uninformative/PII attributes (`Customer Email`, `Customer Password`, `Customer Street`, `Product Image`, `Product Description`).
* **Date Parsing & Temporal Feature Extraction**:
  * Convert `order date (DateOrders)` and `shipping date (DateOrders)` into datetime objects.
  * Derive `Order Year`, `Order Month`, `Order DayOfWeek`, `Order Hour`, `Shipping Duration`.
* **Outlier Detection & Filtering**:
  * Apply Interquartile Range (IQR: $Q_1 - 1.5 \times \text{IQR}$ to $Q_3 + 1.5 \times \text{IQR}$) and Z-Scores on `Sales`, `Order Profit Per Order`, `Order Item Quantity`, and `Days for shipping (real)`.
  * Differentiate data corruption errors from extreme operational transactions (e.g. bulk orders).

### Module 2: Domain Feature Engineering
Construct enterprise supply chain indicators:
1. **Delivery Delay Variance**:
   $$\text{Delay Days} = \text{Days for shipping (real)} - \text{Days for shipment (scheduled)}$$
2. **Profit Margin Ratio**:
   $$\text{Profit Margin \%} = \frac{\text{Order Profit Per Order}}{\text{Sales}} \times 100$$
3. **Discount Impact Ratio**:
   $$\text{Discount Ratio} = \frac{\text{Order Item Discount}}{\text{Order Item Price} \times \text{Order Item Quantity}}$$
4. **RFM Metrics (Per Customer)**:
   * **Recency**: Days since customer's last order.
   * **Frequency**: Total order count per customer.
   * **Monetary**: Cumulative spend per customer.
5. **Supplier / Warehouse Late Delivery Rate**:
   $$\text{Node Late Rate} = \frac{\text{Delayed Orders}}{\text{Total Orders}}$$

### Module 3: Exploratory Data Analysis (EDA)
Generate 50+ visualizations answering major business queries:
* **Sales & Revenue**: Pareto chart of top sales regions/countries, revenue by product category treemap.
* **Profitability**: Profit loss heatmap by discount rate & market segment.
* **Logistics Performance**: Late delivery rate by shipping mode (Standard vs First Class vs Second Class vs Same Day).
* **Delivery Distribution**: KDE overlay plot comparing scheduled vs actual delivery days.
* **Customer Analytics**: Top 20 revenue-generating customers and geographic concentration map.

### Module 4: Rigorous Statistical Analysis & Hypothesis Testing
Validate operational patterns using statistical tests ($\alpha = 0.05$):
1. **Descriptive Statistics**: Mean, Median, Mode, Standard Deviation, Variance, Skewness, Kurtosis, IQR.
2. **Pearson & Spearman Correlation**: Assess relationships between `Sales`, `Profit`, `Discount`, `Quantity`, `Shipping Days`.
3. **Hypothesis Test 1 (Chi-Square Test of Independence)**:
   * $H_0$: Shipping Mode is independent of Late Delivery Risk.
   * $H_1$: Shipping Mode significantly impacts Late Delivery Risk.
4. **Hypothesis Test 2 (One-Way ANOVA)**:
   * $H_0$: Mean actual shipping days are equal across all geographic Markets.
   * $H_1$: Mean shipping days differ significantly across Markets.
5. **Hypothesis Test 3 (Two-Sample T-Test)**:
   * $H_0$: High discount orders ($\ge 15\%$) have identical mean profit margins to low discount orders.
   * $H_1$: High discount orders have significantly lower profit margins.

### Module 5: Machine Learning — Classification (Late Delivery Risk Prediction)
* **Target**: `Late_delivery_risk` ($0 = \text{On-Time/Early}, 1 = \text{Late}$).
* **Features**: `Shipping Mode`, `Market`, `Order Region`, `Category Id`, `Customer Segment`, `Department Id`, `Order Item Quantity`, `Sales`, `Order Item Discount Rate`, `Product Price`.
* **Preprocessing**: `StandardScaler` for numeric values, `OneHotEncoder` for categorical values.
* **Models**: Logistic Regression, Random Forest, XGBoost Classifier.
* **Tuning & Evaluation**: 5-Fold Cross-Validation, Hyperparameter Optimization, Confusion Matrix, Precision, Recall, F1-Score, ROC-AUC Curve, SHAP Explainability.

### Module 6: Machine Learning — Regression (Delivery Time Prediction)
* **Target**: `Days for shipping (real)`.
* **Features**: `Days for shipment (scheduled)`, `Shipping Mode`, `Market`, `Order Region`, `Category Id`, `Customer State`, `Sales`.
* **Models**: Linear Regression, Random Forest Regressor, XGBoost Regressor.
* **Evaluation**: MAE, RMSE, $R^2$, Residual Analysis Plots.

### Module 7: Unsupervised Learning — Customer Segmentation (K-Means Clustering)
* **Input Features**: Customer Recency, Frequency, Monetary Value (RFM), Average Order Value, Profit Contribution.
* **Scaling**: `StandardScaler`.
* **Clustering Analysis**: Elbow Method (WCSS) & Silhouette Coefficient analysis ($k \in [2, 8]$).
* **Cluster Profiles**:
  1. **VIP Customers**: High Monetary, High Frequency, Low Recency.
  2. **Wholesale Bulk Buyers**: High Quantity, High Revenue, Moderate Frequency.
  3. **Regular Steady Customers**: Moderate Spend and Frequency.
  4. **At-Risk / Churned Customers**: High Recency, Low Spend.

### Module 8: Supplier & Warehouse SLA Operational Ranking
Construct a node performance score:
$$\text{SLA Score} = 100 - \left( \text{Late Delivery \%} \times 0.50 + \frac{\text{Avg Shipping Days}}{\text{Scheduled Days}} \times 30 \right) + \left( \text{Profit Margin \%} \times 0.20 \right)$$
Categorize warehouses and suppliers into **Tier 1 (High Reliability)**, **Tier 2 (Moderate Risk)**, and **Tier 3 (High Operational Risk)**.

### Module 9: Business Forecasting (Time-Series Analytics)
* Aggregated monthly sales, profit, and order volumes.
* Models: **ARIMA/SARIMAX** (Stationarity testing via ADF) and **Facebook Prophet** (Seasonality & trend decomposition).
* Outputs: 6 to 12-month future projections with 95% confidence bounds.

### Module 10: Automated Business Recommendation Engine
Python decision engine outputting real-time operational alerts based on model flags:
* *Alert 1*: High Late Delivery Rate ($> 25\%$) in a specific carrier mode $\rightarrow$ "Renegotiate carrier SLA or alter dispatch windows."
* *Alert 2*: Low Profit Margin ($< 5\%$) with high discount ($> 15\%$) $\rightarrow$ "Enforce a 10% ceiling on promotional discounts."
* *Alert 3*: Predicted Late Risk ($1$) on high-value order ($> \$500$) $\rightarrow$ "Trigger priority express re-routing."

### Module 11: Power BI Executive Dashboard Architecture
6-Page Interactive Power BI Solution (`SupplyChainDashboard.pbix`):
* **Page 1: Executive Overview**: High-level KPIs, global sales heatmap, monthly revenue & profit trends.
* **Page 2: Sales & Profit Analytics**: Country/Category performance breakdown, product profitability matrix.
* **Page 3: Logistics & Delivery Performance**: Delay risk maps, shipping mode performance, delivery time histograms.
* **Page 4: Supplier & Warehouse SLA**: Operational ranking tables, late delivery rate by supplier.
* **Page 5: Customer Insights & Segmentation**: RFM cluster visualization, top customer profiles.
* **Page 6: Predictive ML & Demand Forecast**: Predicted delay risk breakdowns, time-series sales forecasts.

#### Essential DAX Measures:
```dax
Total Sales = SUM('DataCoSupplyChain'[Sales])
Total Profit = SUM('DataCoSupplyChain'[Order Profit Per Order])
Profit Margin % = DIVIDE([Total Profit], [Total Sales], 0)
Total Orders = DISTINCTCOUNT('DataCoSupplyChain'[Order Id])
Late Delivery Rate % = DIVIDE(CALCULATE(COUNT('DataCoSupplyChain'[Order Id]), 'DataCoSupplyChain'[Late_delivery_risk] = 1), COUNT('DataCoSupplyChain'[Order Id]), 0)
Avg Real Shipping Days = AVERAGE('DataCoSupplyChain'[Days for shipping (real)])
On-Time Delivery Rate % = 1 - [Late Delivery Rate %]
```

### Module 12: Full-Stack Web Application Platform
Deploy a unified web platform using Python Flask (`web_app/app.py`):
1. **Embedded BI Hub**: Full iframe embed of the 6-page interactive Power BI dashboard.
2. **AI Delay Prediction Form**: Web portal allowing users to input order attributes $\rightarrow$ returns XGBoost Late Risk Probability % & Risk Level.
3. **AI Delivery Duration Estimator Form**: Web portal for predicting actual shipping days.
4. **Customer Segment Explorer**: Web interface for inputting customer RFM metrics to return cluster segment & recommendations.
5. **Command Center & Operational Alerts**: Live UI rendering dynamic alerts generated by Module 10.

---

## 5. Repository Directory Structure

```
DSProject/
│
├── DataCoSupplyChainDataset.csv       # Raw Kaggle Dataset (180,519 records)
│
├── data/
│   ├── cleaned_supply_chain.csv       # Cleaned dataset (PII removed, imputed)
│   └── engineered_features.csv        # Preprocessed dataset with engineered features
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb         # Missing value imputation & sanitization
│   ├── 02_feature_engineering.ipynb    # Metric calculation & aggregation
│   ├── 03_eda_visualization.ipynb     # 50+ Seaborn/Plotly charts
│   ├── 04_statistical_analysis.ipynb  # Chi-Square, ANOVA, T-Tests, Correlation
│   ├── 05_classification_delay_risk.ipynb # XGBoost/RF Late Delivery Risk ML
│   ├── 06_regression_shipping_days.ipynb  # Shipping Time Regression ML
│   ├── 07_customer_clustering.ipynb   # K-Means RFM Segmentation
│   ├── 08_business_forecasting.ipynb  # ARIMA & Prophet Time-Series Forecasting
│   └── 09_recommendation_engine.ipynb # Rule-based decision alert engine
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py                 # Ingestion & cleaning helpers
│   ├── preprocessing.py                # Encoding & scaling pipelines
│   └── recommendation_rules.py        # Business alert logic rules
│
├── models/
│   ├── late_delivery_xgboost.pkl      # Trained classification model
│   ├── delivery_time_regressor.pkl    # Trained regression model
│   └── customer_kmeans_scaler.pkl     # K-Means model & standard scaler
│
├── web_app/
│   ├── app.py                         # Flask server & REST API endpoints
│   ├── templates/                     # Web pages (Power BI Embed + ML Portals)
│   │   ├── index.html                 # Executive Hub (Embedded Power BI)
│   │   ├── predict_delay.html         # Live Delay Risk Prediction UI
│   │   ├── predict_time.html          # Live Shipping Time Estimator UI
│   │   ├── customer_segment.html      # Customer Segment Classifier UI
│   │   └── recommendations.html       # Decision Alert Command Center UI
│   └── static/                        # Custom CSS styles, JavaScript, assets
│
├── dashboard/
│   ├── SupplyChainDashboard.pbix      # Master 6-page Power BI dashboard file
│   └── dashboard_screenshots/         # Report previews for documentation
│
├── reports/
│   ├── Project_Final_Report.pdf       # Academic B.Tech semester report
│   └── Business_Presentation_Deck.pptx# Viva presentation slides
│
├── requirements.txt                   # Dependency list (pandas, xgboost, flask, etc.)
└── README.md                          # Comprehensive GitHub documentation
```

---

## 6. Phased Execution & Verification Roadmap

| Phase | Core Deliverable | Verification Criteria |
| :--- | :--- | :--- |
| **Phase 1: Foundation** | Data cleaning, imputation, PII removal | `cleaned_supply_chain.csv` has 0 missing values in target columns & 0 PII. |
| **Phase 2: Feature & EDA** | Feature engineering, EDA plots, 3 Statistical Tests | Calculated 12+ metrics; executed ANOVA, Chi-Square, T-Test ($p < 0.05$). |
| **Phase 3: Core ML** | Classification, Regression, K-Means Clustering | XGBoost $F1 \ge 0.80$, Regression $R^2 \ge 0.75$, Silhouette Score evaluated. |
| **Phase 4: Forecasting & Rules** | Time-series forecasting & Recommendation Engine | Prophet/ARIMA forecasts generated; business rule alerts verified. |
| **Phase 5: Power BI** | 6-Page Executive Dashboard (`.pbix`) | All 6 pages built with interactive slicers, cross-filtering, and DAX. |
| **Phase 6: Web Integration** | Full-Stack Flask Web App + Power BI Embed + ML Portals | Web app running on localhost with embedded Power BI and live ML prediction forms. |

---

## User Feedback & Final Approval
This **Master End-to-End Implementation Plan** is ready. 
Upon your approval, we will immediately commence **Phase 1: Data Cleaning & Preprocessing**!
