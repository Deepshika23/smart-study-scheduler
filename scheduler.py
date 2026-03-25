"""Smart scheduling utilities for ordering study tasks."""

from datetime import datetime


PRIORITY_ORDER = {
    "High": 0,
    "Medium": 1,
    "Low": 2,
}


def optimize_schedule(tasks):
    """
    Sort tasks by priority and then nearest deadline.

    Rules:
    1. High priority before Medium before Low.
    2. Within same priority, earlier deadlines first.

    Args:
        tasks (list): List of Task objects.

    Returns:
        list: Sorted list of Task objects in optimized order.
    """

    def sort_key(task):
        priority_rank = PRIORITY_ORDER.get(task.priority, 99)
        deadline_value = task.deadline or datetime.max
        return (priority_rank, deadline_value)

    return sorted(tasks, key=sort_key)
