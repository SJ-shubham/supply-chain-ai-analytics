# Ultra-Detailed Step-by-Step Manual: Building the 6-Page Supply Chain & AI Dashboard

This document provides a **click-by-click, visual-by-visual manual** for constructing the complete **6-Page Executive Supply Chain & Machine Learning Dashboard** in Power BI Desktop using our exported Star Schema dataset (`data/powerbi/`).

---

# Section 1: Pre-Requisites & Project Setup

### Step 1.1: Launch Power BI Desktop & Set Canvas Size
1. Open **Power BI Desktop**.
2. Click **File -> Options and settings -> Options**.
3. Under **GLOBAL -> Data Load**, **UNCHECK** *"Autodetect new relationships after data is loaded"* (this allows us to set exact Star Schema relationships manually). Click **OK**.
4. Set Canvas Settings:
   - Click anywhere on the blank canvas.
   - Go to the **Format Pane (Paintbrush icon)** -> **Canvas settings**.
   - Type: **16:9** (Resolution: 1280 × 720 pixels or 1920 × 1080 pixels).

---

# Section 2: Data Import & Star Schema Relationship Setup

### Step 2.1: Load CSV Datasets
1. On the **Home Ribbon**, click **Get Data -> Text/CSV**.
2. Navigate to your project directory: `c:\Users\Shubham\Desktop\DSProject\data\powerbi\`
3. Import the following 5 CSV files one by one (click **Load** for each):
   - `fact_orders.csv`
   - `dim_customers.csv`
   - `dim_products.csv`
   - `dim_geography_clean.csv`
   - `dim_date.csv`

### Step 2.2: Configure Relationships in Model View
1. Click the **Model View icon** on the far-left sidebar (the 3 connected boxes icon).
2. Arrange `fact_orders` in the center and place the 4 dimension tables around it.
3. Drag and drop to create the following relationships:

- **Relationship 1**: Drag `dim_customers[Customer Id]` and drop onto `fact_orders[Customer Id]`
  - Cardinality: **One to Many (1:*)**
  - Cross filter direction: **Single**
- **Relationship 2**: Drag `dim_products[Product Card Id]` and drop onto `fact_orders[Product Card Id]`
  - Cardinality: **One to Many (1:*)**
  - Cross filter direction: **Single**
- **Relationship 3**: Drag `dim_geography_clean[Order Country]` and drop onto `fact_orders[Order Country]`
  - Cardinality: **One to Many (1:*)**
  - Cross filter direction: **Single**
- **Relationship 4**: Drag `dim_date[Date]` and drop onto `fact_orders[Order_Date]`
  - Cardinality: **One to Many (1:*)**
  - Cross filter direction: **Single**

---

# Section 3: DAX Measures Table Creation

### Step 3.1: Create `_Measures` Table
1. On the **Home Ribbon**, click **Enter Data**.
2. In the Table dialog, name the table **`_Measures`** and click **Load**.

### Step 3.2: Add All 19 DAX Measures
*Important Note*: For Measures 17-19 (Time Intelligence like `YTD Revenue` and `SAMEPERIODLASTYEAR`), right-click `dim_date` in the Data Pane -> Select **Mark as date table** -> Select column `Date`.

Right-click `_Measures` in the Data Pane -> Click **New measure**, and copy-paste each measure below:

```dax
// 1. Total Revenue
Total Revenue = SUM(fact_orders[Sales])

// 2. Total Profit
Total Profit = SUM(fact_orders[Order Profit Per Order])

// 3. Profit Margin Percent
Profit Margin % = DIVIDE([Total Profit], [Total Revenue], 0)

// 4. Average Order Value
Average Order Value = DIVIDE([Total Revenue], COUNTROWS(fact_orders), 0)

// 5. Total Discount Amount
Total Discount Amount = SUMX(fact_orders, fact_orders[Order Item Product Price] * fact_orders[Order Item Quantity] * fact_orders[Order Item Discount Rate])

// 6. Total Orders
Total Orders = COUNTROWS(fact_orders)

// 7. Late Deliveries Count
Late Deliveries Count = CALCULATE(COUNTROWS(fact_orders), fact_orders[Late_delivery_risk] = 1)

// 8. Late Delivery Rate Percent
Late Delivery Rate % = DIVIDE([Late Deliveries Count], [Total Orders], 0)

// 9. On-Time Delivery Rate Percent
On-Time Delivery Rate % = 1 - [Late Delivery Rate %]

