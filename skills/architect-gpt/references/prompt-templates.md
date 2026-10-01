# Prompt Templates by Platform & Use Case
# ArchitectGPT Reference — Ready-to-use structures

---

## Universal Prompt Template

The base structure that works across all major models.
Adapt components based on task requirements.

```
[ROLE — optional but powerful]
You are [specific expertise/persona]. You [key characteristic that matters for this task].

[CONTEXT]
[Background information the model needs. What does it need to know about the situation?]

[TASK]
[What exactly should the model do? Be specific. One task per prompt.]

[CONSTRAINTS]
- [What must NOT be done]
- [Format requirements]
- [Length requirements]
- [Tone/style requirements]
- [Compliance requirements if any]

[OUTPUT FORMAT]
Respond in the following format:
[Exact structure you want]

[EXAMPLES — optional, use when pattern matters]
Example input: [...]
Example output: [...]
```

---

## Claude-Specific Templates

### Claude System Prompt Template
```xml
<system>
You are [role]. You specialise in [specific domain].

<context>
[Persistent context that applies to all interactions]
</context>

<capabilities>
[What you can and cannot do in this context]
</capabilities>

<output_style>
[Consistent formatting and response style]
</output_style>
</system>
```

### Claude Long Document Analysis
```xml
<document>
[Insert full document here]
</document>

<task>
Analyse the document above and provide:
1. [Specific extraction 1]
2. [Specific extraction 2]
3. [Specific extraction 3]
</task>

<format>
Respond in structured JSON with the following fields:
{
  "field1": "...",
  "field2": "...",
  "field3": "..."
}
</format>
```

### Claude Chain-of-Thought Template
```
Think through this step by step before providing your answer.

[Problem statement]

Work through your reasoning:
1. First, consider [aspect 1]
2. Then evaluate [aspect 2]
3. Finally, determine [aspect 3]

Only provide your conclusion after completing all reasoning steps.
```

---

## GPT-4o / ChatGPT Templates

### Structured Data Extraction (JSON Mode)
```json
{
  "model": "gpt-4o",
  "response_format": {"type": "json_object"},
  "messages": [
    {
      "role": "system",
      "content": "You extract structured data from text. Always respond with valid JSON matching the requested schema."
    },
    {
      "role": "user",
      "content": "Extract the following from this text: [fields]. Text: [content]\n\nRespond with JSON: {\"field1\": ..., \"field2\": ...}"
    }
  ]
}
```

### GPT Builder System Prompt Template
```
# [GPT Name]

## Role
You are [specific role]. Your purpose is [clear purpose statement].

## Capabilities
You can:
- [Capability 1]
- [Capability 2]
- [Capability 3]

You cannot:
- [Boundary 1]
- [Boundary 2]

## Behaviour
- [Consistent behaviour 1]
- [Consistent behaviour 2]

## Output Format
[Default response format and structure]

## Tone
[Specific tone guidance]
```

---

## Gemini Templates

### Multimodal Analysis Template
```
Analyse the [image/video/document] provided.

Focus specifically on:
1. [What to extract/analyse]
2. [What to ignore]

Provide your analysis in the following structure:
- Summary: [one paragraph]
- Key findings: [bullet points]
- Recommendations: [if applicable]
```

### Long Context Document Template
```
The following [X] documents contain [description of content].

[DOCUMENTS]

Based on these documents, answer the following:
[Specific question or task]

Requirements:
- Base your answer only on the provided documents
- Cite the specific document and section for each claim
- If information is not available in the documents, state this explicitly
```

---

## Vibe Coding Templates

### Lovable.dev — App Initialisation Prompt
```
Build a [type of application] with the following specifications:

**Core purpose:** [One sentence description]

**Target users:** [Who will use this]

**Data model:**
- [Entity 1]: [fields and types]
- [Entity 2]: [fields and types]
- Relationships: [how entities relate]

**Core features (MVP only):**
1. [Feature 1 — specific and bounded]
2. [Feature 2 — specific and bounded]
3. [Feature 3 — specific and bounded]

**Tech stack:**
- Frontend: React + TypeScript + Tailwind
- Backend: Supabase (auth, database, storage)
- Do not add any dependencies not listed above

**Design:**
- Style: [minimal/modern/etc]
- Colour scheme: [specific colours or "default"]

Build the foundation first — data model and authentication.
Do not build UI until the data layer is confirmed.
```

### Lovable.dev — Feature Addition Prompt
```
Add [specific feature] to the existing application.

**What it should do:**
[Exact behaviour, step by step]

**Where it fits:**
[Which page/component/section]

**Data requirements:**
[Any new database fields or tables needed]

**Do not change:**
- [Existing component 1]
- [Existing component 2]
- The current authentication flow

Confirm the data model change before building the UI.
```

### Bolt.new — Targeted Component Edit
```
In the file [exact file path], make the following change:

**Current behaviour:** [What it does now]
**Required behaviour:** [What it should do]
**Specific change:** [Exact modification needed]

Do not modify any other files.
Do not change the component's props interface.
Do not change any styling outside this component.
```

### Claude Code — Agentic Task
```
Task: [Clear, specific task description]

**Scope:**
- Files to modify: [list specific files or directories]
- Files NOT to touch: [explicit exclusions]

**Requirements:**
1. [Requirement 1 — measurable]
2. [Requirement 2 — measurable]
3. [Requirement 3 — measurable]

**Definition of done:**
[How you'll know the task is complete]

**If you encounter [specific scenario]:**
[How to handle it]

Start by reading [specific file] to understand the current implementation.
Then make only the changes necessary to satisfy the requirements above.
```

---

## Specialised Use Case Templates

### Classification Prompt
```
Classify the following [input type] into one of these categories:
[Category 1]: [definition]
[Category 2]: [definition]
[Category 3]: [definition]

Rules:
- If the input matches multiple categories, choose the most specific
- If the input matches no category, respond with "Unclassified"
- Respond with only the category name, nothing else

Input: [text to classify]
```

### Extraction Prompt
```
Extract the following information from the text below.
If a field is not present in the text, use null.

Fields to extract:
- [Field 1]: [description and format]
- [Field 2]: [description and format]
- [Field 3]: [description and format]

Text:
[Input text]

Respond only with the extracted data in JSON format.
Do not include any explanation or commentary.
```

### Evaluation/Grading Prompt
```
Evaluate the following [output type] against these criteria:

Criteria:
1. [Criterion 1] — Weight: [X]%
2. [Criterion 2] — Weight: [X]%
3. [Criterion 3] — Weight: [X]%

For each criterion:
- Score: 1-10
- Reasoning: one sentence
- Improvement: specific suggestion

[Content to evaluate]

End with an overall score (weighted average) and top priority improvement.
```

### Summarisation with Constraints
```
Summarise the following [content type].

Requirements:
- Length: [exact word count or range]
- Audience: [who will read this]
- Focus: [what matters most to this audience]
- Exclude: [what to leave out]
- Tone: [formal/conversational/technical]

[Content to summarise]
```
