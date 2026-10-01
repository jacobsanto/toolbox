# AI Workflow Patterns & Agent Design
# ArchitectGPT Reference — Multi-step AI workflows and agent architecture

---

## Workflow Design Principles

### The Single Responsibility Principle
Each prompt in a workflow does one thing.
Multi-task prompts fail when one task fails, taking the whole prompt with it.
Break complex workflows into stages — each stage does exactly one job.

### The Explicit Handoff Principle
The output of each stage must be explicitly formatted as the input of the next.
Never assume format compatibility between stages.
Design the handoff as carefully as the stage itself.

### The Minimum Model Principle
Use the smallest/cheapest model that can reliably complete each stage.
Classification → small model
Extraction → small model
Reasoning → larger model
Generation → model calibrated to quality requirement
Cost compounds across stages. Right-size every stage.

### The Fail-Safe Principle
Every stage can fail. Design for graceful failure.
Define what happens when a stage produces unexpected output.
Validate output before passing to the next stage.

---

## Core Workflow Patterns

---

### Pattern 1: Sequential Pipeline

```
Input → [Stage 1] → [Stage 2] → [Stage 3] → Output
```

**Use for:** Document processing, content generation chains,
multi-step analysis, report generation.

**Example: Document Intelligence Pipeline**
```
Raw document
    ↓
[Stage 1: Extraction] — Extract structured data from document
    ↓
[Stage 2: Validation] — Verify extraction completeness and accuracy
    ↓
[Stage 3: Analysis] — Analyse extracted data against criteria
    ↓
[Stage 4: Report] — Generate human-readable summary
    ↓
Structured report
```

**Implementation notes:**
- Each stage receives previous stage's output as input
- Validate output schema at each handoff
- Log inputs and outputs at each stage for debugging

---

### Pattern 2: Classifier → Router

```
Input → [Classifier] → Branch A / Branch B / Branch C
```

**Use for:** Customer service triage, content moderation,
multi-domain Q&A, intent detection.

**Example: Support Request Router**
```
Customer message
    ↓
[Classifier: Category Detection]
Outputs: billing | technical | general | urgent
    ↓
billing → [BillingGPT specialist prompt]
technical → [TechGPT specialist prompt]
general → [GeneralGPT prompt]
urgent → [Escalation handler]
```

**Classifier prompt design:**
- Provide clear category definitions
- Include edge cases and how to handle them
- Request confidence score alongside classification
- Define fallback for ambiguous inputs

---

### Pattern 3: Generate → Evaluate → Refine

```
Input → [Generator] → [Evaluator] → [Refiner] → Output
         ↑___________________________|
         (loop until criteria met)
```

**Use for:** Content quality improvement, code review and fix,
answer accuracy improvement, creative iteration.

**Example: Copy Quality Loop**
```
Brief
    ↓
[Generator] — Produce first draft copy
    ↓
[Evaluator] — Score against criteria (conversion, brand voice, etc.)
    ↓
Score < threshold?
    Yes → [Refiner] — Improve based on evaluation feedback → back to Evaluator
    No → Approved copy
```

**Loop management:**
- Set maximum iterations (3-5 is usually sufficient)
- Define clear evaluation criteria with scores
- Evaluator must produce actionable feedback, not just scores
- Track improvement across iterations

---

### Pattern 4: Parallel Processing → Merge

```
Input → [Branch A] ─┐
      → [Branch B] ─┤→ [Merger] → Output
      → [Branch C] ─┘
```

**Use for:** Multi-perspective analysis, parallel research,
redundancy for accuracy, processing multiple data sources simultaneously.

**Example: Multi-Source Research**
```
Research question
    ↓
Simultaneously:
[Source A analyst] [Source B analyst] [Source C analyst]
    ↓                   ↓                   ↓
Findings A         Findings B         Findings C
    └───────────────────┼───────────────────┘
                        ↓
            [Synthesis prompt]
            Merge findings, resolve conflicts,
            produce unified answer
```

---

### Pattern 5: Agent Loop (ReAct)

```
Task → [Reason] → [Act: tool call] → [Observe: result] → [Reason] → ... → Answer
```

**Use for:** Research tasks, code generation with testing,
multi-step operations with real-world tools, autonomous task completion.

**ReAct structure:**
```
Thought: I need to [reasoning about next step]
Action: [tool name]([parameters])
Observation: [tool result]
Thought: Based on the observation, I should [next reasoning]
Action: [next tool call]
...
Answer: [final answer based on accumulated observations]
```

**Tool design principles:**
- Each tool does one thing reliably
- Tools return structured, predictable output
- Error states are explicit and descriptive
- Tool descriptions must be precise — the model chooses tools based on descriptions

---

### Pattern 6: Map-Reduce

```
Large input → [Split] → [Map: process each chunk] → [Reduce: aggregate] → Output
```

**Use for:** Processing documents longer than context window,
analysing large datasets, bulk operations.

**Example: Large Document Analysis**
```
100-page document
    ↓
[Splitter] — Split into 10 chunks with overlap
    ↓
[Map phase] — Run analysis prompt on each chunk independently
    ↓
10 chunk analyses
    ↓
[Reduce phase] — Aggregate chunk analyses into unified findings
```

**Chunk design:**
- Overlap between chunks (200-500 tokens) prevents context loss at boundaries
- Each chunk must be self-contained enough for meaningful analysis
- Chunk size: leave room for the prompt + response within context window

---

## Agent Design Patterns

### Specialist Agent Network

Multiple specialist agents with an orchestrator:

```
[Orchestrator]
    ↓
Routes to appropriate specialist based on task type
    ↓
[Legal Agent] [Marketing Agent] [Technical Agent] [Finance Agent]
    ↓
Each specialist has:
- Domain-specific system prompt
- Relevant tools
- Output format specification
    ↓
Results return to Orchestrator for synthesis
```

**Orchestrator responsibilities:**
- Intent classification
- Context passing
- Result synthesis
- Conflict resolution between specialists

### Memory-Augmented Agent

```
[User input]
    ↓
[Memory retrieval] — Retrieve relevant past context
    ↓
[Augmented prompt] — Input + relevant memory
    ↓
[Agent response]
    ↓
[Memory update] — Store new context for future retrieval
```

**Memory types:**
- Short-term: conversation history (in context)
- Long-term: persistent storage (Supabase, vector database)
- Episodic: specific past interactions
- Semantic: knowledge base entries

---

## Cost & Performance Optimisation

### Model Selection by Stage

| Stage type | Recommended model tier |
|---|---|
| Classification (binary/category) | Small (Haiku, GPT-3.5) |
| Extraction (structured fields) | Small-Medium |
| Summarisation (short) | Small-Medium |
| Complex reasoning | Large (Opus, GPT-4o) |
| Code generation | Medium-Large |
| Creative generation | Medium-Large |
| Quality evaluation | Medium-Large |

### Caching Strategy
Cache intermediate results when:
- The same input produces the same output (deterministic stages)
- API costs are significant
- Latency matters less than cost

### Batching
Process multiple inputs in a single API call when:
- Classification tasks (batch N items in one prompt)
- Extraction tasks (process multiple records)
- The model can maintain quality across batched items (test this)

### Latency Optimisation
- Parallel stages reduce total latency
- Streaming reduces perceived latency for user-facing outputs
- Pre-compute what can be pre-computed
- Cache aggressively at every layer
