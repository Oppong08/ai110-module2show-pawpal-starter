from pawpal_system import Owner, Pet, Task, Scheduler

# 1. Create owner with a 90-minute daily time budget
owner = Owner(name="Jordan", available_minutes=90)

# 2. Create two pets
mochi = Pet(name="Mochi", species="dog")
luna  = Pet(name="Luna",  species="cat")

# 3. Add tasks to each pet (mixed priorities; vet visit will be skipped by time)
mochi.add_task(Task(title="Morning walk",    duration_minutes=30, priority="high",   frequency="daily"))
mochi.add_task(Task(title="Fetch training",  duration_minutes=20, priority="medium", frequency="daily"))
mochi.add_task(Task(title="Vet appointment", duration_minutes=60, priority="high",   frequency="as-needed"))

luna.add_task(Task(title="Litter cleaning",  duration_minutes=10, priority="medium", frequency="daily"))
luna.add_task(Task(title="Brushing",         duration_minutes=15, priority="low",    frequency="weekly"))

# 4. Register pets with the owner
owner.add_pet(mochi)
owner.add_pet(luna)

# 5. Run the scheduler and print the plan
scheduler = Scheduler(owner=owner)
schedule  = scheduler.generate_schedule()
print(schedule.display())
