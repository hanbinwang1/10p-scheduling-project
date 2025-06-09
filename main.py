from data      import generate_mock_teachers, generate_mock_students
from scheduler import run_scheduler, export_csv

if __name__ == '__main__':
    print("Generating data...")
    teachers = generate_mock_teachers(20)
    students = generate_mock_students(250, teachers)

    print("Running scheduler...")
    best_schedule = run_scheduler(
        teachers, students,
        generations=20,
        pop_size=100,
        elite=10
    )

    print("Exporting CSV files...")
    export_csv(teachers, students, best_schedule)
    print("Done: teachers.csv and students.csv created.")