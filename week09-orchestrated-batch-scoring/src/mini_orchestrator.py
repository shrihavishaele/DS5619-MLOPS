"""
A tiny local DAG orchestrator — enough to demonstrate the two ideas from
this week's lecture without needing an actual Airflow install (a scheduler,
webserver, and metadata database is a lot of infra for a 110-minute
session):

  1. A DAG is a dependency graph of tasks, executed in an order that
     respects those dependencies (topological order) — not just top to
     bottom in the file.
  2. Individual task retry: a task that fails transiently should be retried
     some number of times before the whole DAG is considered failed, the
     same as Airflow's per-task `retries` parameter.

Fill in the three functions marked # TODO. The `Task` dataclass above them
is given.
"""
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class Task:
    name: str
    fn: Callable[[dict], None]  # called as fn(context) -> mutates context in place
    depends_on: List[str] = field(default_factory=list)
    max_retries: int = 0
    retry_delay_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Part 1 — Topological order (a DAG is a dependency graph, not a list)
# ---------------------------------------------------------------------------

def topological_order(tasks: Dict[str, Task]) -> List[str]:
    """Given a dict of {task_name: Task}, return a list of task names such
    that every task appears AFTER all the tasks in its `depends_on`.

    If there's more than one valid order (e.g. two independent tasks that
    both depend on the same upstream task), any valid order is fine.

    If the tasks contain a dependency cycle (or a task depends on a name
    that doesn't exist in `tasks`), raise ValueError.

    Hint: Kahn's algorithm — compute in-degree (number of dependencies) for
    every task, repeatedly pick a task with in-degree 0, "remove" it
    (decrementing the in-degree of everything that depended on it), and
    append it to the result. If you run out of in-degree-0 tasks before
    placing every task, there's a cycle.
    """
    # Validate that all dependencies refer to existing tasks
    for name, task in tasks.items():
        for dep in task.depends_on:
            if dep not in tasks:
                raise ValueError(
                    f"Task '{name}' depends on unknown task '{dep}'"
                )

    # Build adjacency list and in-degree map (Kahn's algorithm)
    in_degree = {name: 0 for name in tasks}
    adj: Dict[str, List[str]] = {name: [] for name in tasks}

    for name, task in tasks.items():
        for dep in task.depends_on:
            adj[dep].append(name)
            in_degree[name] += 1

    # Start with all tasks that have no dependencies
    queue = [name for name, deg in in_degree.items() if deg == 0]
    result: List[str] = []

    while queue:
        curr = queue.pop(0)
        result.append(curr)
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(tasks):
        raise ValueError("Dependency cycle detected among tasks")

    return result


# ---------------------------------------------------------------------------
# Part 2 — Retry a single task
# ---------------------------------------------------------------------------

def run_task_with_retry(task: Task, context: dict) -> int:
    """Run `task.fn(context)`. If it raises, retry up to `task.max_retries`
    additional times (so max_retries=2 means up to 3 total attempts),
    sleeping `task.retry_delay_seconds` between attempts (use time.sleep).

    If the task eventually succeeds, return the number of attempts it took
    (1 if it succeeded on the first try).

    If it never succeeds, let the LAST exception propagate (don't swallow
    it) after all retries are exhausted.
    """
    total_attempts = 1 + task.max_retries
    for attempt in range(1, total_attempts + 1):
        try:
            task.fn(context)
            return attempt
        except Exception:
            if attempt == total_attempts:
                raise  # re-raise the last exception
            if task.retry_delay_seconds > 0:
                time.sleep(task.retry_delay_seconds)
    # unreachable, but satisfies type checkers
    return total_attempts


# ---------------------------------------------------------------------------
# Part 3 — Run the whole DAG
# ---------------------------------------------------------------------------

def run_dag(tasks: Dict[str, Task], context: dict) -> dict:
    """Run every task in `tasks` in an order that respects dependencies
    (use topological_order), passing the SAME `context` dict to every task
    (so a downstream task can read what an upstream task wrote into it —
    e.g. context["extract"] = [...] written by the "extract" task, read by
    the "score" task).

    For each task, run it via run_task_with_retry and record:
      task_results[name] = {"status": "success", "attempts": N}
    on success, or, if it ultimately fails:
      task_results[name] = {"status": "failed", "attempts": N, "error": str(exc)}
    and then STOP — don't run any tasks that come after a failed task in
    the order (this mirrors Airflow: downstream tasks don't run if an
    upstream one fails).

    Return {"order": <the order you computed>, "task_results": task_results}.
    """
    order = topological_order(tasks)
    task_results: dict = {}

    for name in order:
        task = tasks[name]
        try:
            attempts = run_task_with_retry(task, context)
            task_results[name] = {"status": "success", "attempts": attempts}
        except Exception as exc:
            task_results[name] = {
                "status": "failed",
                "attempts": task.max_retries + 1,
                "error": str(exc),
            }
            break

    return {"order": order, "task_results": task_results}