// 10. Average Scheduled Shipping Days
Avg Scheduled Days = AVERAGE(fact_orders[Days for shipment (scheduled)])

// 11. Average Actual Shipping Days
Avg Actual Shipping Days = AVERAGE(fact_orders[Days for shipping (real)])

// 12. Average Shipping Delay Days
Avg Shipping Delay Days = AVERAGE(fact_orders[Delivery_Delay_Days])

// 13. AI Flagged High Risk Orders Count
AI High Risk Orders Count = CALCULATE(COUNTROWS(fact_orders), fact_orders[risk_level] = "HIGH RISK")

// 14. AI High Risk Rate Percent
AI High Risk Rate % = DIVIDE([AI High Risk Orders Count], [Total Orders], 0)

// 15. Revenue at Late Risk
Revenue at Late Risk = CALCULATE([Total Revenue], fact_orders[risk_level] = "HIGH RISK")

// 16. Average Predicted Shipping Days
Avg Predicted Shipping Days = AVERAGE(fact_orders[predicted_days])

// 17. YTD Revenue
YTD Revenue = TOTALYTD([Total Revenue], dim_date[Date])

// 18. Prior Year Revenue
Prior Year Revenue = CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(dim_date[Date]))

// 19. Year over Year Revenue Growth Percent
YoY Revenue Growth % = DIVIDE([Total Revenue] - [Prior Year Revenue], [Prior Year Revenue], 0)
```

---

# Section 4: Color Design System & Master Header Layout

### Color Palette (Hex Codes):
- Header Bar: `#1E293B` (Dark Navy Slate)
- Primary Accents / Bars: `#0EA5E9` (Ocean Blue)
- Alert / Late Risk: `#EF4444` (Vibrant Red)
- Success / On-Time: `#10B981` (Emerald Green)
- Warning: `#F59E0B` (Amber Gold)
- Page Canvas Background: `#F8FAFC` (Slate 50)
- Card Container Background: `#FFFFFF` (White)

### Master Header & Navigation Template (All Pages):
1. Insert Shape: **Rectangle** across top (Height: 60px, Width: 1280px, Fill: `#1E293B`).
2. Insert Text Box: **SUPPLY CHAIN & AI ANALYTICS COMMAND CENTER** (Font: Segoe UI Bold, 18pt, White).
3. Insert Page Navigation Bar: **Insert -> Buttons -> Navigator -> Page navigator** (Place at top right).

---

# Section 5: Page 1 — Executive Overview Dashboard

Rename **Page 1** to `Executive Overview`.

### Step 5.1: Top Filter Slicers Panel (Position: Top Bar below Header)
1. **Slicer 1 (Year)**:
   - Select **Slicer** visual. Drag `dim_date[Year]` into Field.
   - Style: Dropdown. Position: Top Left.
2. **Slicer 2 (Market)**:
   - Select **Slicer** visual. Drag `dim_geography_clean[Market]` into Field.
   - Style: Horizontal Buttons / Tiles.
3. **Slicer 3 (Shipping Mode)**:
   - Select **Slicer** visual. Drag `fact_orders[Shipping Mode]` into Field.

### Step 5.2: KPI Cards Row (5 Cards - Position: Y = 110px)
- **Card 1 (Total Revenue)**: Add **Card** visual. Field: `_Measures[Total Revenue]`. Format: Currency `$#,##0`.
- **Card 2 (Total Profit)**: Add **Card** visual. Field: `_Measures[Total Profit]`. Format: Currency `$#,##0`.
- **Card 3 (Profit Margin %)**: Add **Card** visual. Field: `_Measures[Profit Margin %]`. Format: Percentage `0.0%`.
- **Card 4 (Total Orders)**: Add **Card** visual. Field: `_Measures[Total Orders]`. Format: Whole Number `#,##0`.
- **Card 5 (Late Delivery Rate %)**: Add **Card** visual. Field: `_Measures[Late Delivery Rate %]`. Format: Percentage `0.0%`.
  - Conditional Formatting: Go to Callout Value -> Color -> FX -> Rules -> If `Late Delivery Rate %` > 0.5 then Red `#EF4444`.

### Step 5.3: Visuals Construction (Row 2 & 3)

