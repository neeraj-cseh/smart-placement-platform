# Algorithm: Readiness Score Calculation
* **Objective**: Compute a 0-100 metric for employability.
* **Complexity**: O(N) where N is the number of tracks. Optimized to O(1) database queries via ORM Aggregation.
* **Workflow**:
  1. `score += (TopicAccuracy * 0.35)`
  2. `score += (TrackProgress * 0.25)`
  3. `score += (MockTestAvg * 0.15)`
  4. `score += (CompanyReadiness * 0.15)`
  5. `score += (AIAvgScore * 0.10)`
