# ADR-041: Verification Telemetry Wiring

**Status:** Proposed 2026-03-07
**Date:** 2026-03-07
**Decision Makers:** Chris Joseph, LLM Council
**Related:** ADR-026 (Phase 3), ADR-040 (Phase 2 item 4)

---

## Context

Two existing ADRs promise telemetry capabilities that are not functioning in production:

### ADR-026 Phase 3: Dead Code

ADR-026 Phase 3 is marked `IMPLEMENTED` and delivered a complete `performance/` module (~700 lines, 70 tests) with:
- `ModelSessionMetric` — per-model per-session latency, Borda score, parse success
- `InternalPerformanceTracker` — rolling window aggregation with exponential decay
- `ModelPerformanceIndex` — p50/p95 latency, mean Borda, confidence levels
- `persist_session_performance_data()` — integration entry point
- JSONL storage following the `bias_persistence.py` pattern

**The problem:** `persist_session_performance_data()` is never called from any production code path. It is only called from tests. The performance store at `~/.llm-council/performance_metrics.jsonl` does not exist on any installation. The entire Phase 3 module is dead code.

This means:
- `get_quality_score()` always returns 50.0 (cold start) for every model
- `select_tier_models()` cannot use internal performance data for selection
- The ADR-029 audition mechanism's quality percentile graduation gate (`>= 75th percentile`) can never fire
- ADR-026's validation gate ("100+ sessions tracked") has never been met

### ADR-040 Phase 2 Item 4: Missing Observability

ADR-040 Phase 2 explicitly requires:
> "Add observability metrics (stage durations, timeout frequency, estimated vs actual duration)"

With success criteria:
> "P95 verification latency for high tier < 270s (4.5 min)"

And resolved question Q4:
> "Add instrumentation to track `char_count -> actual_duration` for data-driven refinement"

**The problem:** The verification pipeline (`verification/api.py`) uses `time.monotonic()` internally for waterfall budgeting but **discards all timing data**. No per-stage duration is recorded in transcripts. No total elapsed time appears in `result.json`. The success criteria cannot be measured.

Additionally, ADR-040's deferred options depend on this data:
- **Option E** (Tiered Stage 2 Optimization): "Deferred until Options A+D provide observability data"
- **Option F** (Early Consensus Termination): Requires stage duration data to tune thresholds

### Impact: High-Tier Timeouts Cannot Be Tuned

High-tier verifications frequently hit the global timeout (observed across 26 local transcript sessions, where `timeout_fired` and partial results indicate timeout-related failures). Without timing telemetry, we cannot:
1. Determine which stage is the bottleneck (Stage 1 vs Stage 2 vs Stage 3)
2. Identify which models are consistently slow
3. Validate whether the 1.5x timeout multiplier is appropriate
4. Measure whether waterfall budget ratios (50%/70%/remaining) are well-calibrated
5. Compare `char_count` to actual duration for input size limit refinement
6. Make data-driven decisions about ADR-040 Option E or F

### Current Data Available

The only data source is verification transcripts (`.council/logs/`), which contain:
- `request.json` — tier, paths, rubric_focus (no timing)
- `stage1.json` — model responses (no per-model latency)
- `stage2.json` — rankings (no per-reviewer latency)
- `stage3.json` — synthesis (no duration)
- `result.json` — verdict, confidence, `timeout_fired` (no elapsed time)

26 transcripts exist locally but none contain timing data.

## Decision

Wire the existing telemetry infrastructure into the verification pipeline. This is primarily an integration task — the storage, aggregation, and analysis code already exists.

### Phase 1: Transcript Timing (Verification Pipeline)

Record wall-clock timing in verification transcripts for immediate observability.

**1.1 Per-stage timing in `_run_verification_pipeline()`**

Initialize `stage_timings` at pipeline entry and record per-stage elapsed time. Timing must be captured even on timeout or error — this is the most valuable data for tuning.

```python
# Initialize at pipeline entry
partial_state["stage_timings"] = {}
pipeline_start = time.monotonic()

# Per-stage pattern (repeated for each stage)
stage1_start = time.monotonic()
try:
    # ... stage 1 execution ...
    pass
finally:
    # Always capture timing, even on exception/cancellation
    partial_state["stage_timings"]["stage1"] = int((time.monotonic() - stage1_start) * 1000)
```

On global timeout (`asyncio.CancelledError` from `wait_for`), `partial_state["stage_timings"]` contains whatever stages completed plus the in-progress stage's partial timing. The `finally` block ensures the current stage's elapsed time is recorded before cancellation propagates.

