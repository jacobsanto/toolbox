# Governance Architecture
# CompassGPT Reference — Policy register, lifecycle, audit framework

---

## Policy Register Template

Maintain a master register of all company policies.
Review quarterly. Update whenever a policy changes.

```
POLICY REGISTER — [Company Name]
Last updated: [Date] | Owner: [HR/Legal/Compliance]

ID | Policy Name | Category | Version | Effective | Owner | Next Review | Status | Legal Review | Applies To
P01 | Data Protection Policy | GDPR | 2.1 | [Date] | DPO | Q2 2026 | Active | [Date] | All
P02 | Code of Conduct | HR | 1.3 | [Date] | HR | Q4 2026 | Active | [Date] | All
P03 | AI Usage Policy | IT | 1.0 | [Date] | IT | Q2 2026 | Active | Pending | All
P04 | Remote Work Policy | HR | 1.1 | [Date] | HR | Q3 2026 | Active | [Date] | Eligible
P05 | Whistleblower Policy | Compliance | 1.0 | [Date] | HR/Legal | Q4 2026 | Active | [Date] | All
P06 | Disciplinary Procedure | HR | 2.0 | [Date] | HR | Q4 2026 | Active | [Date] | All
P07 | Anti-Harassment Policy | HR | 1.2 | [Date] | HR | Q2 2026 | Active | [Date] | All
```

---

## Policy Lifecycle Framework

### Stage 1: Trigger Identification

A policy is needed when one of these triggers exists:

**Regulatory trigger:** New law or regulation requires it
**Risk trigger:** Incident reveals a gap in existing governance
**Growth trigger:** Company size or structure change creates new need
**Technology trigger:** New tool or capability requires governance
**Review trigger:** Existing policy reaches review date
**Request trigger:** Employees, auditors, or clients request it

### Stage 2: Policy Development

**Who does what:**

| Role | Responsibility |
|---|---|
| Policy owner | Drafts initial document, owns ongoing maintenance |
| HR | Employment law compliance, workforce communication |
| Legal | Legal review, regulatory compliance verification |
| IT | Technical policies, security requirements |
| Management | Final approval, resource commitment |
| Affected employees | Input on practicality (optional but improves adoption) |

**Development checklist:**
- [ ] Trigger and need documented
- [ ] Applicable laws and regulations identified
- [ ] Stakeholders consulted
- [ ] Draft produced
- [ ] Legal review completed (if required)
- [ ] Management approval obtained
- [ ] Version number assigned
- [ ] Effective date set

### Stage 3: Deployment

**Deployment methods by policy type:**

| Policy type | Recommended deployment |
|---|---|
| Data protection | All-staff email + HR system + acknowledgement required |
| Code of conduct | All-staff briefing + HR system + signature required |
| AI usage | All-staff email + training session + acknowledgement |
| Disciplinary procedure | HR system + manager training + accessible at all times |
| Remote work | Individual written agreement + HR system |
| Whistleblower | All-staff email + anonymous channel live + manager briefing |

### Stage 4: Communication

**The communication principle:**
Publishing a policy is not communicating a policy.
Employees who don't know a policy exists cannot be expected to comply with it.

**Communication plan template:**
```
Policy: [Name]
Effective date: [Date]
Who must know: [All / specific roles]

Communication steps:
1. Manager briefing: [Date] — [agenda, attendees]
2. All-staff email: [Date] — [draft included below]
3. HR system publication: [Date]
4. Acknowledgement deadline: [Date]
5. Training (if required): [Date, format]
6. Follow-up for non-acknowledgers: [Date]
```

### Stage 5: Acknowledgement Tracking

For regulated or high-risk policies, maintain acknowledgement records.

```
Acknowledgement Log: [Policy Name] v[X.X]
As of: [Date]

Employee | Department | Date acknowledged | Method | Follow-up sent
[Name]   | [Dept]     | [Date]            | Email  | N/A
[Name]   | [Dept]     | Pending           | -      | [Date]
```

Non-acknowledgement within 30 days: escalate to line manager.
Non-acknowledgement of mandatory policy within 60 days: HR formal action.

---

## Policy Audit Framework

### Annual Policy Audit

Conduct annually. Document results. Action findings.

**Audit scope:**
All policies in the policy register.

**For each policy:**

```
Policy: [Name] | Version: [X.X] | Last reviewed: [Date]

1. CURRENCY
Is this policy current with applicable law? [Yes / No — explain if No]
Legislative changes since last review: [List any relevant changes]
Action required: [None / Update / [REQUIRES LEGAL REVIEW]]

2. COMPLIANCE
Is the company operating in compliance with this policy? [Yes / Partially / No]
Evidence reviewed: [Log entries / incident reports / spot checks]
Gaps identified: [Describe]
Action required: [None / Process change / Training / Policy update]

3. AWARENESS
Do employees know this policy exists and what it requires? [Yes / Partially / No]
Acknowledgement rate: [X]%
Training completion rate (if applicable): [X]%
Action required: [None / Communication / Training]

4. ENFORCEMENT
Were any violations identified this year? [Yes / No]
Violations: [Count and categories — no names]
Enforcement actions taken: [Count and types]
Patterns identified: [Any recurring violation type]
Action required: [None / Process change / Policy clarification / Stronger consequences]

5. OVERALL ASSESSMENT
Policy status: [Active / Needs update / Requires replacement]
Priority: [High / Medium / Low]
Assigned to: [Owner] | Due: [Date]
```

### Compliance Gap Analysis

When starting governance work for a new company or after a significant change:

**Step 1: Inventory existing policies**
List all current policies, versions, and dates.

**Step 2: Identify required policies**
Based on: company size, industry, jurisdiction, activities.
Check against mandatory requirements (Greek law, GDPR, sector regulations).

**Step 3: Gap identification**
Required but missing: [List]
Existing but outdated: [List]
Existing but non-compliant: [List]

**Step 4: Prioritisation**
Priority 1 (immediate — legal requirement): [List]
Priority 2 (within 90 days — significant risk): [List]
Priority 3 (within 12 months — best practice): [List]

**Step 5: Remediation plan**
Policy | Gap | Action | Owner | Target date | Legal review needed
[Policy] | [Gap] | [Draft/Update] | [Name] | [Date] | [Yes/No]

---

## Governance for Different Company Stages

### Startup (1-10 employees)
**Minimum viable governance:**
- Data protection / GDPR policy
- Code of conduct (brief)
- Employment contract template
- Basic IT/security policy

**Not yet needed:**
- Whistleblower formal channel (under 50 employees)
- Full employee handbook
- Dedicated DPO

### Growing company (10-50 employees)
**Add:**
- Full employee handbook
- Remote/hybrid work policy
- Disciplinary procedure
- Expense and travel policy
- AI usage policy

### Mid-size (50-250 employees)
**Add / upgrade:**
- Whistleblower channel and policy (legally required at 50+)
- Anti-harassment policy (legally required at 20+ in Greece)
- Dedicated HR and legal function
- Formal policy register and audit cycle
- DPO consideration

### Enterprise (250+ employees)
**Full governance programme:**
- Whistleblower: mandatory and operational
- DPO: mandatory if large-scale personal data processing
- Full compliance programme with regular audits
- Board-level governance oversight
- Third-party compliance requirements (suppliers, partners)
