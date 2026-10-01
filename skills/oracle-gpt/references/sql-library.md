# SQL Library
# OracleGPT Reference — SQL patterns, window functions, Supabase queries

---

## Window Functions Reference

Window functions are the most powerful and most underused SQL feature.
They perform calculations across related rows without collapsing them.

### Ranking Functions

```sql
-- ROW_NUMBER: unique sequential rank (no ties)
SELECT
  customer_id,
  order_date,
  amount,
  ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY order_date
  ) AS order_sequence
FROM orders;

-- RANK: allows ties, gaps in sequence
-- DENSE_RANK: allows ties, no gaps
SELECT
  product_id,
  revenue,
  RANK() OVER (ORDER BY revenue DESC) AS rank,
  DENSE_RANK() OVER (ORDER BY revenue DESC) AS dense_rank
FROM product_revenue;

-- NTILE: divide rows into N equal buckets
SELECT
  customer_id,
  lifetime_value,
  NTILE(4) OVER (ORDER BY lifetime_value DESC) AS quartile
FROM customer_ltv;
-- Quartile 1 = top 25% by LTV
```

### Lag/Lead — Period-over-Period

```sql
-- Month-over-month comparison
SELECT
  month,
  revenue,
  LAG(revenue, 1) OVER (ORDER BY month) AS prev_month,
  revenue - LAG(revenue, 1) OVER (ORDER BY month) AS abs_change,
  ROUND(
    100.0 * (revenue - LAG(revenue, 1) OVER (ORDER BY month))
    / NULLIF(LAG(revenue, 1) OVER (ORDER BY month), 0),
    1
  ) AS pct_change
FROM monthly_revenue;

-- Year-over-year (lag by 12 periods)
LAG(revenue, 12) OVER (ORDER BY month) AS same_month_last_year
```

### Running Totals and Moving Averages

```sql
-- Running total
SELECT
  date,
  daily_revenue,
  SUM(daily_revenue) OVER (
    ORDER BY date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_revenue

-- 7-day moving average
AVG(daily_revenue) OVER (
  ORDER BY date
  ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
) AS moving_avg_7d

-- 30-day rolling sum
SUM(daily_revenue) OVER (
  ORDER BY date
  ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
) AS rolling_30d_revenue
```

---

## Supabase / PostgreSQL Patterns

### Time Series with Gap Filling

```sql
-- Generate a complete date series (no gaps even if no data)
WITH date_series AS (
  SELECT generate_series(
    '2025-01-01'::date,
    '2025-04-30'::date,
    '1 day'::interval
  )::date AS date
),
daily_data AS (
  SELECT
    created_at::date AS date,
    COUNT(*) AS events,
    SUM(amount) AS revenue
  FROM transactions
  GROUP BY created_at::date
)
SELECT
  ds.date,
  COALESCE(dd.events, 0) AS events,
  COALESCE(dd.revenue, 0) AS revenue
FROM date_series ds
LEFT JOIN daily_data dd USING (date)
ORDER BY ds.date;
```

### JSONB Field Queries

```sql
-- Query JSONB metadata field
SELECT
  id,
  metadata->>'source' AS acquisition_source,
  (metadata->>'session_duration')::INT AS session_seconds,
  metadata->'tags' @> '["premium"]' AS is_premium
FROM events
WHERE metadata->>'country' = 'GR'
  AND (metadata->>'amount')::NUMERIC > 100;

-- Aggregate inside JSONB array
SELECT
  id,
  jsonb_array_length(metadata->'items') AS item_count
FROM orders;
```

### Multi-Tenant RLS-Aware Queries

```sql
-- Query respects RLS automatically when using Supabase client
-- For admin/service role queries that bypass RLS:
SELECT * FROM documents
WHERE company_afm = $1  -- Always filter explicitly even with bypass
  AND created_at >= NOW() - INTERVAL '30 days';

-- Checking RLS policies
SELECT
  schemaname,
  tablename,
  policyname,
  cmd,
  qual
FROM pg_policies
WHERE tablename = 'documents';
```

### Performance-Optimised Patterns

