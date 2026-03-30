from dataclasses import dataclass, field

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """Represents a single pet care activity."""
    title: str
    duration_minutes: int
    priority: str        # "low", "medium", or "high"
    frequency: str       # "daily", "weekly", or "as-needed"
    completed: bool = field(default=False)

    def is_feasible(self, available_time: int) -> bool:
        """Return True if this task fits within the remaining time budget."""
        return self.duration_minutes <= available_time

    def mark_complete(self) -> None:
        """Mark this task as completed by setting completed to True."""
        self.completed = True


@dataclass
class Pet:
    """Stores pet details and owns a list of care tasks."""
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
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
