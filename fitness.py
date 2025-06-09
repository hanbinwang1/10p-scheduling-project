import random
from data import (
    NPERIODS, SEMESTERS,
    CORE, AL_CORE, FULL_YEAR, PE, MAX_CAPACITY
)
from chromosome import Chromosome

def evaluate_fitness(chromo: Chromosome, teachers: list, students: list) -> float:
    # Total fitness and per‐category counters
    fitness = 0.0
    penalties = {
        'load': 0,
        'availability': 0,
        'coverage': 0,
        'student_core': 0,
        'student_pe': 0,
        'gender_balance': 0
    }

    # 1) Teacher load & availability
    for t in teachers:
        for sem in SEMESTERS:
            assigned = [chromo.assignments[(sem, p, t.id)] for p in NPERIODS]
            teach_count = sum(1 for c in assigned if c is not None)
            delta = abs(teach_count - 5)
            penalties['load'] += delta * 20
            for p, c in zip(NPERIODS, assigned):
                if c is not None and p not in t.availability[sem]:
                    penalties['availability'] += 50

    # 2) Required offerings coverage
    for subj in CORE + AL_CORE + FULL_YEAR + ['PE']:
        for sem in SEMESTERS:
            if not any(
                c == subj
                for (s, p, tid), c in chromo.assignments.items()
                if s == sem
            ):
                penalties['coverage'] += 100

    # 3) Student assignment & rosters
    rosters = {}
    for st in students:
        # Reset schedule
        st.schedule = {sem: {} for sem in SEMESTERS}

        for sem in SEMESTERS:
            # a) Assign GenEd or AL cores
            cores = CORE if st.track == 'GenEd' else AL_CORE
            for core in cores:
                placed = False
                options = [
                    (s2, p2, tid2) for (s2, p2, tid2), c in chromo.assignments.items()
                    if s2 == sem and c == core
                ]
                random.shuffle(options)
                for _, p2, _ in options:
                    key = (sem, p2, core)
                    if p2 not in st.schedule[sem] and len(rosters.get(key, [])) < MAX_CAPACITY:
                        rosters.setdefault(key, []).append(st.gender)
                        st.schedule[sem][p2] = core
                        placed = True
                        break
                if not placed:
                    penalties['student_core'] += 50

            # b) Assign exactly one PE in the chosen semester
            if sem == st.pe_semester and 'PE' not in st.schedule[sem].values():
                placed = False
                options = [
                    (s2, p2, tid2) for (s2, p2, tid2), c in chromo.assignments.items()
                    if s2 == sem and c == 'PE'
                ]
                random.shuffle(options)
                for _, p2, _ in options:
                    key = (sem, p2, 'PE')
                    if p2 not in st.schedule[sem] and len(rosters.get(key, [])) < MAX_CAPACITY:
                        rosters.setdefault(key, []).append(st.gender)
                        st.schedule[sem][p2] = 'PE'
                        placed = True
                        break
                if not placed:
                    penalties['student_pe'] += 50

            # c) Electives and filler (EL now zero‐penalty)
            free_periods = [p for p in NPERIODS if p not in st.schedule[sem]]
            prefs = st.requests + st.alternates
            for p in free_periods:
                assigned = False
                for choice in prefs:
                    for (s2, p2, tid2), c in chromo.assignments.items():
                        if s2 == sem and p2 == p and c == choice:
                            key = (sem, p, choice)
                            if len(rosters.get(key, [])) < MAX_CAPACITY:
                                rosters.setdefault(key, []).append(st.gender)
                                st.schedule[sem][p] = choice
                                assigned = True
                                break
                    if assigned:
                        break
                if not assigned:
                    st.schedule[sem][p] = 'EL'   # no penalty for filler

    # 4) Gender‐balance penalty
    for roster_list in rosters.values():
        m = roster_list.count('M')
        f = roster_list.count('F')
        diff = abs(m - f)
        if diff > 1:
            penalties['gender_balance'] += (diff - 1) * 10

    # Sum and report
    fitness = sum(penalties.values())
    print("Fitness breakdown:", penalties, "→ total", fitness)
    return fitness
