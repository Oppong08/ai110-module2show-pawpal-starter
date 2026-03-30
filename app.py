import streamlit as st
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

    if st.button("Add task"):
        if task_title.strip():
            selected_pet.add_task(
                Task(
                    title=task_title.strip(),
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                )
            )
            st.success(f"Task '{task_title.strip()}' added to {selected_pet.name}!")
        else:
            st.warning("Please enter a task title.")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.markdown("**All current tasks:**")
        st.table([
            {
                "Title":     t.title,
                "Duration":  t.duration_minutes,
                "Priority":  t.priority,
                "Frequency": t.frequency,
            }
            for t in all_tasks
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

    if st.button("Generate schedule"):
        if not owner.get_all_tasks():
            st.warning("Add at least one task before generating a schedule.")
        else:
            schedule = Scheduler(owner).generate_schedule()
            st.session_state.last_schedule = schedule

    if st.session_state.last_schedule is not None:
        schedule = st.session_state.last_schedule
        st.markdown(
            f"**Total time scheduled:** {schedule.total_duration} min "
            f"out of {owner.available_minutes} min available"
        )
        st.text(schedule.display())
