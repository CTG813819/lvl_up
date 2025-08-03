# Difficulty Adjustment and XP Persistence Fixes

## Issues Identified

1. **Difficulty not decreasing despite consecutive failures**: The system was calculating difficulty based on AI level instead of current stored difficulty
2. **XP not being persisted properly**: XP was being calculated but not properly saved to database
3. **Difficulty showing as "unknown" in test history**: Test history entries weren't getting the difficulty field properly

## Fixes Implemented

### 1. New Difficulty Calculation Method

Added `_calculate_difficulty_from_current_metrics()` method that:
- Gets current difficulty from database instead of calculating from AI level
- Uses the stored `current_difficulty` as the base for adjustments
- Applies performance-based adjustments to the current difficulty
- Falls back to AI level calculation if no metrics exist

### 2. Updated Difficulty Calculation in Tests

Modified `administer_custody_test()` to use:
```python
difficulty = await self._calculate_difficulty_from_current_metrics(ai_type, recent_performance)
```

Instead of:
```python
difficulty = self._calculate_test_difficulty(ai_level, recent_performance)
```

### 3. Updated Metrics Update Method

Modified `_update_custody_metrics()` to use:
```python
new_difficulty = await self._calculate_difficulty_from_current_metrics(ai_type, performance_data)
```

And added XP persistence fix:
```python
metrics["xp"] = metrics.get("custody_xp", 0)  # Ensure XP field is set
```

### 4. Fixed Test History Difficulty Logging

Enhanced test history entry creation to properly set difficulty:
```python
# Ensure difficulty is properly set from test result
if test_result.get("difficulty"):
    test_history_entry["difficulty"] = test_result["difficulty"]
elif test_result.get("test_difficulty"):
    test_history_entry["difficulty"] = test_result["test_difficulty"]
```

## Expected Behavior After Fixes

1. **Difficulty should decrease**: With 103+ consecutive failures, difficulty should decrease from "intermediate" to "basic"
2. **XP should persist**: XP should be properly saved and loaded from database
3. **Test history should show correct difficulty**: Test history entries should show actual difficulty instead of "unknown"

## Testing

The fixes ensure that:
- Difficulty is calculated based on current stored difficulty, not AI level
- Performance-based adjustments are applied to the current difficulty
- XP is properly persisted to database
- Test history entries include the correct difficulty value

## Files Modified

- `ai-backend-python/app/services/custody_protocol_service.py`
  - Added `_calculate_difficulty_from_current_metrics()` method
  - Updated `administer_custody_test()` to use new method
  - Updated `_update_custody_metrics()` to use new method
  - Fixed XP persistence
  - Fixed test history difficulty logging 