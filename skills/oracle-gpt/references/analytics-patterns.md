# Analytics Patterns
# OracleGPT Reference — Python analytics, statistical methods, data quality

---

## Python Analytics Stack

```python
# Standard imports for data analysis
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
```

---

## Data Cleaning Patterns

```python
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standard data cleaning pipeline."""
    
    # 1. Remove exact duplicates
    initial_rows = len(df)
    df = df.drop_duplicates()
    print(f"Removed {initial_rows - len(df)} duplicate rows")
    
    # 2. Standardise column names
    df.columns = (df.columns
                  .str.lower()
                  .str.replace(' ', '_')
                  .str.replace('[^a-z0-9_]', '', regex=True))
    
    # 3. Parse dates (common formats)
    for col in df.select_dtypes(include='object').columns:
        if any(keyword in col for keyword in ['date', 'time', 'created', 'updated']):
            try:
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
            except:
                pass
    
    # 4. Standardise text fields
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip()
    
    # 5. Report null counts
    null_summary = df.isnull().sum()
    null_summary = null_summary[null_summary > 0]
    if len(null_summary) > 0:
        print(f"\nNull value summary:\n{null_summary}")
    
    return df

def detect_outliers_iqr(series: pd.Series, multiplier: float = 1.5):
    """Detect outliers using IQR method."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    outliers = series[(series < lower) | (series > upper)]
    return outliers, lower, upper
```

---

## SaaS Metrics Calculations

```python
def calculate_saas_metrics(df_revenue: pd.DataFrame) -> dict:
    """
    Calculate key SaaS metrics from a monthly revenue dataframe.
    Required columns: month, mrr, new_mrr, churned_mrr, customer_count
    """
    df = df_revenue.sort_values('month').copy()
    
    # MRR Growth Rate
    df['mrr_growth_rate'] = df['mrr'].pct_change() * 100
    
    # Net Revenue Retention (NRR)
    # NRR = (Beginning MRR + Expansion MRR - Churned MRR) / Beginning MRR
    if 'expansion_mrr' in df.columns:
        df['nrr'] = (
            (df['mrr'].shift(1) + df.get('expansion_mrr', 0) - df['churned_mrr'])
            / df['mrr'].shift(1) * 100
        )
    
    # Gross Churn Rate
    df['gross_churn_rate'] = (df['churned_mrr'] / df['mrr'].shift(1)) * 100
    
    # Quick Ratio (growth efficiency)
    df['quick_ratio'] = (df['new_mrr'] + df.get('expansion_mrr', 0)) / df['churned_mrr']
    
    return {
        'current_mrr': df['mrr'].iloc[-1],
        'mrr_3m_growth': df['mrr_growth_rate'].tail(3).mean(),
        'avg_gross_churn': df['gross_churn_rate'].tail(6).mean(),
        'latest_quick_ratio': df['quick_ratio'].iloc[-1],
        'arr': df['mrr'].iloc[-1] * 12
    }

def calculate_ltv_cac(
    avg_revenue_per_customer: float,
    gross_margin_pct: float,
    monthly_churn_rate: float,
    total_sales_marketing_spend: float,
    new_customers_acquired: int
) -> dict:
    """Calculate LTV:CAC ratio and payback period."""
    
    # LTV = (ARPU × Gross Margin) / Monthly Churn
    ltv = (avg_revenue_per_customer * (gross_margin_pct/100)) / (monthly_churn_rate/100)
    
    # CAC = Total spend / New customers
    cac = total_sales_marketing_spend / new_customers_acquired if new_customers_acquired > 0 else 0
    
    # CAC Payback Period (months)
    monthly_contribution = avg_revenue_per_customer * (gross_margin_pct/100)
    payback_months = cac / monthly_contribution if monthly_contribution > 0 else float('inf')
    
    return {
        'ltv': round(ltv, 2),
        'cac': round(cac, 2),
        'ltv_cac_ratio': round(ltv/cac, 2) if cac > 0 else float('inf'),
        'payback_months': round(payback_months, 1),
        'is_healthy': (ltv/cac >= 3) if cac > 0 else False
    }
```

---

## Cohort Analysis

```python
def build_cohort_table(df: pd.DataFrame,
                        user_col: str = 'user_id',
                        date_col: str = 'activity_date') -> pd.DataFrame:
    """
    Build a cohort retention table.
    Returns pivot table with cohort months as rows,
    periods since first activity as columns.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df['cohort_month'] = df.groupby(user_col)[date_col].transform('min').dt.to_period('M')
    df['activity_month'] = df[date_col].dt.to_period('M')
    df['periods_since_cohort'] = (df['activity_month'] - df['cohort_month']).apply(lambda x: x.n)
    
    cohort_data = df.groupby(['cohort_month', 'periods_since_cohort'])[user_col].nunique()
    cohort_table = cohort_data.unstack(fill_value=0)
    
    # Convert to retention percentages
    cohort_size = cohort_table.iloc[:, 0]
    retention = cohort_table.divide(cohort_size, axis=0) * 100
    
    return retention.round(1)
```

