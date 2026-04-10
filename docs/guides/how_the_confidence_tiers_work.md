# Council Confidence Tiers

The difference between the tiers is essentially a trade-off between **certainty (Consensus)** and **speed (Latency)**.

Per the orchestration logic in `tier_contract.py`, the council changes its entire "personality" based on the tier you select:

### ⚡ `quick` Tier (The "Sprint")
*   **No Voting**: The council skips Stage 2 entirely to save time.
*   **The Workflow**: Every model in the pool (e.g., GPT-5-mini, Haiku-4.5, Qwen-Turbo) generates its response in parallel.
*   **Chairman Persona**: **Summarizer**. Because Stage 2 is skipped, the Chairman receives no peer-review data. Their role is purely to condense the Stage 1 outputs into a clear, single answer.
*   **Ideal for**: Facts, code snippets, or simple explanations where you just want a second and third opinion without a delay.

### ⚖️ `balanced` Tier (The "Jury")
*   **Full Peer Review**: Peer review is active.
*   **The Workflow**: After models generate responses (Stage 1), they are anonymized (Stage 1.5) and sent back to each other. Every model must rank and score its peers' work (Stage 2).
*   **Chairman Persona**: **Mediator**. The Chairman receives a **Borda Count** (a mathematical ranking) of which models were voted "best" by their peers and uses that consensus to resolve any conflicts between the answers.
*   **Ideal for**: Technical comparisons, complex trade-offs, or open-ended advice where you want the "wisdom of the crowd" to filter out low-quality answers.

### 🏛️ `high` Tier (The "Congress")
*   **Maximum Rigor**: Follows the same deep-deliberation structure as balanced but with upgraded hardware and logic.
*   **The Workflow**: Identical to the **Balanced** peer-review logic (Stages 1, 1.5, 2, and 3), but upgraded for maximum rigor. It swaps "Economy" models for **Frontier** models and increases `max_attempts` to **3**, allowing the council to automatically discard and retry deliberations if consensus isn't reached on the first pass.
*   **Chairman Persona**: **Lead Synthesizer**. Powered by a top-tier frontier model, the Chairman performs deep synthesis, weaving together the most advanced insights from the council while specifically highlighting the most rigorously peer-reviewed sections.
*   **Ideal for**: High-stakes decisions, complex architectural reviews, or anything where a subtle error would be costly.

### 🧠 `reasoning` Tier (The "Think Tank")
*   **Deep Deliberation**: Specifically designed for models with internal "Chain of Thought" (CoT) capabilities (e.g., o1, o3, DeepSeek-R1).
*   **The Workflow**: Since these models generate massive text volumes, the council provides a **10-minute time budget** and an **8,192 token limit** to prevent truncation of long reasoning paths.
*   **Chairman Persona**: **Logical Auditor**. Uses **Claude Opus 4.6** to carefully audit the long-form Chain of Thought (CoT) outputs from the council members. Rather than just mediating, it checks the internal logical consistency of the "Thinking" models to extract the most mathematically or theoretically sound conclusion.
*   **Ideal for**: Solving complex math/logic puzzles, deep architectural debugging, or multi-step strategic planning.

## Comparison Table

| Feature | `quick` | `balanced` | `high` | `reasoning` |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 2 (Voting)** | **No** | **Yes** | **Yes** | **Yes** |
| **Peer Ranking** | None | Borda Count | Borda Count + Detail | Comprehensive |
| **Model Class** | Economy (Turbo/Flash) | Standard (Pro) | Frontier (Opus/GPT-5) | Reasoning (o1/R1) |
| **Global Deadline** | 30 seconds | 90 seconds | 180 seconds | 600 seconds |
| **Chairman Role** | Summarizer | Mediator | Lead Synthesizer | Logical Auditor |

!!! tip "Pro-tip"
    You can see this in action by asking the council for something complex (like "Explain Quantum Physics") using `tier="quick"` and then again with `tier="high"`. In the latter, you'll see a `### Council Rankings` section appear because the voting stage was activated!
