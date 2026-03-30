from pawpal_system import Task, Pet


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