---

## Forecasting

```python
def forecast_with_trend_seasonality(
    series: pd.Series,
    periods_ahead: int = 12,
    seasonal_period: int = 12
) -> dict:
    """
    Simple trend + seasonality decomposition forecast.
    Uses STL decomposition where available, falls back to moving average.
    """
    try:
        from statsmodels.tsa.seasonal import STL
        stl = STL(series, seasonal=seasonal_period)
        result = stl.fit()
        
        # Forecast trend component
        trend = result.trend.dropna()
        slope, intercept, r2, *_ = stats.linregress(
            range(len(trend)), trend.values
        )
        
        forecast_trend = [
            intercept + slope * (len(trend) + i)
            for i in range(periods_ahead)
        ]
        
        # Use average seasonal pattern
        seasonal = result.seasonal
        seasonal_pattern = [
            seasonal.iloc[i::seasonal_period].mean()
            for i in range(seasonal_period)
        ]
        
        forecast = [
            forecast_trend[i] + seasonal_pattern[i % seasonal_period]
            for i in range(periods_ahead)
        ]
        
        return {
            'forecast': forecast,
            'method': 'STL decomposition',
            'r_squared': round(r2**2, 3)
        }
    except ImportError:
        # Fallback: simple linear trend
        x = np.arange(len(series))
        slope, intercept, r_value, *_ = stats.linregress(x, series.values)
        forecast = [intercept + slope * (len(series) + i) for i in range(periods_ahead)]
        return {
            'forecast': forecast,
            'method': 'Linear trend (fallback)',
            'r_squared': round(r_value**2, 3)
        }
```

---

## Hospitality Analytics (Arivia-Relevant)

```python
def calculate_hospitality_metrics(df_bookings: pd.DataFrame) -> dict:
    """
    Calculate core hospitality KPIs.
    Required columns: check_in, check_out, rate, status, property_id
    """
    df = df_bookings[df_bookings['status'] == 'completed'].copy()
    df['nights'] = (pd.to_datetime(df['check_out']) -
                    pd.to_datetime(df['check_in'])).dt.days
    df['revenue'] = df['rate'] * df['nights']

    # ADR (Average Daily Rate)
    adr = df['revenue'].sum() / df['nights'].sum()

    # Occupancy Rate (requires total available nights)
    # Calculated externally — passed in or computed from property data

    # RevPAR = ADR × Occupancy
    # Average Length of Stay
    alos = df['nights'].mean()

    # Revenue by channel (if channel column exists)
    channel_mix = {}
    if 'channel' in df.columns:
        channel_mix = df.groupby('channel')['revenue'].sum().to_dict()

    return {
        'total_revenue': round(df['revenue'].sum(), 2),
        'total_bookings': len(df),
        'total_nights': int(df['nights'].sum()),
        'adr': round(adr, 2),
        'alos': round(alos, 1),
        'channel_mix': channel_mix
    }

def review_score_trend(df_reviews: pd.DataFrame,
                        score_col: str = 'score',
                        date_col: str = 'review_date',
                        rolling_window: int = 30) -> pd.Series:
    """
    Calculate rolling average review score.
    """
    df = df_reviews.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).set_index(date_col)
    return df[score_col].rolling(f'{rolling_window}D').mean()
```

---

## Data Quality Checklist

Before any analysis, verify:

**Completeness:**
- [ ] Null rates per column documented
- [ ] Expected row count matches actual
- [ ] Date range covers expected period (no truncation)

**Accuracy:**
- [ ] Spot-check 10 random rows against source system
- [ ] Numeric ranges are plausible (no negative quantities, no future dates)
- [ ] Categorical values match expected set (no typos, no unexpected values)

**Consistency:**
- [ ] Join keys produce expected match rates (high unmatched = data issue)
- [ ] Aggregates reconcile with known totals
- [ ] Time zones are consistent (all UTC, or all local with documentation)

**Timeliness:**
- [ ] Data is as fresh as expected (check MAX(updated_at))
- [ ] No unexpected gaps in time series

**Interpretability:**
- [ ] Column definitions are documented and understood
- [ ] Business logic rules are clear (e.g., what constitutes a "completed" order)
- [ ] Any known anomalies are flagged before analysis begins

**The most expensive analytics mistake:**
Running a sophisticated analysis on dirty data.
The sophistication of the method does not compensate for the quality of the input.
Data quality checks take 20 minutes. Rebuilding trust after a bad analysis takes months.
