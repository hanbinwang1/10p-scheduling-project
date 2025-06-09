import csv, random
from chromosome import create_random_chromosome, Chromosome
from fitness    import evaluate_fitness
from operators  import tournament_selection, crossover, mutate
from data       import NPERIODS, SEMESTERS

def run_scheduler(
    teachers: list,
    students: list,
    generations=100,
    pop_size=50,
    elite=5,
    mutation_rate=0.2,
    immigrant_rate=0.1
) -> Chromosome:
    """
    Genetic Algorithm with elitism, diversity maintenance via random immigrants,
    and adjustable mutation rate.
    """
    # initialize population
    population = [
        create_random_chromosome(teachers, students)
        for _ in range(pop_size)
    ]
    best_fit = float('inf')
    best = None
    stagnant = 0

    for gen in range(1, generations+1):
        # reset student schedules
        for st in students:
            st.schedule = {sem: {} for sem in SEMESTERS}

        # evaluate fitness
        fits = [evaluate_fitness(c, teachers, students) for c in population]
        idx = min(range(len(fits)), key=lambda i: fits[i])
        curr_fit = fits[idx]

        # update best
        if curr_fit < best_fit:
            best_fit = curr_fit
            best = population[idx].copy()
            stagnant = 0
        else:
            stagnant += 1

        avg_fit = sum(fits) / len(fits)
        print(f"Gen {gen}: best={best_fit}, avg={avg_fit:.1f}, stagnation={stagnant}")

        # early stopping
        if best_fit <= 0 or stagnant >= 10:
            print("Stopping early due to convergence.")
            break

        # create next generation
        # 1) elitism
        sorted_pop = [c for _, c in sorted(zip(fits, population), key=lambda x: x[0])]
        next_pop = sorted_pop[:elite]

        # 2) offspring via crossover & mutation
        target_offspring = int((1 - immigrant_rate) * pop_size) - elite
        while len(next_pop) < elite + target_offspring:
            p1 = tournament_selection(population, fits)
            p2 = tournament_selection(population, fits)
            c1, c2 = crossover(p1, p2, teachers)
            mutate(c1, teachers, rate=mutation_rate)
            mutate(c2, teachers, rate=mutation_rate)
            next_pop.extend([c1, c2])

        # 3) random immigrants for diversity
        while len(next_pop) < pop_size:
            next_pop.append(create_random_chromosome(teachers, students))

        population = next_pop[:pop_size]

    print(f"GA finished at generation {gen}, best fitness = {best_fit}")
    return best


def export_csv(teachers: list, students: list, schedule: Chromosome):
    # Teachers schedule export
    with open('teachers.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Teacher','Semester'] + [f'P{p}' for p in NPERIODS])
        for t in teachers:
            for sem in SEMESTERS:
                row = [t.id, sem] + [
                    schedule.assignments[(sem, p, t.id)] or 'BREAK'
                    for p in NPERIODS
                ]
                w.writerow(row)

    # Students schedule export
    with open('students.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Student','Gender','Semester'] + [f'P{p}' for p in NPERIODS])
        for s in students:
            for sem in SEMESTERS:
                row = [s.id, s.gender, sem] + [
                    s.schedule[sem].get(p, 'EL') for p in NPERIODS
                ]
                w.writerow(row)