**1.2 Per-model latency in Stage 1 and Stage 2**

Stage 1 already returns `model_statuses` with `latency_ms` from the gateway. Persist this in `stage1.json`.

Stage 2's `asyncio.as_completed` path (ADR-040) records per-reviewer timing by wrapping each task with a start timestamp and computing delta on completion:

```python
# In stage2 as_completed path
task_start_times: Dict[str, float] = {}
for model in reviewers:
    task_start_times[model] = time.monotonic()
    # ... create task ...

# On completion
elapsed = int((time.monotonic() - task_start_times[model]) * 1000)
reviewer_timings[model] = elapsed
```

**1.3 Summary timing in `result.json`**

Add to transcript result. `budget_utilization` is defined as `total_elapsed_ms / global_deadline_ms` (ratio of time used to time available; always in [0, 1] for non-timeout cases, can exceed 1.0 if timeout fires mid-cleanup):

```json
{
  "timing": {
    "total_elapsed_ms": 142000,
    "stage1_elapsed_ms": 45000,
    "stage2_elapsed_ms": 78000,
    "stage3_elapsed_ms": 19000,
    "global_deadline_ms": 270000,
    "timeout_fired": false,
    "budget_utilization": 0.53
  },
  "input_metrics": {
    "content_chars": 32000,
    "tier_max_chars": 50000,
    "num_models": 4,
    "num_reviewers": 4
  }
}
```

On timeout, partially-completed stages appear with their elapsed time. Missing stages are omitted (not null), so consumers check key existence:

```json
{
  "timing": {
    "total_elapsed_ms": 270000,
    "stage1_elapsed_ms": 45000,
    "stage2_elapsed_ms": 225000,
    "global_deadline_ms": 270000,
    "timeout_fired": true,
    "budget_utilization": 1.0
  }
}
```

### Phase 2: Performance Tracker Integration

Wire `persist_session_performance_data()` into the verification pipeline so the ADR-026 Phase 3 tracker actually accumulates data.

**2.1 Call site in `run_verification()`**

The existing function signature (from `performance/integration.py`) is:

```python
def persist_session_performance_data(
    session_id: str,
    model_statuses: Dict[str, Dict[str, Any]],   # model_id -> {"latency_ms": int, ...}
    aggregate_rankings: Dict[str, Dict[str, Any]], # model_id -> {"borda_score": float, ...}
    stage2_results: Optional[List[Dict[str, Any]]] = None,
) -> int:
```

The verification pipeline produces these exact shapes:
- `model_statuses` from `stage1_collect_responses_with_status()` — confirmed compatible
- `aggregate_rankings` from `calculate_aggregate_rankings()` — confirmed compatible
- `stage2_results` from `stage2_collect_rankings()` — confirmed compatible

Call in a `finally` block after pipeline completion, wrapped in try/except to ensure telemetry failures never fail the verification:

```python
# In run_verification(), after pipeline completes (or times out)
try:
    persist_session_performance_data(
        session_id=verification_id,
        model_statuses=partial_state.get("model_statuses", {}),
        aggregate_rankings=partial_state.get("aggregate_rankings", {}),
        stage2_results=partial_state.get("stage2_results"),
    )
except Exception:
    logger.warning("Telemetry persistence failed", exc_info=True)
```

**Reliability constraint**: Telemetry persistence must never fail the verification pipeline. A high-tier verification taking minutes should never crash at the last step because a JSONL write failed (disk full, permissions, etc.).

**2.2 Call site in `consult_council` MCP tool (Deferred)**

The main council deliberation path in `mcp_server.py` also never calls the tracker. This is a separate integration with different data shapes and session semantics. Deferred to a follow-up task to keep this ADR focused on the verification pipeline.

**Concurrency note**: JSONL append writes are atomic on POSIX for lines under `PIPE_BUF` (4096 bytes on Linux/macOS). `ModelSessionMetric.to_jsonl_line()` produces ~200 bytes per record, well under this limit. The existing `bias_persistence.py` uses the same pattern in production. No file locking is required.

### Phase 3: Analysis CLI (Deferrable)

Extend the existing `bias-report` CLI pattern to add a `timing-report` command. This phase is a convenience tool and is explicitly deferrable — raw JSONL and transcript data can be analyzed with `jq` in the interim.

```bash
llm-council timing-report [--days N] [--tier TIER] [--format text|json]
```

Output:
- Per-tier P50/P95/P99 total elapsed time
- Per-stage P50/P95 breakdown
- Per-model P50/P95 latency
- Timeout frequency by tier
- `char_count` vs `actual_duration` correlation
- Budget utilization distribution

