# Refactor Plan: Final Fix for Council Scope Regression

## 1. Problem Statement
The previous "applied fix" inadvertently removed three variable assignments (`stage2_results`, `aggregate_rankings`, `label_to_model`) from the `run_council_pipeline` scope. These variables are required by the telemetry block, leading to a `NameError` and resulting in a `failed` status in reliability tests.

## 2. Proposed Changes

### A. Restore Scope Variables in `council.py`
Re-extract the following variables from `stage2_data` immediately after the `run_stage2` call.

```python
# council.py ~line 1140
stage2_data = await run_stage2(...)
usage_info.update(stage2_data["usage"])
# RESTORE THESE:
stage2_results = stage2_data["stage2_results"]
aggregate_rankings = stage2_data["aggregate_rankings"]
label_to_model = stage2_data["label_to_model"]
```

### B. Clean up redundancy in `council.py`
Remove the redundant `usage_info["stage1"] = stage1_data["usage"]` at line 1165 as it is already captured at line 1109.

## 3. Verification Plan
- **Pytest**: Run `tests/test_council_reliability.py` and ensure `15 passed`.
- **Telemetry Verification**: Ensure `result["metadata"]["usage"]["stages"]["stage3"]` is correctly populated.
