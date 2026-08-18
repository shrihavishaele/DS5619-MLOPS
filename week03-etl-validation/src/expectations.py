"""
A minimal, from-scratch expectations framework in the spirit of Great
Expectations / data contracts (this week's lecture). You are implementing
the checking logic yourself rather than importing a library — the goal is
to understand what these tools actually do under the hood.

Fill in the four functions marked # TODO. Do not change the Violation
dataclass or any function signature.
"""
from dataclasses import dataclass


@dataclass
class Violation:
    expectation: str      # name of the check, e.g. "expect_column_not_null"
    column: str            # which column it was checking
    row_index: int          # index into the rows list where it failed
    detail: str              # short human-readable reason


def _is_null(value):
    return value is None or (isinstance(value, str) and value.strip() == "")


def expect_column_not_null(rows, column):
    """Return a Violation for every row where rows[i][column] is null/empty."""
    # TODO: implement
    violations = []

    for i, rows in enumerate(rows):
        if _is_null(rows.get(column)):
            violations.append(Violation(
                expectation="expect_column_not_null",
                column=column,
                row_index=i,
                detail=f"column {column} is missing or null"
            ))
    return violations

def expect_column_positive(rows, column):
    """Return a Violation for every row where rows[i][column], cast to float,
    is not strictly greater than 0. If the value can't be cast to float at
    all, that also counts as a violation (detail should say so).
    """
    # TODO: implement
    violations = []
    for i, row in enumerate(rows):
        val = row.get(column)
        try:
            f_val = float(val)
            if f_val <= 0:
                violations.append(Violation(
                    expectation="expect_column_positive",
                    column=column,
                    row_index=i,
                    detail=f"Value {f_val} is not strictly positive."
                ))
        except (ValueError, TypeError):
            violations.append(Violation(
                expectation="expect_column_positive",
                column=column,
                row_index=i,
                detail=f"Value {val} cannot be cast to float."
            ))
    return violations


def expect_column_in_set(rows, column, allowed_values):
    """Return a Violation for every row where rows[i][column] is not a member
    of allowed_values (a set or list you're given).
    """
    # TODO: implement
    violations = []

    for i, rows in enumerate(rows):
        val = rows.get(column)
        if val not in allowed_values:
            violations.append(Violation(
                expectation="expect_column_in_set",
                column=column,
                row_index=i,
                detail=f"Value {val} is not in allowed_valued set"
            ))
    return violations


def expect_column_unique(rows, column):
    """Return a Violation for every row AFTER THE FIRST that repeats a value
    already seen in `column`. (i.e. if three rows share a value, rows 2 and 3
    are violations; row 1 is not.)
    """
    # TODO: implement
    violations = []
    visited = set()

    for i, rows in enumerate(rows):
        val = rows.get(column)
        if val in visited:
            violations.append(Violation(
                expectation="expect_column_unique",
                column=column,
                row_index=i,
                detail=f"Value {val} is a duplicate"
            ))
        else:
            visited.add(val)
    return violations