```sql
-- Use EXISTS instead of IN for large subqueries
-- Slow:
SELECT * FROM users WHERE id IN (SELECT user_id FROM purchases WHERE amount > 100);
-- Fast:
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM purchases p WHERE p.user_id = u.id AND p.amount > 100);

-- Partial index for frequent filtered queries
CREATE INDEX idx_active_users ON users(created_at)
WHERE status = 'active';  -- Only indexes active users

-- Materialised view for expensive recurring queries
CREATE MATERIALIZED VIEW monthly_summary AS
SELECT
  DATE_TRUNC('month', created_at) AS month,
  COUNT(*) AS transactions,
  SUM(amount) AS revenue
FROM orders
GROUP BY DATE_TRUNC('month', created_at);

-- Refresh:
REFRESH MATERIALIZED VIEW monthly_summary;
-- Schedule with pg_cron or external scheduler
```

---

## Google Sheets Formula Library

### Lookup and Reference

```
# XLOOKUP (modern replacement for VLOOKUP)
=XLOOKUP(A2, Sheet2!A:A, Sheet2!B:B, "Not found", 0)

# INDEX/MATCH (still useful for complex lookups)
=INDEX(Sheet2!B:B, MATCH(A2, Sheet2!A:A, 0))

# Two-condition lookup
=INDEX(C:C, MATCH(1, (A:A=E2)*(B:B=F2), 0))
```

### Aggregation with Conditions

```
# SUMIFS — sum with multiple conditions
=SUMIFS(amount_col, date_col, ">="&DATE(2025,1,1), status_col, "completed")

# COUNTIFS — count with conditions
=COUNTIFS(country_col, "GR", status_col, "active")

# AVERAGEIFS — average with conditions
=AVERAGEIFS(revenue_col, month_col, "January", type_col, "subscription")
```

### Dynamic Arrays

```
# FILTER — returns filtered array
=FILTER(A:C, (B:B="GR")*(C:C>100), "No results")

# SORT and SORTBY
=SORT(FILTER(A:B, B:B>0), 2, -1)  -- Sort by col 2 descending

# UNIQUE — deduplicate a range
=UNIQUE(A2:A1000)

# QUERY — SQL-like queries in Sheets
=QUERY(A:D, "SELECT A, B, SUM(C) WHERE D='active' GROUP BY A, B ORDER BY SUM(C) DESC", 1)
```

### Date Intelligence

```
# Month-over-month in Sheets
=SUMIFS(revenue, month, EOMONTH(TODAY(),-1)+1, month, "<="&EOMONTH(TODAY(),-1))

# Year-to-date
=SUMIFS(revenue, date, ">="&DATE(YEAR(TODAY()),1,1), date, "<="&TODAY())

# Rolling 30 days
=SUMIFS(revenue, date, ">"&(TODAY()-30), date, "<="&TODAY())
```

---

## Advanced Analytics Queries

### Customer Lifetime Value Calculation

```sql
-- LTV by acquisition channel
WITH customer_revenue AS (
  SELECT
    c.id AS customer_id,
    c.acquisition_channel,
    c.created_at AS first_purchase,
    SUM(o.amount) AS total_revenue,
    COUNT(o.id) AS order_count,
    MAX(o.created_at) AS last_purchase,
    EXTRACT(DAYS FROM MAX(o.created_at) - MIN(o.created_at)) AS customer_lifespan_days
  FROM customers c
  JOIN orders o ON c.id = o.customer_id
  WHERE o.status = 'completed'
  GROUP BY c.id, c.acquisition_channel, c.created_at
)
SELECT
  acquisition_channel,
  COUNT(customer_id) AS customers,
  ROUND(AVG(total_revenue), 2) AS avg_ltv,
  ROUND(AVG(order_count), 1) AS avg_orders,
  ROUND(AVG(customer_lifespan_days), 0) AS avg_lifespan_days,
  ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_revenue), 2) AS median_ltv
FROM customer_revenue
GROUP BY acquisition_channel
ORDER BY avg_ltv DESC;
```

### Churn Detection

