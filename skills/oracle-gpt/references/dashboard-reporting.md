# Dashboard & Reporting Reference
# OracleGPT Reference — KPI frameworks, dashboard templates, report structures

---

## KPI Framework by Business Type

### SaaS / Subscription

**Revenue:**
- MRR (Monthly Recurring Revenue)
- ARR (Annual Recurring Revenue)
- MRR Growth Rate (MoM)
- Net Revenue Retention (NRR) — target >100%

**Acquisition:**
- CAC (Customer Acquisition Cost)
- New MRR (from new customers)
- Lead-to-customer conversion rate

**Retention:**
- Gross Churn Rate — target <2%/month for B2B
- Net Churn Rate (accounting for expansion)
- D1/D7/D30 retention (for consumer)

**Engagement:**
- DAU/MAU ratio — target >20%
- Feature adoption rate
- NPS — target >40

**Unit Economics:**
- LTV:CAC — target >3:1
- CAC payback period — target <18 months
- Gross Margin — target >70% for SaaS

---

### Hospitality / Short-Term Rental

**Revenue:**
- Total Revenue (per property, per portfolio)
- RevPAR (Revenue Per Available Room/Night)
- ADR (Average Daily Rate)
- Revenue vs. prior year / budget

**Occupancy:**
- Occupancy Rate (%) — nights booked / nights available
- Lead time (days between booking and arrival)
- Length of Stay (average)

**Quality:**
- Average review score (by platform)
- Review response rate
- Complaint rate

**Customer:**
- Returning guest rate (% who rebook)
- Direct booking rate (% not through OTA)
- Channel mix (Airbnb / Booking.com / direct / other)

**RevPAR formula:**
```
RevPAR = ADR × Occupancy Rate
OR
RevPAR = Total Revenue / Total Available Room Nights
```

---

### E-commerce / Retail

**Revenue:**
- Gross Revenue, Net Revenue (after returns)
- Revenue by channel, category, product

**Acquisition:**
- ROAS (Return on Ad Spend) — target >3:1 minimum
- CPA (Cost Per Acquisition)
- New vs. returning customer split

**Transaction:**
- AOV (Average Order Value)
- Cart abandonment rate — target <70%
- Conversion rate — target >2% for most categories

**Customer:**
- Repeat purchase rate
- Customer LTV
- RFM segmentation

---

### Marketplace

**Volume:**
- GMV (Gross Merchandise Value)
- Transaction count

**Take Rate:**
- Platform revenue / GMV — typically 10-30%

**Supply/Demand:**
- Active sellers vs. active buyers
- Liquidity ratio (transactions per listing)
- Repeat transaction rate (both sides)

---

## Dashboard Templates by Audience

### Executive Dashboard (Monthly)

```
┌─────────────────────────────────────────────────────────────────┐
│  EXECUTIVE DASHBOARD — [Company] — [Month Year]                  │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  REVENUE     │  CUSTOMERS   │  GROWTH      │  HEALTH           │
│  €[X]        │  [N]         │  +[X]%       │  [Score]          │
│  vs last mo  │  +[N] new    │  vs last mo  │  NPS / Churn      │
├──────────────┴──────────────┴──────────────┴───────────────────┤
│  REVENUE TREND (12 months)                                       │
│  [Line chart: revenue + target line]                             │
├─────────────────────────────────┬───────────────────────────────┤
│  ACQUISITION                    │  RETENTION                    │
│  [Bar chart: new customers MoM] │  [Cohort retention heatmap]  │
├─────────────────────────────────┴───────────────────────────────┤
│  KEY EXCEPTIONS THIS MONTH                                       │
│  ⚠ [Metric] is [X]% below target — [one-line context]          │
│  ✓ [Metric] reached [X] — highest in [period]                  │
└─────────────────────────────────────────────────────────────────┘
```

### Operational Dashboard (Daily/Weekly)

```
┌─────────────────────────────────────────────────────────────────┐
│  OPERATIONS — [Team] — [Date]                                    │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│ TODAY    │ THIS WEEK│ PENDING  │ ALERTS   │ VS TARGET          │
│ [X]      │ [X]      │ [X]      │ [N] ⚠   │ [%]               │
├──────────┴──────────┴──────────┴──────────┴────────────────────┤
│  TODAY'S ACTIVITY TABLE                                          │
│  [Time] | [Event] | [Status] | [Owner] | [Action needed]       │
├─────────────────────────────────────────────────────────────────┤
│  QUEUE / BACKLOG                                                 │
│  Item | Age | Priority | Owner | Due                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Reporting Cadence Design

### Recommended Reporting Calendar

| Report | Audience | Cadence | Delivery | Owner |
|---|---|---|---|---|
| Daily ops summary | Team leads | Daily 9am | Slack/email | Automated |
| Weekly performance | Management | Monday 8am | Email | Analytics |
| Monthly business review | Leadership | First Monday | Slide deck | CEO/CFO |
| Quarterly board update | Board | End of quarter | Presentation | CEO |
| Annual plan vs. actual | All | Year end | Report | Finance |

### Alert Design

Alerts reduce dashboard fatigue by surfacing only what requires action.

**Alert thresholds template:**

| Metric | Warning (amber) | Critical (red) | Action |
|---|---|---|---|
| Revenue (daily) | <80% of target | <60% of target | Notify Sales lead |
| Churn rate | >2.5%/month | >4%/month | Notify CEO |
| Error rate | >1% | >5% | Notify Engineering |
| Occupancy | <60% for 7+ days | <40% for 7+ days | Notify Operations |
| Review score | Below 4.2 | Below 4.0 | Notify Customer Success |

**Alert channels:**
- Operational alerts → Slack channel (immediate)
- Management alerts → Email (daily digest)
- Critical alerts → Phone/SMS (immediate, any time)

---

## Data Storytelling Framework

### The Situation-Complication-Resolution (SCR) Structure

For any analytical report or presentation:

**Situation:** What is the current state? (Facts, no interpretation)
"Revenue in Q1 was €X, representing Y% growth year-on-year."

**Complication:** What has changed or what problem exists?
"However, customer acquisition cost increased by 40%, reducing contribution margin."

**Resolution:** What does the data recommend?
"Analysis shows that Channel X has 3× better CAC than Channel Y.
Reallocating 30% of Channel Y budget to Channel X would recover margin
while maintaining growth."

### The "So What?" Chain

For every data point, ask "So what?" until you reach an action:

Data: "Churn rate increased to 3.2% this month."
So what? "We're losing customers faster than we're acquiring them."
So what? "At this rate, MRR will decline in 60 days."
So what? "We need to identify the cohort driving the churn."
Analysis: "Churn concentrated in customers acquired through Channel X, 
who have 2× the churn rate of other channels."
Action: "Pause Channel X acquisition while investigating onboarding quality for that segment."

The "So what?" chain converts data into decisions.
Data without a "So what?" is information, not insight.