#### Visual 1: Monthly Revenue Trend & Order Volume (Top Left)
- **Visual Type**: **Line and clustered column chart**
- **Shared X-Axis**: `dim_date[Month_Name]` (Sort by `dim_date[Month]` ascending)
- **Column Y-Axis**: `_Measures[Total Revenue]` (Color: `#0EA5E9`)
- **Line Y-Axis**: `_Measures[Total Orders]` (Color: `#1E293B`)
- **Title**: `Monthly Revenue Trend & Order Volume`

#### Visual 2: Financial Profitability Waterfall Chart (Top Right)
- **Visual Type**: **Waterfall chart**
- **Category**: `fact_orders[Shipping Mode]`
- **Y-Axis**: `_Measures[Total Profit]`
- **Title**: `Profit Contribution by Shipping Mode`

#### Visual 3: Global Revenue Distribution Map (Bottom Left)
- **Visual Type**: **Map**
- **Location**: `dim_geography_clean[Order Country]`
- **Bubble Size**: `_Measures[Total Revenue]`
- **Tooltips**: `_Measures[Total Profit]`, `_Measures[Late Delivery Rate %]`
- **Title**: `Global Revenue Geographic Distribution`

#### Visual 4: Customer Segment Revenue Share (Bottom Right)
- **Visual Type**: **Donut chart**
- **Legend**: `fact_orders[Customer Segment]`
- **Values**: `_Measures[Total Revenue]`
- **Detail Labels**: Category + Percent of Total
- **Title**: `Revenue Share by Customer Segment`

#### Visual 5: Smart Narrative AI Summary (Bottom Panel)
- **Visual Type**: **Smart Narrative**
- Auto-generates written executive insights summarizing sales drivers.

---

# Section 6: Page 2 — Supply Chain & Logistics Operations

Create a new page and rename to `Logistics Operations`.

### Step 6.1: Top Filter Slicers Panel
- Add Slicers for `dim_geography_clean[Order Region]`, `fact_orders[Delivery Status]`, and `fact_orders[Shipping Mode]`.

### Step 6.2: KPI Cards Row (4 Cards)
- **Card 1**: `_Measures[Avg Scheduled Days]` (Format: `0.0` Days)
- **Card 2**: `_Measures[Avg Actual Shipping Days]` (Format: `0.0` Days)
- **Card 3**: `_Measures[Avg Shipping Delay Days]` (Format: `0.0` Days, Callout Color FX: Red if > 0)
- **Card 4**: `_Measures[On-Time Delivery Rate %]` (Format: Percentage `0.0%`)

### Step 6.3: Visuals Construction

#### Visual 1: On-Time Target SLA Gauge Chart (Top Left)
- **Visual Type**: **Gauge**
- **Value**: `_Measures[On-Time Delivery Rate %]`
- **Target Value**: `0.85` (85% Target SLA)
- **Minimum**: `0`, **Maximum**: `1`
- **Callout Color**: Green `#10B981` if >= 85%, Red `#EF4444` if < 85%
- **Title**: `On-Time Delivery Rate vs 85% Target SLA`

#### Visual 2: Late Delivery Root Cause Decomposition Tree (Top Right)
- **Visual Type**: **Decomposition tree**
- **Analyze**: `_Measures[Late Deliveries Count]`
- **Explain By**: `dim_geography_clean[Market]`, `dim_geography_clean[Order Region]`, `fact_orders[Shipping Mode]`, `dim_products[Category Name]`
- **Title**: `Late Delivery Root Cause AI Decomposition Tree`

#### Visual 3: Late Delivery Rate by Shipping Mode Bar Chart (Middle Left)
- **Visual Type**: **Clustered bar chart**
- **Y-Axis**: `fact_orders[Shipping Mode]`
- **X-Axis**: `_Measures[Late Delivery Rate %]`
- **Analytics Pane**: Add Constant Line at `0.50` (50% Threshold line, Red)
- **Title**: `Late Delivery Rate by Shipping Mode`

#### Visual 4: Regional Shipping Delay Heatmap Matrix (Bottom Left)
- **Visual Type**: **Matrix**
- **Rows**: `dim_geography_clean[Order Region]`
- **Columns**: `fact_orders[Shipping Mode]`
- **Values**: `_Measures[Avg Shipping Delay Days]`
- **Conditional Formatting**: Background Color -> Color Scale -> Minimum: Green `#10B981`, Maximum: Red `#EF4444`
- **Title**: `Regional Shipping Delay Heatmap (Days)`