```sql
-- Identify customers at risk of churning
-- (active customers with no activity in 60+ days)
WITH last_activity AS (
  SELECT
    customer_id,
    MAX(activity_date) AS last_seen,
    NOW()::DATE - MAX(activity_date) AS days_inactive
  FROM customer_activities
  GROUP BY customer_id
),
customer_profile AS (
  SELECT
    c.id,
    c.email,
    c.plan_tier,
    c.mrr,
    la.last_seen,
    la.days_inactive,
    CASE
      WHEN la.days_inactive BETWEEN 30 AND 59 THEN 'At Risk'
      WHEN la.days_inactive BETWEEN 60 AND 89 THEN 'High Risk'
      WHEN la.days_inactive >= 90 THEN 'Likely Churned'
      ELSE 'Active'
    END AS churn_risk
  FROM customers c
  LEFT JOIN last_activity la ON c.id = la.customer_id
  WHERE c.status = 'active'
)
SELECT
  churn_risk,
  COUNT(*) AS customers,
  SUM(mrr) AS at_risk_mrr,
  ROUND(AVG(days_inactive), 0) AS avg_days_inactive
FROM customer_profile
WHERE churn_risk != 'Active'
GROUP BY churn_risk
ORDER BY
  CASE churn_risk
    WHEN 'Likely Churned' THEN 1
    WHEN 'High Risk' THEN 2
    WHEN 'At Risk' THEN 3
  END;
```

### Revenue Attribution

```sql
-- First-touch vs last-touch attribution comparison
WITH first_touch AS (
  SELECT
    user_id,
    FIRST_VALUE(utm_source) OVER (
      PARTITION BY user_id ORDER BY session_date
    ) AS first_source
  FROM sessions
),
last_touch AS (
  SELECT
    user_id,
    LAST_VALUE(utm_source) OVER (
      PARTITION BY user_id
      ORDER BY session_date
      ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_source
  FROM sessions
  WHERE session_date <= (
    SELECT MIN(order_date) FROM orders o WHERE o.user_id = sessions.user_id
  )
),
conversions AS (
  SELECT user_id, SUM(amount) AS revenue
  FROM orders WHERE status = 'completed'
  GROUP BY user_id
)
SELECT
  ft.first_source,
  COUNT(c.user_id) AS first_touch_conversions,
  ROUND(SUM(c.revenue), 2) AS first_touch_revenue,
  lt.last_source,
  COUNT(c.user_id) AS last_touch_conversions
FROM first_touch ft
JOIN last_touch lt USING (user_id)
JOIN conversions c USING (user_id)
GROUP BY ft.first_source, lt.last_source
ORDER BY first_touch_revenue DESC;
```

### Geographic Performance

```sql
-- Revenue and growth by country
SELECT
  country,
  SUM(CASE WHEN DATE_TRUNC('month', created_at) = DATE_TRUNC('month', NOW()) 
      THEN amount ELSE 0 END) AS this_month,
  SUM(CASE WHEN DATE_TRUNC('month', created_at) = DATE_TRUNC('month', NOW() - INTERVAL '1 month')
      THEN amount ELSE 0 END) AS last_month,
  ROUND(
    100.0 * (
      SUM(CASE WHEN DATE_TRUNC('month', created_at) = DATE_TRUNC('month', NOW()) THEN amount ELSE 0 END) -
      SUM(CASE WHEN DATE_TRUNC('month', created_at) = DATE_TRUNC('month', NOW() - INTERVAL '1 month') THEN amount ELSE 0 END)
    ) / NULLIF(
      SUM(CASE WHEN DATE_TRUNC('month', created_at) = DATE_TRUNC('month', NOW() - INTERVAL '1 month') THEN amount ELSE 0 END), 0
    ), 1
  ) AS mom_growth_pct
FROM orders
WHERE status = 'completed'
  AND created_at >= NOW() - INTERVAL '2 months'
GROUP BY country
HAVING SUM(CASE WHEN DATE_TRUNC('month', created_at) = DATE_TRUNC('month', NOW()) THEN amount ELSE 0 END) > 0
ORDER BY this_month DESC;
```

---

## Excel Formula Advanced Patterns

### Financial Calculations

```
# CAGR (Compound Annual Growth Rate)
=(end_value/start_value)^(1/years)-1

# NPV (Net Present Value)
=NPV(discount_rate, cashflow_range) + initial_investment

# Running total with reset by category
=IF(A2=A1, B1+C2, C2)

# Weighted average
=SUMPRODUCT(weights_range, values_range)/SUM(weights_range)
```

### Text and Data Manipulation

```
# Extract domain from email
=MID(A2, FIND("@",A2)+1, LEN(A2))

# Standardise phone numbers (remove non-digits)
=REGEXREPLACE(A2,"[^0-9]","")

# Fuzzy match (approximate string matching — Sheets)
Not native — use VLOOKUP with wildcard:
=IFERROR(VLOOKUP("*"&A2&"*", B:C, 2, FALSE), "No match")

# Conditional concatenation
=TEXTJOIN(", ", TRUE, IF(B2:B10="active", A2:A10, ""))
```
