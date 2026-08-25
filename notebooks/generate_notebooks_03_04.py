import json

# Notebook 03: EDA Visualization
nb3 = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Module 3: Exploratory Data Analysis (EDA)\n",
    "**Project**: Data-Driven Supply Chain Analytics for Business Decision Support  \n",
    "**Dataset**: Engineered DataCo Supply Chain Dataset (180,519 records × 68 attributes)  \n",
    "**Phase**: Phase 4 of 8 Execution Roadmap\n",
    "\n",
    "---  \n",
    "### Objectives:\n",
    "1. Visualize sales and gross revenue patterns across countries, product categories, and time.\n",
    "2. Analyze profit margin distributions and discount impact heatmaps.\n",
    "3. Investigate logistics bottlenecks: Late delivery rate across shipping modes and global markets.\n",
    "4. Generate and export 10 high-resolution charts to `reports/figures/`."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import sys\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "\n",
    "PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath('.'))) if os.path.basename(os.getcwd()) == 'notebooks' else os.getcwd()\n",
    "if PROJECT_ROOT not in sys.path:\n",
    "    sys.path.append(PROJECT_ROOT)\n",
    "\n",
    "from src.feature_engineering import ENGINEERED_DATASET_PATH"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "df = pd.read_csv(ENGINEERED_DATASET_PATH, low_memory=False)\n",
    "print(f\"Loaded Engineered Dataset: {df.shape[0]:,} rows × {df.shape[1]} columns.\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Top 10 Countries by Gross Revenue"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "plt.figure(figsize=(10, 5))\n",
    "top_countries = df.groupby('Order Country')['Sales'].sum().nlargest(10).reset_index()\n",
    "sns.barplot(data=top_countries, x='Sales', y='Order Country', hue='Order Country', palette='Blues_r', legend=False)\n",
    "plt.title('Top 10 Order Countries by Total Gross Revenue ($)', fontsize=12, fontweight='bold')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Late Delivery Risk by Shipping Mode"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "mode_perf = df.groupby('Shipping Mode')['Late_delivery_risk'].mean().reset_index()\n",
    "mode_perf['Late_Pct'] = mode_perf['Late_delivery_risk'] * 100\n",
    "plt.figure(figsize=(9, 5))\n",
    "sns.barplot(data=mode_perf, x='Shipping Mode', y='Late_Pct', hue='Shipping Mode', palette='magma', legend=False)\n",
    "plt.title('Late Delivery Rate (%) by Shipping Mode', fontsize=12, fontweight='bold')\n",
    "plt.axhline(50, color='red', linestyle='--', label='50% Threshold')\n",
    "plt.legend()\n",
    "plt.show()"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

# Notebook 04: Statistical Analysis
nb4 = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Module 4: Rigorous Statistical Analysis & Hypothesis Testing\n",
    "**Project**: Data-Driven Supply Chain Analytics for Business Decision Support  \n",
    "**Dataset**: Engineered DataCo Supply Chain Dataset (180,519 records × 68 attributes)  \n",
    "**Phase**: Phase 4 of 8 Execution Roadmap\n",
    "\n",
    "---  \n",
    "### Objectives:\n",
    "1. **Descriptive Statistics**: Compute central tendency, dispersion, skewness, and kurtosis across all numeric metrics.\n",
    "2. **Hypothesis Test 1 (Chi-Square)**: Test independence between `Shipping Mode` and `Late_delivery_risk`.\n",
    "3. **Hypothesis Test 2 (ANOVA)**: Test mean shipping days across global `Market` regions.\n",
    "4. **Hypothesis Test 3 (Welch's T-Test)**: Test profit margin difference for high vs low discount orders."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import sys\n",
    "import pandas as pd\n",
    "\n",
    "PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath('.'))) if os.path.basename(os.getcwd()) == 'notebooks' else os.getcwd()\n",
    "if PROJECT_ROOT not in sys.path:\n",
    "    sys.path.append(PROJECT_ROOT)\n",
    "\n",
    "from src.feature_engineering import ENGINEERED_DATASET_PATH\n",
    "from src.statistical_analysis import run_full_statistical_pipeline"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "df = pd.read_csv(ENGINEERED_DATASET_PATH, low_memory=False)\n",
    "desc_stats, summary = run_full_statistical_pipeline(df)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "desc_stats.head(12)"
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

with open("notebooks/03_eda_visualization.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb3, f, indent=1)

with open("notebooks/04_statistical_analysis.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb4, f, indent=1)

print("Generated 03_eda_visualization.ipynb and 04_statistical_analysis.ipynb successfully!")