#### Visual 5: Average Delay Days Trend Line Chart (Bottom Right)
- **Visual Type**: **Line chart**
- **X-Axis**: `dim_date[Date]` (Continuous)
- **Y-Axis**: `_Measures[Avg Shipping Delay Days]`
- **Title**: `Average Shipping Delay Trend Over Time`

---

# Section 7: Page 3 — Customer Intelligence & Segmentation

Create a new page and rename to `Customer Intelligence`.

### Step 7.1: Top Filter Slicers Panel
- Add Slicers for `dim_customers[Cluster_Label]` and `fact_orders[Customer Segment]`.

### Step 7.2: KPI Cards Row (4 Cards)
- **Card 1**: `Total Unique Customers` -> Count of `dim_customers[Customer Id]`
- **Card 2**: `Avg Customer Lifetime Spend` -> `AVERAGE(dim_customers[Customer_Monetary])` (Currency `$#,##0`)
- **Card 3**: `Avg Days Recency` -> `AVERAGE(dim_customers[Customer_Recency])` (`0` Days)
- **Card 4**: `VIP Champions Count` -> `CALCULATE(Count Customer Id, Cluster_Label = "VIP Champions")`

### Step 7.3: Visuals Construction

#### Visual 1: Recency vs Monetary Customer Matrix Scatter Plot (Top Left)
- **Visual Type**: **Scatter chart**
- **X-Axis**: `dim_customers[Customer_Recency]`
- **Y-Axis**: `dim_customers[Customer_Monetary]`
- **Legend**: `dim_customers[Cluster_Label]`
- **Size**: `dim_customers[Customer_Frequency]`
- **Title**: `Customer Recency vs Monetary Spend Matrix`

#### Visual 2: VIP Champion Key Influencers AI Visual (Top Right)
- **Visual Type**: **Key influencers**
- **Analyze**: `dim_customers[Cluster_Label]`
- **Explain By**: `Customer_Monetary`, `Customer_Frequency`, `Customer_Recency`, `Customer_Profit`
- **Title**: `Key Influencers Driving Customer Segments`

#### Visual 3: Customer Share by Persona Segment Donut Chart (Middle Left)
- **Visual Type**: **Donut chart**
- **Legend**: `dim_customers[Cluster_Label]`
- **Values**: Count of `dim_customers[Customer Id]`
- **Title**: `Customer Base Share by Persona Segment`

#### Visual 4: Profit Contribution by Persona Column Chart (Bottom Left)
- **Visual Type**: **Clustered column chart**
- **X-Axis**: `dim_customers[Cluster_Label]`
- **Y-Axis**: `SUM(dim_customers[Customer_Profit])`
- **Conditional Formatting**: Color Rules -> If Cluster_Label = "Unprofitable Returners" then Red `#EF4444` else Ocean Blue `#0EA5E9`
- **Title**: `Net Profit Contribution by Customer Segment`

#### Visual 5: Top Customer Directory Table (Bottom Right)
- **Visual Type**: **Table**
- **Columns**: `dim_customers[Customer Id]`, `dim_customers[Cluster_Label]`, `dim_customers[Customer_Recency]`, `dim_customers[Customer_Frequency]`, `dim_customers[Customer_Monetary]`, `dim_customers[Customer_Profit]`
- **Sort**: Click column header `Customer_Monetary` descending
- **Title**: `Top Customer Directory & Lifetime Metrics`

---

# Section 8: Page 4 — Product Catalog & Profitability Analytics

Create a new page and rename to `Product Analytics`.

### Step 8.1: Top Filter Slicers Panel
- Add Slicers for `dim_products[Department Name]` and `dim_products[Category Name]`.

### Step 8.2: KPI Cards Row (4 Cards)
- **Card 1**: `Active Products Count` -> Count of `dim_products[Product Card Id]`
- **Card 2**: `Categories Count` -> Distinct Count of `dim_products[Category Name]`
- **Card 3**: `Avg Product Price` -> `AVERAGE(dim_products[Order Item Product Price])`
- **Card 4**: `Avg Discount Rate` -> `AVERAGE(fact_orders[Order Item Discount Rate])`

### Step 8.3: Visuals Construction

#### Visual 1: Pareto 80/20 Category Revenue Driver Chart (Top Left)
- **Visual Type**: **Line and clustered column chart**
- **X-Axis**: `dim_products[Category Name]` (Sorted by Sales descending)
- **Column Y-Axis**: `_Measures[Total Revenue]`
- **Line Y-Axis**: Cumulative Revenue %
- **Title**: `Pareto 80/20 Revenue Driver Analysis by Category`

