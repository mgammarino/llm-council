# Implementation Plan: Anti-Herding Persistence

Enables real-time model usage tracking to trigger the 35% anti-herding penalty when a single model's traffic share exceeds 30%. This prevents provider monocultures and improves system robustness during outages.

## User Review Required

> [!IMPORTANT]
> **Performance Impact**: Calculating traffic share requires reading the last ~500 lines of a JSONL file. I will implement a 5-minute cache for these calculations to ensure the `/ask` command remains fast.

## Proposed Changes

### [Component: Performance Tracker]
Add the intelligence to calculate usage shares from historical records.

#### [MODIFY] [tracker.py](file:///c:/git_projects/llm-council/src/llm_council/performance/tracker.py)
- Implement `get_recent_traffic_shares(window_size=100)`.
- It will count model occurrences in the last `N` sessions and return a percentage dictionary.
- Add basic TTL caching to prevent disk I/O on every query.

### [Component: Model Intelligence]
Connect the selection algorithm to the real-world data.

#### [MODIFY] [selection.py](file:///c:/git_projects/llm-council/src/llm_council/metadata/selection.py)
- Update `_create_candidates_from_pool()` to fetch real traffic percentages from the tracker.
- Replace the hardcoded `0.0` with the calculated share.

#### [MODIFY] [discovery.py](file:///c:/git_projects/llm-council/src/llm_council/metadata/discovery.py)
- Update `_create_candidate_from_info()` to also use the tracker for traffic data.

## Verification Plan

### Automated Tests
1. **Unit Test**: Create 100 fake usage records where `gpt-4o` has 90% share.
2. **Verification**: Verify that `select_tier_models` penalizes `gpt-4o` and prioritizes a different model (like `claude-3-5-sonnet`) even if `gpt-4o` has higher base quality.

### Manual Verification
- Run a "Stress Test" using the MCP server in Claude Desktop. 
- Ask 10 quick questions in a row.
- Verify in the logs that the "Recent Traffic" value for the primary model increases incrementally.
