from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_sets_completed_true():
    """mark_complete() should change completed from False to True."""
    task = Task(title="Morning walk", duration_minutes=30, priority="high", frequency="daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """add_task() should append the task and increase len(pet.tasks) by 1."""
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Evening walk", duration_minutes=20, priority="medium", frequency="daily"))
    assert len(pet.tasks) == 1


def test_add_task_stamps_pet_name():
    """add_task() should set the task's pet_name to the pet's name."""
    pet = Pet(name="Luna", species="cat")
    task = Task(title="Brushing", duration_minutes=15, priority="low", frequency="weekly")
    pet.add_task(task)
    assert task.pet_name == "Luna"


def test_mark_complete_daily_returns_next_task():
    """mark_complete() on a daily task should return a new Task due one day later."""
    task = Task(
        title="Morning walk",
        duration_minutes=30,
        priority="high",
        frequency="daily",
        due_date="2026-03-30",
    )
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == "2026-03-31"
    assert next_task.completed is False
    assert next_task.title == "Morning walk"


def test_mark_complete_weekly_returns_next_task():
    """mark_complete() on a weekly task should return a new Task due seven days later."""
    task = Task(
        title="Grooming",
        duration_minutes=20,
        priority="medium",
        frequency="weekly",
        due_date="2026-03-30",
    )
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == "2026-04-06"


def test_mark_complete_as_needed_returns_none():
    """mark_complete() on an as-needed task should return None (no recurrence)."""
    task = Task(title="Vet visit", duration_minutes=60, priority="high", frequency="as-needed")
    result = task.mark_complete()
    assert result is None


def test_sort_by_time_orders_chronologically():
    """sort_by_time() should return tasks in ascending HH:MM order."""
    owner = Owner(name="Alex", available_minutes=120)
    pet = Pet(name="Buddy", species="dog")
    t1 = Task(title="Lunch", duration_minutes=15, priority="low", frequency="daily", time="12:00")
    t2 = Task(title="Walk",  duration_minutes=30, priority="high", frequency="daily", time="08:00")
    t3 = Task(title="Meds",  duration_minutes=5,  priority="high", frequency="daily", time="10:30")
    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(owner.get_all_tasks())
    times = [t.time for t in sorted_tasks]
    assert times == ["08:00", "10:30", "12:00"]


def test_sort_by_time_untimed_tasks_sort_last():
    """Tasks with no time should appear after all timed tasks."""
    owner = Owner(name="Alex", available_minutes=60)
    pet = Pet(name="Buddy", species="dog")
    timed   = Task(title="Walk",   duration_minutes=20, priority="high",   frequency="daily", time="09:00")
    untimed = Task(title="Cuddle", duration_minutes=10, priority="medium", frequency="daily", time="")
    pet.add_task(untimed)
    pet.add_task(timed)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(owner.get_all_tasks())
    assert sorted_tasks[0].title == "Walk"
    assert sorted_tasks[1].title == "Cuddle"


def test_filter_tasks_by_pet_name():
    """filter_tasks(pet_name=...) should return only tasks for that pet."""
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    mochi.add_task(Task(title="Walk",    duration_minutes=30, priority="high",   frequency="daily"))
    luna.add_task( Task(title="Litter",  duration_minutes=10, priority="medium", frequency="daily"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    assert all(t.pet_name == "Mochi" for t in mochi_tasks)
    assert len(mochi_tasks) == 1
    assert mochi_tasks[0].title == "Walk"


def test_filter_tasks_by_completed_status():
    """filter_tasks(completed=True/False) should return tasks matching that status."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    t1 = Task(title="Walk",   duration_minutes=30, priority="high",   frequency="daily")
    t2 = Task(title="Litter", duration_minutes=10, priority="medium", frequency="daily")
    pet.add_task(t1)
    pet.add_task(t2)
    owner.add_pet(pet)
    t1.mark_complete()

    scheduler = Scheduler(owner)
    done    = scheduler.filter_tasks(completed=True)
    pending = scheduler.filter_tasks(completed=False)
    assert len(done) == 1 and done[0].title == "Walk"
    assert len(pending) == 1 and pending[0].title == "Litter"


def test_detect_conflicts_finds_same_time_tasks():
    """detect_conflicts() should return a warning when two tasks share an exact time."""
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = Pet(name="Mochi", species="dog")
    luna  = Pet(name="Luna",  species="cat")
    mochi.add_task(Task(title="Walk",     duration_minutes=30, priority="high",   frequency="daily",  time="09:00"))
    luna.add_task( Task(title="Grooming", duration_minutes=20, priority="medium", frequency="weekly", time="09:00"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "09:00" in warnings[0]


def test_detect_conflicts_no_conflict():
    """detect_conflicts() should return an empty list when all times are distinct."""
    owner = Owner(name="Jordan", available_minutes=120)
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(Task(title="Walk", duration_minutes=30, priority="high",   frequency="daily", time="08:00"))
    pet.add_task(Task(title="Meds", duration_minutes=5,  priority="high",   frequency="daily", time="12:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []
