# NOTES.md — Week 9: Orchestrated Batch Scoring

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
student_id: 142301003
seed: 4193672056
Wrote 40 images across 2 camera profiles -> D:\DS5619-MLOPS\week09-orchestrated-batch-scoring\data\fixtures  
Wrote 163 annotations -> D:\DS5619-MLOPS\week09-orchestrated-batch-scoring\data\fixtures/_annotations.coco.json

## notify retry count

<!-- How many attempts did notify take in your run? (Check
     dag_run_summary.json.) -->

`notify` took **3 attempts** in my run.

From output:
```json
Execution order: ['extract', 'score', 'load', 'notify']
  extract: {'status': 'success', 'attempts': 1}
  score: {'status': 'success', 'attempts': 1}
  load: {'status': 'success', 'attempts': 1}
  notify: {'status': 'success', 'attempts': 3}
```

The task is configured with `max_retries=3`, meaning up to 4 total attempts are allowed. It succeeded on the 3rd attempt, which matches the design in `run_pipeline.py`: `notify()` intentionally raises a `RuntimeError` on attempts 1 and 2, then succeeds on attempt 3.

## Branch independence

<!-- Why does load still succeed even though notify — its "sibling" in the
     DAG — failed on its first two attempts? What does that tell you about
     how failures in one branch of a DAG should (or shouldn't) affect an
     unrelated branch? -->

`load` succeeds because it depends only on `score`, not `notify`:

```
extract --> score --> load
                 \--> notify
```

`load` and `notify` are independent sibling branches in the topological execution order. Orchestrators isolate task execution and propagate failures strictly **downstream along dependency edges**, never laterally to siblings. `notify`'s retries were contained within its own task slot, so `load` ran and completed unaffected.

**Takeaway:** Failures in one DAG branch must not block unrelated branches unless a shared upstream dependency (`extract` or `score`) fails.

## Retry cost under FinOps

<!-- Tying back to this week's FinOps content: if notify were a metered API
     call you paid for per attempt, what would you change about the retry
     strategy, and why is "retry every failed task the same way" a risky
     default once cost enters the picture? -->

If `notify` were a metered, pay-per-call API (e.g., Twilio, SendGrid), I would adjust the retry strategy:

1. **Lower `max_retries`**: Reduce from 3 to 1 (or 0 / fire-and-forget) for non-critical notifications.
2. **Exponential back-off**: Replace fixed delays with exponential back-off to avoid wasting paid calls while the service recovers.
3. **Filter by error type**: Retry only transient failures (`5xx`, network timeouts), never deterministic client errors (`4xx`).
4. **Circuit breaker**: Halt retries during sustained outages to prevent compounding costs across DAG runs.

**Why a uniform retry policy is risky under FinOps:**
Applying the same retry policy everywhere treats free local compute the same as paid external APIs. With `max_retries=3`, a failure can quadruple API spend per run. In high-frequency batch pipelines, this causes silent cost spikes because tasks eventually report "success" while burning through budget. Under FinOps, retry policies must be budgeted per task based on unit cost and criticality.