#### Visual 2: Top 10 Best-Selling Products Bar Chart (Top Right)
- **Visual Type**: **Clustered bar chart**
- **Y-Axis**: `dim_products[Product Name]`
- **X-Axis**: `_Measures[Total Revenue]`
- **Filters Pane**: Drag `Product Name` into Visual Filters -> Filter Type: **Top N** -> Show Top **10** by `_Measures[Total Revenue]`
- **Title**: `Top 10 Best-Selling Products by Revenue`

#### Visual 3: Discount Rate vs Profit Margin Impact Scatter Plot (Bottom Left)
- **Visual Type**: **Scatter chart**
- **X-Axis**: `fact_orders[Order Item Discount Rate]`
- **Y-Axis**: `_Measures[Profit Margin %]`
- **Legend**: `dim_products[Category Name]`
- **Analytics Pane**: Add Trend Line (Linear)
- **Title**: `Discount Rate Impact on Profit Margin %`

#### Visual 4: Department & Category Hierarchy Treemap (Bottom Middle)
- **Visual Type**: **Treemap**
- **Category**: `dim_products[Department Name]`, `dim_products[Category Name]`
- **Values**: `_Measures[Total Revenue]`
- **Title**: `Department & Category Revenue Hierarchy`

#### Visual 5: Revenue vs Profit by Department Column Chart (Bottom Right)
- **Visual Type**: **Clustered column chart**
- **X-Axis**: `dim_products[Department Name]`
- **Y-Axis**: `_Measures[Total Revenue]` and `_Measures[Total Profit]`
- **Title**: `Revenue vs Profit Comparison by Department`

---

# Section 9: Page 5 — Regional & Market Intelligence

Create a new page and rename to `Regional Intelligence`.

### Step 9.1: Top Filter Slicers Panel
- Add Slicers for `dim_geography_clean[Market]` and `dim_date[Year]`.

### Step 9.2: KPI Cards Row (4 Cards)
- **Card 1**: `Total Markets` -> `DISTINCTCOUNT(dim_geography_clean[Market])`
- **Card 2**: `Total Countries` -> `DISTINCTCOUNT(dim_geography_clean[Order Country])`
- **Card 3**: `Top Revenue Region` -> Text display of top region
- **Card 4**: `Highest Risk Region` -> Text display of highest late rate region

### Step 9.3: Visuals Construction

#### Visual 1: Global Late Delivery Risk Heatmap Shape Map (Top Left)
- **Visual Type**: **Filled Map / Shape Map**
- **Location**: `dim_geography_clean[Order Country]`
- **Color Fill / Saturation**: `_Measures[Late Delivery Rate %]`
- **Format Data Colors**: Minimum: Emerald Green `#10B981`, Maximum: Vibrant Red `#EF4444`
- **Title**: `Global Country-Level Late Delivery Risk Map`

#### Visual 2: Global Market Order Volume Funnel Chart (Top Right)
- **Visual Type**: **Funnel**
- **Category**: `dim_geography_clean[Market]`
- **Values**: `_Measures[Total Orders]`
- **Title**: `Order Volume Funnel across Global Markets`

#### Visual 3: Sales & Profit by Order Region Bar Chart (Middle Left)
- **Visual Type**: **Clustered bar chart**
- **Y-Axis**: `dim_geography_clean[Order Region]`
- **X-Axis**: `_Measures[Total Revenue]` and `_Measures[Total Profit]`
- **Title**: `Sales & Profit Performance by Order Region`

#### Visual 4: Regional Hierarchy Matrix with Data Bars (Bottom Left)
- **Visual Type**: **Matrix**
- **Rows**: `dim_geography_clean[Market]` -> `dim_geography_clean[Order Region]` -> `dim_geography_clean[Order Country]`
- **Values**: `_Measures[Total Revenue]`, `_Measures[Total Profit]`, `_Measures[Late Delivery Rate %]`, `_Measures[Avg Shipping Delay Days]`
- **Cell Elements**: Enable Data Bars for `Total Revenue`
- **Title**: `Regional Hierarchy Drill-Down Matrix`

