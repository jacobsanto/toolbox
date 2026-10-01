# Prompt Engineering Technique Library
# ArchitectGPT Reference — Full technique guide with application and debugging

---

## Technique Depth Guide

---

## Zero-Shot Prompting

**What it is:** A prompt with no examples — relies entirely on the model's training.
**When it works:** Clear, well-defined tasks where the model has strong training signal.
Simple questions, standard formats, well-understood domains.
**When it fails:** Novel formats, pattern-sensitive tasks, tasks requiring specific style.
**Optimisation:** Be more specific. Add output format. Add role if domain expertise matters.

---

## Few-Shot Prompting

**What it is:** Providing 2-5 examples of input → output pairs before the actual task.
**When it works:** Consistent formatting needed, classification tasks, style matching,
any task where showing is more effective than telling.
**When it fails:** When examples constrain the model too much (kills creativity),
when examples are low quality (model mimics the flaws).
**Number of examples:** 2-3 is usually optimal. More than 5 rarely helps and consumes tokens.
**Example quality:** Better 2 perfect examples than 5 mediocre ones.
**Example selection:** Diverse examples that cover the range of inputs.

---

## Chain-of-Thought (CoT)

**What it is:** Instructing the model to show its reasoning before giving an answer.
**Why it works:** Forces sequential processing that mirrors how complex reasoning works.
Errors in reasoning become visible and correctable.
**Variants:**
- Basic: "Think step by step"
- Zero-shot CoT: "Let's think step by step" appended to the prompt
- Few-shot CoT: Examples that show the reasoning process, not just the answer
- Self-consistency: Run CoT multiple times, take the most common answer
**When to use:** Math, logic, multi-step analysis, coding, complex decisions
**When NOT to use:** Factual lookups, creative generation, simple formatting tasks

---

## Role Prompting

**What it is:** Establishing a specific persona, expertise level, or perspective.
**When it works:** Domain-specific expertise needed, consistent voice required,
perspective-dependent analysis.
**When it's unnecessary:** Simple tasks where role adds no meaningful capability.
**Role construction:**
- Specific beats general: "Senior Greek tax attorney" > "legal expert"
- Include relevant constraints: "...who prioritises compliance over convenience"
- Include relevant context: "...working with SMEs in Greece"
**Caution:** Role prompting does not grant capabilities the model doesn't have.
It shapes the framing and vocabulary, not the underlying knowledge.

---

## System Prompts

**What it is:** Instructions that persist across the entire conversation (API/platform level).
**When to use:** Persistent persona, consistent output format, tool behaviour definition,
knowledge base injection, safety/compliance constraints.
**Best practices:**
- Keep system prompts focused — they consume tokens from every turn
- Be explicit about both what to do AND what not to do
- Order matters: role → context → constraints → format
- Test with adversarial inputs — users will try to override system prompts
**Claude-specific:** System prompts are highly respected. Clear, direct instructions work.
**GPT-specific:** System prompt can be "forgotten" in long conversations — reinforce.

---

## Structured Output Specification

**What it is:** Explicitly defining the format of the model's response.
**Why it matters:** Dramatically improves consistency, especially for downstream use.
**Methods:**
- JSON schema specification (GPT JSON mode, Claude structured outputs)
- Markdown template ("Respond using this structure: ##Header\n[content]")
- Example output ("Respond in exactly this format: [example]")
- Explicit field list ("Provide: Title, Summary, Key Points, Recommendation")
**Best practice:** Show a complete example of the desired output structure.

---

## Negative Constraints

**What it is:** Explicitly telling the model what NOT to do.
**When to use:** Preventing specific failure modes, compliance requirements,
style constraints, reducing verbosity.
**Examples:**
- "Do not include any disclaimers or caveats"
- "Do not suggest consulting a professional"
- "Do not repeat information already provided in the context"
- "Do not use passive voice"
**Caution:** Too many negative constraints confuse the model. Prioritise the most critical.

---

## Context Injection

**What it is:** Providing reference material the model should use as its knowledge source.
**When to use:** Domain-specific knowledge not in training, current information,
confidential data, structured reference material.
**Structure:**
- Label clearly: `<reference_document>`, `<knowledge_base>`, `<context>`
- Position before the task, not after
- For multiple documents, separate clearly and name each
**Grounding instruction:** "Base your response only on the provided documents.
If the information is not in the documents, say so explicitly."

---

## Step-Back Prompting

**What it is:** Asking the model to first identify the underlying principle before solving.
**Why it works:** Forces the model to access relevant knowledge before diving into specifics.
Reduces errors from misapplied specific knowledge.
**Structure:** "Before answering, identify the general principle or concept that applies here."
**When to use:** Complex questions where first principles reasoning helps,
legal/medical/technical questions where general frameworks matter.

---

## Self-Consistency

**What it is:** Generating multiple responses and selecting the most consistent answer.
**When to use:** High-stakes reasoning where accuracy matters more than speed.
**Implementation:** Run the same reasoning prompt 3-5 times, take majority answer.
**Cost:** Multiple API calls — use only when accuracy justifies the cost.

---

## ReAct (Reason + Act)

**What it is:** Interleaving reasoning and tool use in a structured loop.
**Structure:** Thought → Action → Observation → Thought → Action → ...
**When to use:** Agent workflows with tool access, research tasks, multi-step operations.
**Implementation:** Requires tool/function calling capability in the model.

---

## Prompt Debugging Guide

### Failure Type → Diagnosis → Fix

**Inconsistent outputs:**
Diagnosis: Task or format specification is ambiguous
Fix: Add explicit output format with example. Add constraints.

**Wrong assumptions:**
Diagnosis: Missing context
Fix: Add relevant background before the task. State what the model should assume.

**Ignoring constraints:**
Diagnosis: Constraints buried or contradictory
Fix: Move constraints to a clearly labelled section. Reduce total number of constraints.

**Hallucination:**
Diagnosis: Model inventing information
Fix: Add grounding instruction + source material. "Answer only from the provided documents."

**Over-refusal:**
Diagnosis: Framing triggers safety mechanisms
Fix: Add context that legitimises the request. Frame professionally. Add role.

**Wrong length:**
Diagnosis: Length constraint missing
Fix: Add explicit word/sentence count. "Respond in exactly 3 sentences."

**Persona drift:**
Diagnosis: System prompt not strong enough for multi-turn
Fix: Reinforce role at start of user messages. Add "Remember: you are [role]."

**Reasoning errors:**
Diagnosis: Model skipping reasoning steps
Fix: Add chain-of-thought instruction. Add "Show your reasoning before your answer."

**Example contamination:**
Diagnosis: Examples too rigid — output only matches examples
Fix: Diversify examples. Add: "These examples show format only, not the range of outputs."

---

## Token Optimisation

Every token costs money and consumes context window.
Optimise without sacrificing clarity.

**Reduce:**
- Remove pleasantries ("Please could you kindly...")
- Remove redundant context (only include what the model needs)
- Use consistent formatting (model processes consistent structure faster)

**Never reduce:**
- Specificity in the task
- Output format specification
- Critical constraints
- Examples when pattern matters

**Context window management:**
- System prompt: keep focused, ideally under 500 tokens
- Each example: under 200 tokens
- User context: provide only what's relevant to this specific task
- Total prompt: leave room for the response (tokens in + tokens out = context window)
