from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Setup: owner, pets, and tasks added OUT OF ORDER (by time) intentionally
# ---------------------------------------------------------------------------
owner = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog")
luna  = Pet(name="Luna",  species="cat")

# Mochi's tasks — times added out of chronological order
mochi.add_task(Task(title="Fetch training",  duration_minutes=20, priority="medium",
                    frequency="daily",      time="14:00", due_date="2026-03-30"))
mochi.add_task(Task(title="Morning walk",    duration_minutes=30, priority="high",
                    frequency="daily",      time="08:00", due_date="2026-03-30"))
mochi.add_task(Task(title="Vet appointment", duration_minutes=60, priority="high",
                    frequency="as-needed",  time="11:00"))

# Luna's tasks
luna.add_task(Task(title="Litter cleaning",  duration_minutes=10, priority="medium",
                   frequency="daily",       time="09:00", due_date="2026-03-30"))
luna.add_task(Task(title="Brushing",         duration_minutes=15, priority="low",
                   frequency="weekly",      time="08:00"))  # same time as Morning walk!

owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner=owner)

# ---------------------------------------------------------------------------
# 1. Priority-based schedule (original behaviour)
# ---------------------------------------------------------------------------
print("=" * 55)
print("PRIORITY-BASED SCHEDULE")
print("=" * 55)
schedule = scheduler.generate_schedule()
print(schedule.display())

# ---------------------------------------------------------------------------
# 2. Sort tasks by scheduled time
# ---------------------------------------------------------------------------
print("=" * 55)
print("ALL TASKS SORTED BY TIME")
print("=" * 55)
all_tasks = owner.get_all_tasks()
sorted_tasks = scheduler.sort_by_time(all_tasks)
for task in sorted_tasks:
    time_label = task.time if task.time else "--:--"
    print(f"  {time_label}  [{task.priority:<6}]  {task.title}  ({task.pet_name})")

# ---------------------------------------------------------------------------
# 3. Filter tasks
# ---------------------------------------------------------------------------
print()
print("=" * 55)
print("FILTER: Mochi's tasks only")
print("=" * 55)
mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
for t in mochi_tasks:
    print(f"  {t.title} — {t.duration_minutes} min")

print()
print("=" * 55)
print("FILTER: Pending (not yet completed) tasks")
print("=" * 55)
pending = scheduler.filter_tasks(completed=False)
for t in pending:
    print(f"  {t.title} ({t.pet_name})")

# ---------------------------------------------------------------------------
# 4. Conflict detection  (run before any state changes)
# ---------------------------------------------------------------------------
print()
print("=" * 55)
print("CONFLICT DETECTION")
print("=" * 55)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No scheduling conflicts found.")

# ---------------------------------------------------------------------------
# 5. Recurring tasks — mark complete and auto-generate next occurrence
# ---------------------------------------------------------------------------
print()
print("=" * 55)
print("RECURRING TASK: Mark 'Morning walk' complete")
print("=" * 55)
walk = mochi.tasks[1]  # Morning walk, due_date="2026-03-30", frequency="daily"
next_walk = walk.mark_complete()
print(f"  '{walk.title}' marked complete (due {walk.due_date})")
if next_walk:
    print(f"  Next occurrence auto-created: '{next_walk.title}' due {next_walk.due_date}")
    mochi.add_task(next_walk)

print()
print("FILTER: Completed tasks (after marking Morning walk done)")
done = scheduler.filter_tasks(completed=True)
for t in done:
    print(f"  {t.title} ({t.pet_name}) — completed={t.completed}")
