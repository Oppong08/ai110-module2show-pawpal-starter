from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"

    def is_feasible(self, available_time: int) -> bool:
        """Return True if this task fits within the remaining time budget."""
        pass


class Owner:
    def __init__(self, name: str, pet: Pet, available_minutes: int):
        self.name = name
        self.pet = pet
        self.available_minutes = available_minutes


class Schedule:
    def __init__(self, scheduled_tasks: list[Task], total_duration: int, explanations: list[str]):
        self.scheduled_tasks = scheduled_tasks
        self.total_duration = total_duration
        self.explanations = explanations

    def display(self) -> str:
        """Format the schedule and explanations for display in the UI."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, tasks: list[Task]):
        self.owner = owner
        self.tasks = tasks

    def generate_schedule(self) -> Schedule:
        """Select and order feasible tasks by priority within the owner's available time."""
        pass

    def explain_schedule(self) -> list[str]:
        """Return a human-readable explanation for why each task was included."""
        pass
