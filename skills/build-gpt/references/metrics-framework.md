# Product Metrics Framework
# BuildGPT Reference — Metrics by stage, North Star, OKRs, HEART

---

## The Metrics Hierarchy

### Level 1: North Star Metric
The single metric that best captures whether users get core value.
One per product. Changes rarely. Directs every other decision.

**How to choose a North Star:**
- It captures actual value delivered to the user (not revenue)
- It is a leading indicator of long-term business health
- Teams can influence it through their work
- It does not encourage gaming at the expense of real user value

**Examples by product type:**
| Product type | North Star |
|---|---|
| Social network | Daily active users or posts created |
| E-commerce | Successful purchases per month |
| SaaS (productivity) | Features used per active user |
| Marketplace | Transactions completed |
| Media/content | Time spent consuming |
| Communication tool | Messages sent |
| Accounting software | Documents correctly processed |
| Travel booking | Nights booked |

### Level 2: Input Metrics
Actions teams can directly take that predict North Star movement.
These are what squads work on.

### Level 3: Output Metrics
Revenue, retention, NPS — what results from getting inputs right.

### Counter Metrics
What breaks if you game the North Star?
Always define and track alongside it.

---

## Metrics by Product Stage

### Pre-PMF (Before Product-Market Fit)

**Primary question:** Do users get real value from this product?

| Metric | Target signal | Warning signal |
|---|---|---|
| Retention (Day 1) | >40% | Under 25% |
| Retention (Day 7) | >20% | Under 10% |
| Retention (Day 30) | >10% | Under 5% |
| Sean Ellis PMF score | >40% "very disappointed" | Under 40% |
| NPS | >30 | Under 0 |
| Referral rate | Organic growth | Zero organic |

**The Sean Ellis PMF Survey:**
"How would you feel if you could no longer use [product]?"
Very disappointed / Somewhat disappointed / Not disappointed / N/A
If 40%+ say "very disappointed" → you have PMF. Below 40% → keep iterating.

### Growth Stage (After PMF)

| Metric | Description | Target |
|---|---|---|
| DAU/MAU ratio | Engagement ratio (sticky product) | >20% good, >50% excellent |
| Activation rate | New users reaching first value | Varies — set baseline and improve |
| D1/D7/D30 retention | Cohort retention curves | Flattening = PMF signal |
| Viral coefficient (K) | New users per existing user | K>1 = viral, K<1 = need paid |
| CAC (Customer Acquisition Cost) | Cost to acquire one customer | CAC < LTV/3 |
| LTV (Lifetime Value) | Revenue per customer over lifetime | LTV > 3× CAC |
| MRR/ARR growth rate | Monthly/Annual recurring revenue | 10-15%/month for strong SaaS |

### Mature Stage

| Metric | Description | Focus |
|---|---|---|
| Net Revenue Retention | Revenue retained + expanded from existing | Target >100% (expansion > churn) |
| Gross churn rate | Customers lost per period | B2B SaaS target: <2%/month |
| NPS | Net Promoter Score | Track trend, not just number |
| CSAT | Customer Satisfaction | Per touchpoint and overall |
| Support ticket volume | Proxy for product confusion | Should decrease over time |

---

## The HEART Framework

Google's framework for user-centred metrics.

**Happiness:** Do users like the product?
- NPS, CSAT, app store ratings, survey satisfaction scores

**Engagement:** Are users using the product meaningfully?
- DAU, sessions per user, features used, depth of use

**Adoption:** Are new users successfully adopting the product?
- Activation rate, time to first value, onboarding completion rate

**Retention:** Are users coming back?
- D1/D7/D30 retention, churn rate, return visit rate

**Task success:** Can users accomplish their goals?
- Task completion rate, error rate, time on task

**Apply HEART to specific features, not just the product overall.**
A new feature should be evaluated on its own HEART metrics.

---

## OKR Framework

### OKR Structure
```
Objective: [Qualitative, inspiring, directional]
  Key Result 1: [Quantitative, measurable, time-bound]
  Key Result 2: [Quantitative, measurable, time-bound]
  Key Result 3: [Quantitative, measurable, time-bound]
```

### OKR Quality Criteria

**Good Objective:**
- Directional and inspiring
- Not a metric itself (that's a KR)
- Achievable in one quarter
- Connects to company strategy

**Good Key Result:**
- Quantitative and measurable
- Outcome-focused (not output/task)
- Ambitious but achievable (60-70% completion target)
- Has a clear baseline and target

**OKR Examples:**

Objective: Help users get value from the product faster
KR1: Increase Day-1 activation rate from 35% to 55%
KR2: Reduce time to first value from 12 minutes to 6 minutes
KR3: Increase completion of onboarding flow from 40% to 65%

Objective: Build a loyal user base that returns regularly
KR1: Increase D30 retention from 15% to 25%
KR2: Increase DAU/MAU ratio from 18% to 30%
KR3: Achieve NPS of 40+ (from current 22)

### OKR Anti-Patterns

**Output OKRs (tasks, not outcomes):**
Bad: "Launch feature X by Q2"
Good: "Increase [metric] by [amount] — feature X is one initiative toward this"

**Health metric OKRs (maintain, not improve):**
Bad: "Maintain uptime above 99.9%"
Good: Use health metrics as constraints, not OKRs

**Too many OKRs:**
Max 3-5 objectives per team per quarter.
If everything is a priority, nothing is.

---

## Cohort Analysis Framework

### Retention Cohort Table

Track each cohort of users from their signup date:

| Cohort | Day 1 | Day 7 | Day 14 | Day 30 | Day 60 | Day 90 |
|---|---|---|---|---|---|---|
| Jan users | 100% | 45% | 32% | 20% | 15% | 12% |
| Feb users | 100% | 48% | 35% | 23% | 17% | 14% |
| Mar users | 100% | 52% | 38% | 26% | 20% | 17% |

**Reading the table:**
- Are retention curves improving over time? (Feb better than Jan? — product improving)
- Where is the biggest drop-off? (That's your top activation/engagement problem)
- Is the curve flattening? (Flat tail = PMF; declining to zero = no PMF)

### Revenue Cohort Analysis

Same structure but tracking revenue per cohort over time.
Expansion: if revenue per cohort increases over time → strong product
Contraction: if revenue decreases → users finding less value or leaving

---

## Funnel Metrics

### Generic Product Funnel

| Stage | Metric | Definition |
|---|---|---|
| Acquisition | Signups | New registered users per period |
| Activation | Activated users | Users who completed key action in first session |
| Engagement | Active users | Users with meaningful activity in period |
| Retention | Retained users | Active users returning after first period |
| Revenue | Paying users | Users on paid plan |
| Referral | Referred users | New users from existing user referral |

**Conversion rate between each stage:**
Acquisition → Activation: typically 20-60%
Activation → Retention: typically 15-40%
Retention → Revenue: varies by business model
Revenue → Referral: typically 5-20%

Track where users drop and invest in improving that stage first.
