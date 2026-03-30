import streamlit as st
from datetime import date, time as time_type
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------- session state bootstrap ----------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "last_schedule" not in st.session_state:
    st.session_state.last_schedule = None

# ============================================================
# Section 1 — Owner Setup
# ============================================================
st.header("1. Owner Setup")

with st.form("owner_form"):
    owner_name        = st.text_input("Owner name", placeholder="e.g. Jordan")
    available_minutes = st.number_input(
        "Available minutes today", min_value=1, max_value=1440, value=60
    )
    submitted = st.form_submit_button("Save owner profile")

if submitted:
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    st.session_state.last_schedule = None  # clear stale schedule on owner reset
    st.success(f"Profile saved for {owner_name} ({available_minutes} min available)!")

st.divider()

# ============================================================
# Section 2 — Add a Pet
# ============================================================
st.header("2. Add a Pet")

if st.session_state.owner is None:
    st.info("Set up your owner profile first (Section 1).")
else:
    owner = st.session_state.owner

    pet_name = st.text_input("Pet name", placeholder="e.g. Mochi", key="pet_name_input")
    species  = st.selectbox("Species", ["dog", "cat", "other"], key="species_input")

    if st.button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"{pet_name.strip()} added!")
        else:
            st.warning("Please enter a pet name.")

    if owner.pets:
        st.markdown("**Current pets:**")
        for pet in owner.pets:
            st.write(f"- {pet.name} ({pet.species}) — {len(pet.tasks)} task(s)")
    else:
        st.info("No pets yet. Add one above.")

st.divider()

# ============================================================
# Section 3 — Add a Task
# ============================================================
st.header("3. Add a Task")

if st.session_state.owner is None:
    st.info("Set up your owner profile first (Section 1).")
elif not st.session_state.owner.pets:
    st.info("Add at least one pet first (Section 2).")
else:
    owner = st.session_state.owner

    pet_options   = {pet.name: pet for pet in owner.pets}
    selected_name = st.selectbox("Assign task to pet", list(pet_options.keys()), key="task_pet_select")
    selected_pet  = pet_options[selected_name]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
    with col2:
        duration   = st.number_input("Duration (min)", min_value=1, max_value=240, value=20, key="task_duration_input")
    with col3:
        priority   = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="task_priority_input")
    with col4:
        frequency  = st.selectbox("Frequency", ["daily", "weekly", "as-needed"], key="task_freq_input")

    col5, col6 = st.columns(2)
    with col5:
        use_time  = st.checkbox("Set a scheduled time", key="use_time_check")
        task_time = st.time_input("Scheduled time", value=time_type(8, 0), key="task_time_input") if use_time else None
    with col6:
        task_date = st.date_input("Due date", value=date.today(), key="task_date_input")

    if st.button("Add task"):
        if task_title.strip():
            selected_pet.add_task(
                Task(
                    title=task_title.strip(),
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                    time=task_time.strftime("%H:%M") if task_time else "",
                    due_date=task_date.isoformat(),
                )
            )
            st.success(f"Task '{task_title.strip()}' added to {selected_pet.name}!")
        else:
            st.warning("Please enter a task title.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.markdown("**All current tasks (sorted by scheduled time):**")
        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.sort_by_time(all_tasks)
        st.table([
            {
                "Time":      t.time or "—",
                "Pet":       t.pet_name,
                "Title":     t.title,
                "Duration":  f"{t.duration_minutes} min",
                "Priority":  t.priority,
                "Frequency": t.frequency,
                "Done":      "✓" if t.completed else "",
            }
            for t in sorted_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ============================================================
# Section 4 — Generate Schedule
# ============================================================
st.header("4. Generate Schedule")

if st.session_state.owner is None:
    st.info("Set up your owner profile first (Section 1).")
else:
    owner = st.session_state.owner
    scheduler = Scheduler(owner)

    # Show conflict warnings whenever tasks exist
    if owner.get_all_tasks():
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(f"⚠️ {warning}")
        else:
            st.success("No scheduling conflicts detected!")

    if st.button("Generate schedule"):
        if not owner.get_all_tasks():
            st.warning("Add at least one task before generating a schedule.")
        else:
            schedule = scheduler.generate_schedule()
            st.session_state.last_schedule = schedule

    if st.session_state.last_schedule is not None:
        schedule = st.session_state.last_schedule

        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Time available", f"{owner.available_minutes} min")
        with col_b:
            st.metric("Time scheduled", f"{schedule.total_duration} min",
                      delta=f"{schedule.total_duration - owner.available_minutes} min")

        if schedule.scheduled_tasks:
            st.markdown("**Scheduled tasks:**")
            st.table([
                {
                    "Title":    t.title,
                    "Pet":      t.pet_name,
                    "Priority": t.priority.capitalize(),
                    "Duration": f"{t.duration_minutes} min",
                    "Time":     t.time or "—",
                }
                for t in schedule.scheduled_tasks
            ])
        else:
            st.warning("No tasks fit within your available time budget.")

        with st.expander("Scheduling notes"):
            for note in schedule.explanations:
                st.write(f"- {note}")

st.divider()

# ============================================================
# Section 5 — Mark a Task Complete
# ============================================================
st.header("5. Mark a Task Complete")

if st.session_state.owner is None:
    st.info("Set up your owner profile first (Section 1).")
else:
    owner = st.session_state.owner
    scheduler = Scheduler(owner)
    pending_tasks = scheduler.filter_tasks(completed=False)

    if not pending_tasks:
        st.info("No pending tasks — all done!")
    else:
        task_labels    = [f"{t.title} ({t.pet_name})" for t in pending_tasks]
        selected_label = st.selectbox("Select task to mark complete", task_labels, key="complete_select")
        selected_idx   = task_labels.index(selected_label)
        selected_task  = pending_tasks[selected_idx]

        if st.button("Mark complete"):
            next_task = selected_task.mark_complete()
            if next_task:
                pet_map = {pet.name: pet for pet in owner.pets}
                pet_map[next_task.pet_name].add_task(next_task)
                st.success(
                    f"'{selected_task.title}' marked complete! "
                    f"Next occurrence auto-created for {next_task.due_date}."
                )
            else:
                st.success(f"'{selected_task.title}' marked complete!")
            st.session_state.last_schedule = None
            st.rerun()