#### Visual 5: Top 10 Countries by Order Volume Column Chart (Bottom Right)
- **Visual Type**: **Clustered column chart**
- **X-Axis**: `dim_geography_clean[Order Country]` (Filter Top 10 by `Total Orders`)
- **Y-Axis**: `_Measures[Total Orders]`
- **Title**: `Top 10 Global Countries by Order Volume`

---

# Section 10: Page 6 — AI Predictions & Demand Forecasting

Create a new page and rename to `AI Predictions & Forecasting`.

### Step 10.1: Top Filter Slicers Panel
- Add Slicers for `fact_orders[risk_level]` (HIGH RISK vs LOW RISK) and `dim_geography_clean[Market]`.

### Step 10.2: KPI Cards Row (4 Cards)
- **Card 1**: `AI High Risk Orders Count` -> `_Measures[AI High Risk Orders Count]`
- **Card 2**: `Revenue at Late Risk` -> `_Measures[Revenue at Late Risk]` (Currency `$#,##0`)
- **Card 3**: `AI High Risk Rate %` -> `_Measures[AI High Risk Rate %]` (Percentage `0.0%`)
- **Card 4**: `Avg Predicted Shipping Days` -> `_Measures[Avg Predicted Shipping Days]` (`0.0` Days)

### Step 10.3: Visuals Construction

#### Visual 1: Revenue Volume vs AI Late Probability Combo Chart (Top Left)
- **Visual Type**: **Line and clustered column chart**
- **X-Axis**: `dim_date[Month_Name]`
- **Column Y-Axis**: `_Measures[Total Revenue]`
- **Line Y-Axis**: `AVERAGE(fact_orders[late_probability])`
- **Title**: `Monthly Revenue Volume vs AI Late Probability`

#### Visual 2: 30-Day Out-of-Sample Demand Forecast Line Chart (Top Right)
- **Visual Type**: **Line chart**
- **X-Axis**: `dim_date[Date]` (Continuous)
- **Y-Axis**: `_Measures[Total Revenue]`
- **Analytics Pane Settings**:
  - Scroll down to **Forecast** -> Click **Add**
  - Units: **Days**, Forecast Length: **30**
  - Ignore Last: **0**
  - Confidence Interval: **95%**
- **Title**: `Daily Sales Revenue & 30-Day Future Demand Forecast`

#### Visual 3: AI Predicted vs Actual Shipping Days Scatter Plot (Middle Left)
- **Visual Type**: **Scatter chart**
- **X-Axis**: `fact_orders[Days for shipping (real)]`
- **Y-Axis**: `_Measures[Avg Predicted Shipping Days]`
- **Legend**: `fact_orders[Shipping Mode]`
- **Analytics Pane**: Add Reference Line (X=Y 45-degree slope)
- **Title**: `AI Predicted vs Actual Shipping Days Validation`

#### Visual 4: Orders Distribution by AI Risk Classification Donut (Bottom Left)
- **Visual Type**: **Donut chart**
- **Legend**: `fact_orders[risk_level]` (HIGH RISK vs LOW RISK)
- **Values**: `_Measures[Total Orders]`
- **Data Colors**: HIGH RISK = Red `#EF4444`, LOW RISK = Green `#10B981`
- **Title**: `Orders Distribution by AI Risk Classification`

#### Visual 5: Deployed Machine Learning Model Scorecard Matrix (Bottom Right)
- **Visual Type**: **Matrix / Table**
- **Add Table Columns**:
  - `Model Name` (XGBoost Classifier, Linear Regression, K-Means Clustering, SARIMAX / Holt-Winters)
  - `Predictive Task` (Late Risk Prediction, Delivery Duration, Customer Segmentation, 30-Day Sales Forecast)
  - `Primary Metric` (ROC-AUC / F1, MAE / RMSE, Silhouette Score, MAE)
  - `Score` (78.2%, 0.98 Days, 0.4242, $12,875)
  - `Status` (Production Deployed)
- **Title**: `Deployed Machine Learning Model Performance Scorecard`

---

# Section 11: Navigation, Sync Slicers & Final Export

### Step 11.1: Sync Slicers Across Pages
1. Go to **View Ribbon -> Sync Slicers**.
2. Select the `Year` and `Market` slicers on Page 1.
3. Check the **Sync checkbox** for all 6 pages (this ensures selecting Year 2017 on Page 1 updates all 6 pages automatically!).

### Step 11.2: Save File
Save your Power BI Desktop project to: `c:\Users\Shubham\Desktop\DSProject\dashboard\SupplyChainDashboard.pbix`
