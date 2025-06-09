import random, copy
from chromosome import Chromosome
from data import SEMESTERS, NPERIODS

def tournament_selection(pop: list, fits: list, k=3) -> Chromosome:
    contenders = random.sample(list(zip(pop, fits)), k)
    return copy.deepcopy(min(contenders, key=lambda x: x[1])[0])

def crossover(p1: Chromosome, p2: Chromosome, teachers: list) -> tuple:
    child1, child2 = p1.copy(), p2.copy()
    sem = random.choice(SEMESTERS)
    per = random.choice(NPERIODS)
    for t in teachers:
        key = (sem, per, t.id)
        child1.assignments[key], child2.assignments[key] = (
            child2.assignments[key],
            child1.assignments[key]
        )
    return child1, child2

def mutate(chromo: Chromosome, teachers: list, rate=0.1):
    for key in list(chromo.assignments.keys()):
        sem, period, tid = key
        teacher = next(t for t in teachers if t.id == tid)

        # If the slot is outside their availability, always clear it
        if period not in teacher.availability[sem]:
            chromo.assignments[key] = None
            continue

        # Otherwise, only mutate with probability rate
        if random.random() < rate:
            choices = teacher.subjects + [None]
            chromo.assignments[key] = random.choice(choices)
