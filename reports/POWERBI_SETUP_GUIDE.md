# Power BI 6-Page Dashboard Setup & DAX Guide

This guide provides step-by-step instructions for building the **6-Page Supply Chain & ML Dashboard** in Power BI Desktop using our exported Star Schema datasets.

---

## 1. Import Data & Establish Relationships (Star Schema)

Import all 5 CSV files from `data/powerbi/` into Power BI Desktop via **Get Data -> Text/CSV**:
1. `fact_orders.csv`
2. `dim_customers.csv`
3. `dim_products.csv`
4. `dim_geography.csv`
5. `dim_date.csv`

### Data Model Relationships (Model View):
- Connect `fact_orders[Customer Id]` (Many) to `dim_customers[Customer Id]` (One)
- Connect `fact_orders[Product Card Id]` (Many) to `dim_products[Product Card Id]` (One)
- Connect `fact_orders[Order Country]` (Many) to `dim_geography[Order Country]` (One)
- Connect `fact_orders[Order_Date]` (Many) to `dim_date[Date]` (One)

---

## 2. DAX Measures Library (Copy & Paste)

Create a new table named **`_Measures`** in Power BI and add the following DAX measures:

```dax
// 1. Total Revenue ($)
Total Revenue = SUM(fact_orders[Sales])

// 2. Total Profit ($)
Total Profit = SUM(fact_orders[Order Profit Per Order])

// 3. Overall Profit Margin (%)
Profit Margin % = DIVIDE([Total Profit], [Total Revenue], 0)

// 4. Total Orders
Total Orders = COUNTROWS(fact_orders)

// 5. Late Deliveries Count
Late Deliveries Count = CALCULATE(COUNTROWS(fact_orders), fact_orders[Late_delivery_risk] = 1)

// 6. Late Delivery Rate (%)
Late Delivery Rate % = DIVIDE([Late Deliveries Count], [Total Orders], 0)

// 7. Average Actual Shipping Days
Avg Shipping Days = AVERAGE(fact_orders[Days for shipping (real)])

// 8. Average Scheduled Shipping Days
Avg Scheduled Days = AVERAGE(fact_orders[Days for shipment (scheduled)])

// 9. Average Shipping Delay (Days)
Avg Shipping Delay = AVERAGE(fact_orders[Delivery_Delay_Days])

// 10. AI Predicted Late Risk Count
AI High Risk Orders = CALCULATE(COUNTROWS(fact_orders), fact_orders[risk_level] = "HIGH RISK")
```

---

## 3. Detailed 6-Page Visual Layout Specification

### Page 1: Executive Overview Dashboard
- **KPI Cards**: `Total Revenue`, `Total Profit`, `Profit Margin %`, `Late Delivery Rate %`.
- **Main Line Chart**: X-axis: `dim_date[Date]`, Y-axis: `Total Revenue` (Monthly Trend).
- **Bar Chart**: Y-axis: `fact_orders[Market]`, X-axis: `Total Revenue`.
- **Map Visual**: Location: `fact_orders[Order Country]`, Bubble size: `Total Revenue`.

### Page 2: Supply Chain & Logistics Operations
- **Donut Chart**: Legend: `fact_orders[Delivery Status]`, Values: `Total Orders`.
- **Clustered Bar Chart**: Y-axis: `fact_orders[Shipping Mode]`, X-axis: `Late Delivery Rate %`.
- **Matrix Visual**: Rows: `fact_orders[Order Region]`, Columns: `fact_orders[Shipping Mode]`, Values: `Avg Shipping Delay`.

### Page 3: Customer Intelligence & Segmentation
- **Donut Chart**: Legend: `dim_customers[Cluster_Label]`, Values: `Count of Customer Id`.
- **Scatter Plot**: X-axis: `dim_customers[Customer_Monetary]`, Y-axis: `dim_customers[Customer_Profit]`, Legend: `dim_customers[Cluster_Label]`.
- **Table Visual**: `Customer Id`, `Cluster_Label`, `Customer_Recency`, `Customer_Frequency`, `Customer_Monetary`.

### Page 4: Product & Category Analytics
- **Treemap Visual**: Group: `dim_products[Category Name]`, Values: `Total Revenue`.
- **Bar Chart**: Y-axis: `dim_products[Product Name]` (Top 10), X-axis: `Total Revenue`.
- **Scatter Plot**: X-axis: `fact_orders[Order Item Discount Rate]`, Y-axis: `Profit Margin %`.

### Page 5: Regional & Market Intelligence
- **Filled Map / Shape Map**: `fact_orders[Order Country]`, Color saturation: `Late Delivery Rate %`.
- **Bar Chart**: `fact_orders[Order Region]`, Values: `Total Profit`.

### Page 6: AI Predictions & Demand Forecasting
- **KPI Cards**: `AI High Risk Orders`, `Avg Predicted Shipping Days`.
- **Line & Stacked Column Chart**: X-axis: `dim_date[Date]`, Column: `Total Revenue`, Line: `fact_orders[late_probability]`.
- **Gauge Chart**: Target: 0.15 (15%), Actual: `Late Delivery Rate %`.

---
