# ADR-F-001: Adversarial Critique Protocol (Stage 1B)

## Status
**Accepted** (Implemented 04/2026)

## Context
The standard 3-stage LLM Council deliberation (Stage 1: Research, Stage 2: Peer Review, Stage 3: Synthesis) relies on independent researchers. However, in complex technical domains, models often exhibit "Positive Bias" or shared hallucinations. There was a need for a dedicated "Forensic Auditor" role that explicitly searches for flaws in the initial Stage 1 responses before they are shared with the rest of the council.

## Decision
We implemented **Stage 1B: Adversarial Critique**.

1.  **Sequential Execution**: The Adversary (Devil's Advocate) acts *after* Stage 1 responses are collected but *before* Stage 2 peer reviews begin.
2.  **Role Isolation**: One model is reserved exclusively for the Adversary role (`adversary_prompt.py`). This model does not provide an initial opinion.
3.  **Context Injection**: The resulting "Dissenting Report" is injected into the context for all models in Stage 2 (Peer Review) and Stage 3 (Synthesis).
4.  **Interface**: Triggered via the `--adversary` CLI flag or `adversarial_mode=True` in the MCP/API layer.

## Consequences
- **Latency**: Adds a sequential LLM call, effectively doubling the time for Phase 1.
- **Robustness**: Prevents "Consensus Cascades" where multiple models agree on a wrong answer.
- **Quality**: Improves synthesis by providing the Chairman with a structured list of potential risks and hallucinations to address.

## References
- [Implementation Plan (04/09/2026)](file:///c:/git_projects/llm-council/plan/implementation_plan_adversarial_da_04092026.md)
- [Adversary Prompt Template](file:///c:/git_projects/llm-council/src/llm_council/adversary_prompt.py)
