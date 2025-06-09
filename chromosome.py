import random, copy, math
from data import (
    NPERIODS, SEMESTERS,
    CORE, AL_CORE, FULL_YEAR,
    PE, MAX_CAPACITY
)

class Chromosome:
    """
    Represents a complete teacher-period assignment:
     key = (semester, period, teacher_id) -> subject or None
    """
    def __init__(self, teachers: list):
        self.assignments = {}
        for sem in SEMESTERS:
            for p in NPERIODS:
                for t in teachers:
                    self.assignments[(sem, p, t.id)] = None

    def copy(self):
        new = Chromosome([])
        new.assignments = copy.deepcopy(self.assignments)
        return new


def create_random_chromosome(teachers: list, students: list):
    """
    Build a chromosome that:
      1) Offers each CORE and AL_CORE subject enough times each semester to cover all students.
      2) Offers FULL_YEAR electives once per semester.
      3) Ensures each teacher has exactly 5 teaching slots.
      4) Distributes classes evenly across periods.
    """
    chromo = Chromosome(teachers)
    period_usage = {(sem, p): 0 for sem in SEMESTERS for p in NPERIODS}

    # Compute per-semester demand
    demand = {(sem, subj): 0 for sem in SEMESTERS for subj in CORE + AL_CORE}
    for st in students:
        cores = CORE if st.track == 'GenEd' else AL_CORE
        for sem in SEMESTERS:
            for subj in cores:
                demand[(sem, subj)] += 1

    # Compute sections needed per (semester, subject)
    sections_needed = {key: math.ceil(cnt / MAX_CAPACITY)
                       for key, cnt in demand.items()}

    # Assign mandatory cores
    for (sem, subj), needed in sections_needed.items():
        for _ in range(needed):
            qualified = [t for t in teachers if subj in t.subjects]
            if not qualified:
                continue
            best, best_free = None, -1
            for t in qualified:
                free = [p for p in t.availability[sem]
                        if chromo.assignments[(sem, p, t.id)] is None]
                if len(free) > best_free:
                    best_free, best = len(free), t
            if best_free <= 0:
                continue
            free_ps = [p for p in best.availability[sem]
                       if chromo.assignments[(sem, p, best.id)] is None]
            p = min(free_ps, key=lambda x: period_usage[(sem, x)])
            chromo.assignments[(sem, p, best.id)] = subj
            period_usage[(sem, p)] += 1

    # Assign full-year electives
    for sem in SEMESTERS:
        for subj in FULL_YEAR:
            qualified = [t for t in teachers if subj in t.subjects]
            if not qualified:
                continue
            t = random.choice(qualified)
            free = [p for p in t.availability[sem]
                    if chromo.assignments[(sem, p, t.id)] is None]
            if not free:
                continue
            p = min(free, key=lambda x: period_usage[(sem, x)])
            chromo.assignments[(sem, p, t.id)] = subj
            period_usage[(sem, p)] += 1

    # Fill to 5 classes per teacher
    for t in teachers:
        for sem in SEMESTERS:
            assigned = [p for p in NPERIODS
                        if chromo.assignments[(sem, p, t.id)] is not None]
            needed = 5 - len(assigned)
            if needed > 0:
                free = [p for p in t.availability[sem]
                        if chromo.assignments[(sem, p, t.id)] is None]
                free_sorted = sorted(free, key=lambda x: period_usage[(sem, x)])
                for p in free_sorted[:needed]:
                    subj = 'PE' if 'PE' in t.subjects else random.choice(t.subjects)
                    chromo.assignments[(sem, p, t.id)] = subj
                    period_usage[(sem, p)] += 1
            elif needed < 0:
                drop = random.sample(assigned, -needed)
                for p in drop:
                    chromo.assignments[(sem, p, t.id)] = None
                    period_usage[(sem, p)] = max(0, period_usage[(sem, p)] - 1)

    return chromo
