from dataclasses import dataclass, field
from datetime import date, timedelta

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """Represents a single pet care activity."""
    title: str
    duration_minutes: int
    priority: str        # "low", "medium", or "high"
    frequency: str       # "daily", "weekly", or "as-needed"
    time: str = ""       # "HH:MM" scheduled start time; "" means unscheduled
    due_date: str = ""   # "YYYY-MM-DD" used to compute next occurrence for recurring tasks
    pet_name: str = ""   # auto-stamped by Pet.add_task(); used for filtering and conflict display
    completed: bool = field(default=False)

    def is_feasible(self, available_time: int) -> bool:
        """Return True if this task fits within the remaining time budget.

        Args:
            available_time: Remaining minutes in the owner's daily budget.

        Returns:
            True if duration_minutes <= available_time, False otherwise.
        """
        return self.duration_minutes <= available_time

    def mark_complete(self) -> "Task | None":
        """Mark this task as completed and auto-generate the next occurrence for recurring tasks.

        Sets completed to True. For "daily" or "weekly" tasks, creates and returns a new
        Task with the same attributes but completed=False and a due_date advanced by 1 or
        7 days respectively. For "as-needed" tasks, returns None.

        Returns:
            A new Task for the next occurrence, or None if this task does not recur.
        """
        self.completed = True
        if self.frequency in ("daily", "weekly"):
            base = date.fromisoformat(self.due_date) if self.due_date else date.today()
            delta = timedelta(days=1 if self.frequency == "daily" else 7)
            return Task(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                time=self.time,
                due_date=(base + delta).isoformat(),
                pet_name=self.pet_name,
            )
        return None


@dataclass
class Pet:
    """Stores pet details and owns a list of care tasks."""
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list and stamp the task's pet_name.

        Args:
            task: The Task to add. Its pet_name attribute will be set to this pet's name.
        """
        task.pet_name = self.name
        self.tasks.append(task)


class Owner:
    """Manages one or more pets and provides access to all their tasks."""

    def __init__(self, name: str, available_minutes: int) -> None:
        """Initialize an owner with a name and daily time budget in minutes."""
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return a flat list of all tasks across every pet the owner has."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Schedule:
    """The output object produced by the Scheduler."""

    def __init__(self, owner: Owner, scheduled_tasks: list[Task], explanations: list[str]) -> None:
        """Store the owner, the ordered list of chosen tasks, and their explanations."""
        self.owner = owner
        self.scheduled_tasks = scheduled_tasks
        self.explanations = explanations

    @property
    def total_duration(self) -> int:
        """Compute total scheduled time — always in sync with scheduled_tasks."""
        return sum(t.duration_minutes for t in self.scheduled_tasks)

    def display(self) -> str:
        """Return a formatted multi-line string showing the full schedule."""
        lines = []
        lines.append(f"=== Today's Schedule for {self.owner.name} ===")
        lines.append("")
        pet_names = ", ".join(p.name for p in self.owner.pets)
        lines.append(f"Pets: {pet_names}")
        lines.append(
            f"Time budget: {self.owner.available_minutes} min  |  "
            f"Time used: {self.total_duration} min"
        )
        lines.append("")
        lines.append("TASKS:")
        if self.scheduled_tasks:
            for i, task in enumerate(self.scheduled_tasks, start=1):
                tag = f"[{task.priority.upper()}]"
                lines.append(f"  {i}. {tag:<8} {task.title:<26} — {task.duration_minutes} min")
        else:
            lines.append("  (no tasks fit within the available time)")
        lines.append("")
        lines.append("NOTES:")
        for note in self.explanations:
            lines.append(f"  - {note}")
        lines.append("")
        lines.append(
            f"Total: {self.total_duration} min scheduled out of "
            f"{self.owner.available_minutes} min available."
        )
        return "\n".join(lines)


class Scheduler:
    """The brain — retrieves tasks from the owner's pets and builds a daily plan."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the scheduler with an owner whose pets supply the tasks."""
        self.owner = owner

    def generate_schedule(self) -> Schedule:
        """Select and order feasible tasks by priority; return a Schedule with explanations."""
        all_tasks = self.owner.get_all_tasks()
        pending = [t for t in all_tasks if not t.completed]
        sorted_tasks = sorted(pending, key=lambda t: PRIORITY_ORDER[t.priority.lower()])

        scheduled: list[Task] = []
        explanations: list[str] = []
        remaining = self.owner.available_minutes

        for task in sorted_tasks:
            if task.is_feasible(remaining):
                scheduled.append(task)
                remaining -= task.duration_minutes
                explanations.append(
                    f"Included '{task.title}' ({task.duration_minutes} min, "
                    f"{task.priority} priority) — {remaining} min remaining."
                )
            else:
                explanations.append(
                    f"Skipped '{task.title}' ({task.duration_minutes} min) "
                    f"— only {remaining} min left."
                )

        return Schedule(self.owner, scheduled, explanations)

    def sort_by_time(self, tasks: list) -> list:
        """Sort a list of tasks chronologically by their scheduled time.

        Tasks without a time value (empty string) sort after all timed tasks.

        Args:
            tasks: List of Task objects to sort.

        Returns:
            A new list sorted by time in ascending "HH:MM" order.
        """
        return sorted(tasks, key=lambda t: t.time if t.time else "99:99")

    def filter_tasks(self, pet_name: str = None, completed: bool = None) -> list:
        """Filter the owner's tasks by pet name and/or completion status.

        Both parameters are optional; omitting one means that dimension is not filtered.

        Args:
            pet_name: If provided, only return tasks belonging to this pet.
            completed: If True, return only completed tasks. If False, only pending tasks.

        Returns:
            A list of Task objects matching all supplied filters.
        """
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self) -> list:
        """Detect tasks scheduled at the exact same time and return warning messages.

        Only tasks with a non-empty time attribute are considered. The check uses exact
        "HH:MM" string matching; overlapping durations are not detected (see reflection.md
        section 2b for the tradeoff rationale).

        Returns:
            A list of human-readable warning strings, one per conflicting pair.
            Returns an empty list if no conflicts exist.
        """
        timed = [t for t in self.owner.get_all_tasks() if t.time]
        warnings = []
        seen: dict[str, Task] = {}
        for task in timed:
            if task.time in seen:
                other = seen[task.time]
                warnings.append(
                    f"Conflict at {task.time}: '{task.title}' ({task.pet_name}) "
                    f"clashes with '{other.title}' ({other.pet_name})"
                )
            else:
                seen[task.time] = task
        return warnings
