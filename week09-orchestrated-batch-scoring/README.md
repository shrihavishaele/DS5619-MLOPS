# Week 9: Orchestrated Batch Scoring

In this lab, we built a mini DAG orchestrator to run a batch-scoring pipeline with dependency management and automatic retries. The pipeline scores vehicle detection images across multiple camera feeds and demonstrates how production orchestrators like Airflow work under the hood.

Key components:
1. **Topological Ordering**: Sorts tasks using Kahn's algorithm so every task runs only after its dependencies, and detects cycles or missing dependencies.
2. **Task Retry Logic**: Retries failed tasks up to a configurable `max_retries` with a delay between attempts, re-raising the last exception if all retries are exhausted.
3. **DAG Execution**: Runs the full pipeline in dependency order with a shared context, stopping downstream tasks if an upstream task fails permanently.

By orchestrating tasks as a DAG with per-task retries, we can build reliable batch pipelines that tolerate transient failures without manual intervention!
