# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Features

- **Multi-pet support** — manage tasks for any number of pets in one session
- **Priority-driven scheduling** — high-priority tasks are always evaluated first within the time budget; every include/skip decision comes with a plain-English explanation
- **Time-sorted task view** — all tasks displayed in chronological order by scheduled start time (`HH:MM`); tasks with no time assigned sort to the end
- **Conflict detection** — instant `st.warning` banners when two tasks share the exact same time slot, so scheduling problems are visible before generating the plan
- **Recurring task automation** — daily and weekly tasks auto-generate their next occurrence when marked complete, using Python's `timedelta` for accurate date arithmetic
- **Completion filtering** — the Mark Complete section shows only pending tasks; the task table marks finished ones with ✓

## 📸 Demo

<a href="Pawpal final.png" target="_blank"><img src='Pawpal final.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

## Smarter Scheduling

Phase 3 adds four algorithmic features that make the scheduler more intelligent:

- **`Scheduler.sort_by_time(tasks)`** — Returns tasks sorted chronologically by their `time` attribute (`"HH:MM"`). Tasks with no time assigned sort to the end. Powered by Python's `sorted()` with a lambda key.

- **`Scheduler.filter_tasks(pet_name, completed)`** — Filters the owner's full task list by pet name, completion status, or both. Useful for showing only a single pet's tasks or only pending work.

- **Recurring task automation** — `Task.mark_complete()` now returns a new `Task` for the next occurrence when `frequency` is `"daily"` (tomorrow) or `"weekly"` (7 days later). The caller adds this task back to the pet's list. Uses Python's `datetime.timedelta` for accurate date arithmetic.

- **`Scheduler.detect_conflicts()`** — Checks all timed tasks for exact `"HH:MM"` collisions. Returns a list of human-readable warning strings (one per conflicting pair) instead of raising an exception, so the app never crashes on a scheduling conflict.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
