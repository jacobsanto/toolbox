# UX Research Methods
# BuildGPT Reference — Research methods, interview guides, testing protocols

---

## Research Method Selection Guide

| Method | Question answered | When | Users needed |
|---|---|---|---|
| Problem interviews | What problem exists? How painful? | Before building | 5-15 |
| Usability testing | Can users accomplish the task? | During/after building | 5 per round |
| Card sorting | How do users categorise? | IA design | 15-20 |
| Tree testing | Can users find things? | IA validation | 20-30 |
| Contextual inquiry | How do users work in context? | Deep discovery | 5-8 |
| Diary study | How does behaviour evolve? | Long-term patterns | 5-10 |
| Survey | How widespread is an opinion? | After qualitative | 100+ |
| A/B test | Which performs better? | Optimisation | Statistical significance |
| First click test | Where do users click first? | Navigation design | 20-30 |
| Five-second test | What's the first impression? | Landing pages | 20+ |

---

## Problem Interview Guide

### Before the Interview

**Purpose:** Understand the problem, not validate your solution.
**Golden rule:** Do not mention your product or solution. Ever. In discovery.
**Recruit:** People who currently have the problem, not people who want your product.

### Interview Structure (45-60 minutes)

**Opening (5 min)**
"Thank you for your time. I want to understand how you currently [problem domain].
There are no right or wrong answers. I'm not testing you — I'm trying to understand
your experience. Please think out loud and be honest, including when things aren't working."

**Context setting (10 min)**
"Tell me about your role and what a typical day looks like."
"How does [problem domain] fit into your work?"
"How often do you deal with [problem area]?"

**Problem exploration (25 min)**
"Tell me about the last time you had to [problem area]. Walk me through exactly what happened."
"What did you do first? Then what?"
"Where did you get stuck or frustrated?"
"What did you use to solve it? How did that work?"
"What do you wish you had that you don't?"
"How do you currently handle [specific pain point]?"
"What's the most frustrating part of this process?"

**Wrap up (10 min)**
"Is there anything else about this that you think would be important for me to understand?"
"Is there anyone else you think I should talk to?"

### Analysis
After 5+ interviews, look for:
- Recurring problems (mentioned by 3+ people without prompting)
- Emotional language (strongest signal of real pain)
- Workarounds (evidence the pain is severe enough to trigger action)
- Surprising findings (things you didn't expect)

---

## Usability Testing Protocol

### When to Run

- Before major feature launches (prototype test)
- After building but before shipping (functional test)
- On existing features with high support volume
- When analytics show unexpected user behaviour

### Session Setup

**Test with:** Real users from your target persona — not colleagues
**Session length:** 45-60 minutes for complex flows, 20-30 for single features
**Moderation:** Think-aloud protocol — ask users to narrate their thoughts
**Recording:** Always record (with consent) — you will miss things in real-time

### The Task Script

```
Task: [Specific, realistic task — not "use the feature", not "find the button"]

Context: "You are a [persona description]. You want to [realistic goal].
Starting from [specific starting point], please [task]."

Important: Do not say "click", "button", "menu" — use the language of the goal,
not the solution.

Good task: "You need to send your Q1 invoice to a client. Please do that."
Bad task: "Find the invoice creation button and create a new invoice."
```

### Think-Aloud Facilitation

**Ask these:** "What are you thinking?" "What are you expecting to happen?"
"What would you do next?" "What's confusing about this?"

**Never ask:** "Is this confusing?" (leading) "Did you find that easy?" (leading)
"Why didn't you click the button?" (they don't know why)

**When stuck:** Wait 30 seconds before intervening. Note confusion.
If completely blocked: "What would you normally do here?" then gently redirect.

### Finding Severity Classification

**Critical:** Most users cannot complete the core task → Must fix before launch
**Serious:** Some users fail or significantly struggle → Fix before launch
**Minor:** Small friction, workarounds exist → Fix if time allows
**Enhancement:** Would improve experience, not blocking → Future sprint

### The 5-User Rule

Test with 5 users. Fix critical issues. Test again with 5 more.
Do not run more than 5 users before iterating — you will keep finding the same issues.
The value is in iteration, not in volume.

---

## Jobs-to-be-Done Interview Guide

JTBD interviews focus on the moment of decision — when and why the user
chose to adopt a solution (including your product or a competitor's).

### The Switching Interview

For users who recently adopted your product (or a competitor's):

**The discovery question:**
"Take me back to the time just before you first started using [product].
What was going on in your life that led you to start looking for a solution?"

**The trigger question:**
"Was there a specific moment or event that made you realise you needed to do something?"

**The consideration question:**
"What else did you consider? Why did you choose [product] over the alternatives?"

**The first use question:**
"Tell me about the first time you used it. What were you hoping would happen?"

**The progress question:**
"What job were you hiring [product] to do? What problem were you trying to solve?"

### JTBD Story Format

From interviews, extract stories in this format:

**Situation:** When [specific situation/context]...
**Motivation:** I want to [action/capability]...
**Outcome:** So I can [desired progress]...

Examples:
"When I have multiple invoices to process at month end, I want to batch-process them,
so I can close my books without spending all day on manual entry."

"When a new team member joins, I want to onboard them in under an hour,
so I can get them productive before they lose motivation."

---

## Survey Design Guide

### When to Survey

Surveys answer "how many?" not "why?"
Use surveys after qualitative research has identified what to measure.
Never use surveys to discover problems — use interviews for that.

### Question Types

**NPS question (always last):**
"How likely are you to recommend [product] to a friend or colleague?"
0-10 scale. Promoters (9-10) minus Detractors (0-6) = NPS.

**CSAT question:**
"How satisfied are you with [specific experience]?"
1-5 or 1-7 scale. Report % satisfied (4-5 on 5-point scale).

**Likert scale:**
"[Statement]" → Strongly disagree / Disagree / Neutral / Agree / Strongly agree
Good for attitudes and opinions. Requires 7+ responses per segment for significance.

**Open text:**
"What is the primary reason for your score?"
Essential after NPS and CSAT — the number means nothing without the reason.

### Survey Design Rules

- Max 10 questions (5 is better)
- One question per question (no "and")
- No leading questions ("Don't you agree that...")
- No double negatives
- Always include "Other (please specify)" for multiple choice
- Test with 3 people before sending to full list
- Response rate target: 10-20% is typical, 30%+ is excellent

---

## A/B Testing Framework

### When A/B Testing is Appropriate

Requirements:
- Sufficient traffic (minimum ~1,000 unique visitors per variant per week)
- Clear hypothesis based on user research
- Single variable change (one thing at a time)
- Measurable primary metric identified before starting

### The Hypothesis Template

"We believe that [change] will cause [metric] to [increase/decrease] because [reason].
We will know this is true when [specific measurable outcome]."

### Statistical Significance

Minimum confidence: 95% (p < 0.05)
Minimum test duration: 2 weeks (to account for day-of-week variation)
Minimum sample: ~1,000 per variant for conversion rate tests

### What Not to A/B Test

- Significant UX overhauls (too many variables)
- Changes affecting <5% of traffic (insufficient power)
- Changes where ethical concerns exist
- Questions better answered by user interviews
