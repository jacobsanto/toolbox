# Product Frameworks
# BuildGPT Reference — PRD template, user stories, prioritisation matrices

---

## PRD Template

```
PRODUCT REQUIREMENTS DOCUMENT
[Product/Feature Name]
Version: 1.0 | Date: [Date] | Author: [Name] | Status: Draft/Review/Approved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. EXECUTIVE SUMMARY
Problem: [One sentence — what problem does this solve?]
Solution: [One sentence — how does this product/feature solve it?]
Success metric: [One metric — how will we know this worked?]
Target date: [Realistic date]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. PROBLEM STATEMENT
2.1 User problem
[Describe the problem from the user's perspective, grounded in evidence]
Evidence: [Interview quotes, analytics data, support tickets, NPS feedback]

2.2 Business opportunity
[Why does solving this problem matter to the business?]
Quantification: [How many users affected? Revenue at stake? Churn attributed?]

2.3 Current state
[How do users solve this problem today? Why is the current solution insufficient?]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. GOALS AND NON-GOALS
Goals (in priority order):
G1: [Primary outcome — user-focused]
G2: [Secondary outcome]
G3: [Tertiary outcome]

Non-goals (explicitly out of scope):
N1: [What we are not building — be specific]
N2: [What we are deferring and why]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. USER PERSONAS
Primary persona: [Name]
- Role/context: [Who they are]
- Jobs to be done: [What they're trying to accomplish]
- Current pain: [Specific frustration today]
- Success state: [What success looks like for them]

Secondary persona (if applicable): [Name]
[Same structure]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. USER JOURNEY
5.1 Current state (with pain)
Step 1: [What user does today]
Step 2: [Pain point here]
Step 3: [Workaround or failure]

5.2 Future state (with product)
Step 1: [What user does with our solution]
Step 2: [Where value is delivered]
Step 3: [Successful outcome]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. REQUIREMENTS
6.1 Functional requirements (MoSCoW prioritised)
MUST have:
FR1: [Requirement — specific and testable]
FR2: [Requirement]

SHOULD have:
FR3: [Requirement]

COULD have:
FR4: [Requirement]

6.2 Non-functional requirements
NFR1: Performance — [e.g., page load under 2s]
NFR2: Accessibility — [WCAG level]
NFR3: Security — [specific requirements]
NFR4: Scalability — [expected load]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. SUCCESS METRICS
Primary metric: [What we measure to know this worked]
Baseline: [Current value]
Target: [Target value]
Timeframe: [When we expect to hit it]

Secondary metrics:
M1: [Supporting metric]
M2: [Supporting metric]

Counter metrics (what we watch to prevent gaming):
C1: [Metric that breaks if we game the primary]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8. OPEN QUESTIONS
Q1: [Question] — Owner: [Name] — Due: [Date]
Q2: [Question] — Owner: [Name] — Due: [Date]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9. DEPENDENCIES
D1: [What this depends on] — Team: [Team] — Status: [Status]
D2: [External dependency] — Status: [Status]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

10. RISKS AND MITIGATIONS
R1: [Risk] — Likelihood: H/M/L — Impact: H/M/L — Mitigation: [Action]
R2: [Risk] — Likelihood: H/M/L — Impact: H/M/L — Mitigation: [Action]
```

---

## User Story Templates

### Standard User Story
```
Title: [Short, descriptive name]
Epic: [Parent epic name]
Priority: Must/Should/Could

Story:
As a [specific user type],
I want to [specific action],
So that [specific outcome].

Acceptance Criteria:
Scenario 1: [Happy path]
  Given [initial state]
  When [user action]
  Then [expected result]

Scenario 2: [Edge case]
  Given [initial state]
  When [edge case action]
  Then [expected handling]

Scenario 3: [Error state]
  Given [initial state]
  When [error condition]
  Then [error message/handling]

Definition of Done:
- [ ] Code complete and reviewed
- [ ] Unit tests written and passing
- [ ] Acceptance criteria verified by QA
- [ ] Accessibility requirements met
- [ ] Analytics events firing correctly
- [ ] Documentation updated
```

### Technical Story (Infrastructure/Non-visible)
```
Title: [Technical task name]
Type: Technical debt / Infrastructure / Performance

Problem:
[What technical issue exists and why it matters to users or the business]

Solution:
[What technical change will be made]

Acceptance Criteria:
- [ ] [Measurable technical outcome]
- [ ] [Performance benchmark]
- [ ] [No regression in existing functionality]

Why now:
[Why this is prioritised — what breaks or degrades without it]
```

---

## Prioritisation Matrix Templates

### RICE Scoring Sheet
```
Feature: [Name]
Estimated by: [Name] | Date: [Date]

REACH
Question: How many users will this affect per quarter?
Estimate: [Number] users/quarter
Confidence: High / Medium / Low
Score: [Number]

IMPACT
Question: How significantly does this affect each user?
Options: 3=Massive, 2=High, 1=Medium, 0.5=Low, 0.25=Minimal
Score: [Number]
Rationale: [Why this score]

CONFIDENCE
Question: How confident are we in Reach and Impact estimates?
Options: 100% / 80% / 50%
Score: [%]
Rationale: [What data exists? What are we assuming?]

EFFORT
Question: Total person-months across all functions
Breakdown: Engineering: [X] + Design: [X] + PM: [X] + QA: [X]
Total: [Number] person-months

RICE SCORE = (Reach × Impact × Confidence) / Effort
= ([Reach] × [Impact] × [Confidence]) / [Effort]
= [Score]
```

### Impact/Effort Matrix
```
Plot each feature on a 2x2:

HIGH IMPACT / LOW EFFORT → Quick wins: Do first
HIGH IMPACT / HIGH EFFORT → Major projects: Plan carefully
LOW IMPACT / LOW EFFORT → Fill-ins: Do when capacity allows
LOW IMPACT / HIGH EFFORT → Thankless tasks: Avoid or delegate

Features:
[Feature 1]: Impact [H/M/L] | Effort [H/M/L] → Quadrant: [Name]
[Feature 2]: Impact [H/M/L] | Effort [H/M/L] → Quadrant: [Name]
```

---

## Roadmap Templates

### Now/Next/Later Roadmap
```
NOW (Current quarter — committed)
✅ [Feature 1] — In progress — [Owner] — Target: [Date]
✅ [Feature 2] — Planned — [Owner] — Target: [Date]

NEXT (Next quarter — directionally committed)
🔜 [Feature 3] — Rationale: [Why this next]
🔜 [Feature 4] — Rationale: [Why this next]

LATER (6+ months — not committed)
📋 [Feature 5] — Condition: [What must be true to pursue]
📋 [Feature 6] — Condition: [What must be true to pursue]

NOT DOING (explicitly declined)
❌ [Feature 7] — Reason: [Why not]
```

### Outcome-Based Roadmap (preferred over feature roadmap)
```
Q1 THEME: [Outcome we're driving toward]
Hypothesis: If we [build X], then [users will do Y], which will [drive Z metric]
Bets:
  - [Initiative 1] → Expected outcome: [Metric change]
  - [Initiative 2] → Expected outcome: [Metric change]
Success looks like: [Metric at target value]

Q2 THEME: [Next outcome]
[Same structure]
```
