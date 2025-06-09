import random
from typing import List

# Constants
NPERIODS      = list(range(1, 8))  # Periods 1–7
SEMESTERS     = ['Fall', 'Spring']
CORE          = ['math', 'science', 'language_arts', 'social_studies']
AL_CORE       = ['AL_math', 'AL_science', 'AL_language_arts', 'AL_social_studies']
FULL_YEAR     = ['X', 'Y']         # full-year electives
PE            = ['PE']             # semester-only core
SEM_ELECTIVES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
MAX_CAPACITY  = 30

class Teacher:
    def __init__(self, id: str, subjects: list, availability: dict):
        self.id = id
        self.subjects = subjects       # list of subject codes
        self.availability = availability  # dict: semester -> set(periods)

class Student:
    def __init__(self, id: str, gender: str, track: str, requests: list, alternates: list):
        self.id = id
        self.gender = gender           # 'M' or 'F'
        self.track = track             # 'GenEd' or 'AL'
        self.requests = requests       # ranked elective requests
        self.alternates = alternates
        # Randomly choose which semester they take PE
        self.pe_semester = random.choice(SEMESTERS)
        # Will be filled by scheduler
        self.schedule = {sem: {} for sem in SEMESTERS}


def generate_mock_teachers(n=10) -> List[Teacher]:
    teachers = []
    all_subs = CORE + AL_CORE + FULL_YEAR + PE + SEM_ELECTIVES
    # pick 1 or 2 teachers to be PE specialists
    pe_count = random.choice([1, 2])
    pe_indices = set(random.sample(range(1, n+1), pe_count))
    for i in range(1, n+1):
        tid = f'T{i}'
        # availability: 6 of 7 periods each semester
        avail = {sem: set(random.sample(NPERIODS, 6)) for sem in SEMESTERS}
        if i in pe_indices:
            subs = ['PE']
        else:
            subs = random.sample([s for s in all_subs if s != 'PE'], random.randint(3, 5))
        teachers.append(Teacher(tid, subs, avail))
    return teachers


def generate_mock_students(n: int, teachers: List[Teacher]) -> List[Student]:
    """
    Create n students whose elective requests are drawn only from
    courses that at least one teacher can actually teach.
    """
    # 1) Determine which courses are offered by any teacher
    offered_full_year = set()
    offered_semester  = set()
    for t in teachers:
        for subj in t.subjects:
            if subj in FULL_YEAR or subj in PE:
                offered_full_year.add(subj)
            elif subj in SEM_ELECTIVES:
                offered_semester.add(subj)

    # 2) Generate students
    students = []
    for i in range(1, n+1):
        sid    = f'S{i}'
        gender = random.choice(['M', 'F'])
        track  = random.choice(['GenEd', 'AL'])
        r      = random.random()

        fy_pool  = list(offered_full_year)
        sem_pool = list(offered_semester)

        # decide mix of full-/semester electives
        if r < 0.33 and len(fy_pool) >= 2 and len(sem_pool) >= 1:
            req = random.sample(fy_pool, 2) + random.sample(sem_pool, 1)
        elif r < 0.66 and len(fy_pool) >= 1 and len(sem_pool) >= 3:
            req = random.sample(fy_pool, 1) + random.sample(sem_pool, 3)
        elif len(sem_pool) >= 5:
            req = random.sample(sem_pool, 5)
        else:
            # fallback: whatever is available
            req = random.sample(fy_pool, min(2, len(fy_pool))) \
                + random.sample(sem_pool, min(3, len(sem_pool)))

        # alternates from remaining semester electives
        remaining = [e for e in sem_pool if e not in req]
        alt_count = min(4, len(remaining))
        alternates = random.sample(remaining, alt_count) if alt_count > 0 else []

        students.append(Student(sid, gender, track, req, alternates))

    return students
