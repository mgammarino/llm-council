---
name: council-verify
description: |
  Verify code, documents, or implementation against requirements using LLM Council multi-model deliberation.
  Use when you need multi-model consensus on correctness, completeness, or quality.
  Keywords: verify, check, validate, review, approve, pass/fail, consensus, multi-model

license: Apache-2.0
compatibility: "llm-council >= 2.0, mcp >= 1.0"
metadata:
  category: verification
  domain: ai-governance
  council-version: "2.0"
  author: amiable-dev
  repository: https://github.com/amiable-dev/llm-council

allowed-tools: "Read Grep Glob mcp:llm-council/verify mcp:llm-council/audit"
---

# Council Verification Skill

Use LLM Council's multi-model deliberation to verify work with structured, machine-actionable verdicts.

## When to Use

- Verify code changes before committing
- Validate implementation against requirements
- Check documents for accuracy and completeness
- Get multi-model consensus on quality

## Workflow

1. **Capture Snapshot**: Capture current git diff or file state (snapshot pinning for reproducibility)
2. **Invoke Verification**: Call `mcp:llm-council/verify` with isolated context
3. **Receive Verdict**: Get structured JSON with verdict, confidence, and blocking issues
4. **Audit Trail**: Persist transcript via `mcp:llm-council/audit`

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `snapshot_id` | string | required | Git commit SHA for reproducibility |
| `rubric_focus` | string | null | Focus area: "Security", "Performance", "Accessibility" |
| `confidence_threshold` | float | 0.7 | Minimum confidence for PASS verdict |
| `tier` | string | "balanced" | Confidence tier: "quick", "balanced", "high", "reasoning" |

### Tier Selection Guide

| Tier | Use When | Timeout | Max Input |
|------|----------|---------|-----------|
| `quick` | Fast sanity checks, small diffs | ~30s | 15K chars |
| `balanced` | **Default.** Routine verification | ~90s | 30K chars |
| `high` | Security-critical reviews only | ~180s | 50K chars |
| `reasoning` | Complex architectural decisions | ~600s | 50K chars |

**Important**: `high`/`reasoning` use slow frontier models. For large diffs (>20K chars), prefer `balanced` to avoid timeouts.

## Output Schema

```json
{
  "verdict": "pass|fail|unclear",
  "confidence": 0.85,
  "rubric_scores": {
    "accuracy": 8.5,
    "completeness": 7.0,
    "clarity": 9.0,
    "conciseness": 8.0
  },
  "blocking_issues": [...],
  "rationale": "Chairman synthesis...",
  "transcript_location": ".council/logs/...",
  "partial": false,
  "timeout_fired": false,
  "completed_stages": ["stage1", "stage2", "stage3"],
  "timing": {
    "stage1_elapsed_ms": 45000,
    "stage2_elapsed_ms": 78000,
    "stage3_elapsed_ms": 19000,
    "total_elapsed_ms": 142000,
    "global_deadline_ms": 270000,
    "budget_utilization": 0.53
  },
  "input_metrics": {
    "content_chars": 32000,
    "tier_max_chars": 50000,
    "num_models": 4,
    "num_reviewers": 4,
    "tier": "high"
  }
}
```

### Timeout & Partial Results (ADR-040)

If `timeout_fired: true`, the tier deadline was exceeded. Check `completed_stages` for progress. Max input: quick=15K, balanced=30K, high/reasoning=50K chars. `timing.budget_utilization` shows time used vs deadline (1.0 on timeout). On timeout, only completed stages appear in `timing`.

## Exit Codes (for CI/CD)

- `0`: PASS - Approved with confidence >= threshold
- `1`: FAIL - Rejected
- `2`: UNCLEAR - Confidence below threshold, timeout, or oversized input

## Example Usage

```bash
council-verify --snapshot $(git rev-parse HEAD) --rubric-focus Security
council-verify --snapshot $(git rev-parse HEAD) --tier reasoning
```

## Progressive Disclosure

- **Level 1**: Metadata (~200 tokens)
- **Level 2**: Full instructions (~800 tokens)
- **Level 3**: See `references/rubrics.md`

## Related Skills

- `council-review`: Code review with structured feedback
- `council-gate`: CI/CD quality gate