### What This Enables

Once data accumulates (target: 30+ sessions for PRELIMINARY confidence):
- **Timeout tuning**: Adjust `VERIFICATION_TIMEOUT_MULTIPLIER` based on P95 data
- **Budget ratio tuning**: Adjust 50%/70%/remaining waterfall based on actual stage proportions
- **Input limit refinement**: Adjust `TIER_MAX_CHARS` based on `char_count -> duration` correlation
- **Model selection feedback**: `select_tier_models()` uses real latency/quality data
- **ADR-040 Option E**: Data-driven Stage 2 optimization decisions
- **ADR-029 graduation**: Audition quality percentile gate becomes functional

### ADR Updates Required

1. **ADR-026 Phase 3**: Add "Known Gaps" subsection noting that wiring is incomplete, pointing to ADR-041
2. **ADR-040 Phase 2**: Add implementation status for item 4 pointing to ADR-041

## Consequences

### Positive
- **Existing investment pays off**: ~700 lines of performance tracking code becomes functional
- **Data-driven timeout tuning**: Replace guesswork with measured P95 latencies
- **ADR-040 success criteria measurable**: Can finally validate "P95 < 270s for high tier"
- **ADR-029 audition unblocked**: Quality percentile graduation gate becomes functional
- **Low risk**: No new abstractions — wiring existing code to existing call sites

### Negative
- **Disk usage**: JSONL files grow over time (~200 bytes per model per session). Data retention/rotation is deferred — at current usage rates (~30 sessions/month), annual growth is ~300KB, which does not warrant a rotation strategy yet.
- **Minor latency**: File I/O for persistence adds ~1-2ms per session (negligible vs 60-270s sessions)
- **Migration**: Old transcripts lack timing data; analysis tools must handle missing `timing` field gracefully
- **Test impact**: Integration tests that run real verification will create JSONL files; test fixtures should use temp directories with cleanup

### Neutral
- **No schema changes to VerifyResponse**: Timing data goes to transcripts and JSONL, not API response
- **Backward compatible**: transcript `result.json` gains new `timing` field (additive)

## Compliance / Validation

1. **Transcript timing test**: Verify `result.json` contains `timing` object with `total_elapsed_ms`, `global_deadline_ms`, `budget_utilization`, and at least one `stageN_elapsed_ms` field
2. **Timeout timing test**: Verify that on global timeout, `result.json` still contains partial `timing` data for completed and in-progress stages
3. **Performance store test**: Verify `~/.llm-council/performance_metrics.jsonl` is created and populated after a verification session
4. **Telemetry isolation test**: Verify that `persist_session_performance_data()` failure (simulated via mock raising IOError) does not affect the verification result
5. **Integration test**: Run 5 verification sessions, verify timing values are non-negative, stage times sum to approximately `total_elapsed_ms` (within 100ms measurement tolerance), and `budget_utilization` is in [0, 1] for non-timeout cases
6. **ADR-040 validation** (runtime, not code gate): After 30+ sessions, measure P95 high-tier latency against 270s target

## Council Deliberation (2026-03-07, Reasoning Tier)

**Models consulted:** gemini-3.1-pro-preview, claude-opus-4.6, deepseek-v3.2-speciale
**Consensus level:** Moderate (2 approved, 1 needs-review)

**Council feedback incorporated:**
1. **Error/timeout path timing** — Added `finally` blocks for stage timing capture, explicit timeout transcript example, and reliability constraint for persistence (all 3 reviewers)
2. **Function signature verification** — Added explicit signature from `performance/integration.py` with compatibility confirmation (Opus, DeepSeek)
3. **`partial_state["stage_timings"]` initialization** — Added explicit initialization at pipeline entry (Gemini, DeepSeek)
4. **Phase 2.2 scoping** — Deferred `consult_council` wiring to follow-up task (Opus)
5. **`budget_utilization` formula** — Defined as `total_elapsed_ms / global_deadline_ms` with edge case behavior (Opus)
6. **Concurrent write safety** — Added POSIX atomic append justification with `PIPE_BUF` analysis (Opus)
7. **Phase 3 deferrable** — Explicitly marked as deferrable with `jq` interim workaround (Opus)
8. **Telemetry isolation** — Added try/except wrapper and compliance test for persistence failure (Gemini, Opus)
9. **Data retention** — Added explicit deferral with growth estimate (Opus)
10. **Test impact** — Added note about temp directory fixtures (Opus)
11. **Claim substantiation** — Reworded "users report" to reference observed transcript data (Opus)
