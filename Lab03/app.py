"""Оболонка побічних ефектів для демонстрації роботи незмінної моделі (Варіант 3)."""

from __future__ import annotations

from core import (
    add_course_result,
    add_skill,
    calculate_average,
    calculate_weighted_gpa,
    recalculate_average_in_profile,
    top_courses,
)
from model import CourseResult, Student, make_profile


def build_initial_student() -> Student:
    """Створює початковий незмінний запис студента."""
    initial_results = (
        CourseResult(course="Алгоритми та структури даних", credits=5, grade=88.0),
        CourseResult(course="Бази даних", credits=4, grade=92.0),
        CourseResult(course="Операційні системи", credits=4, grade=85.0),
    )
    student = Student(
        student_id=2103,
        full_name="Букшований Максим",
        results=initial_results,
        skills=frozenset({"Python", "Arch Linux", "SQL"}),
        profile=make_profile(group="ФЕП-21с", specialty="121 Інженерія ПЗ"),
    )
    return recalculate_average_in_profile(student)


def render_student_card(title: str, student: Student) -> None:
    """Побічний ефект: друкує стан незмінного об'єкта студента у консоль."""
    print(f"=== {title} (id об'єкта в пам'яті: {id(student)}) ===")
    print(
        f"Студент: [{student.student_id}] {student.full_name} | "
        f"Група: {student.profile.get('group', '-')}"
    )
    print(f"Навички (frozenset): {', '.join(sorted(student.skills))}")
    for res in student.results:
        print(f"  - {res.course} ({res.credits} кред.): {res.grade:.1f}")
    print(
        f"Середній бал: {calculate_average(student.results):.2f} | "
        f"Зважений GPA: {calculate_weighted_gpa(student.results):.2f}"
    )
    print("-" * 72)


def main() -> None:
    """Демонстрація ланцюжка pure updates без мутації початкового стану."""
    s0 = build_initial_student()
    s1 = add_course_result(
        s0,
        course="Функціональне програмування",
        credits=5,
        grade=96.0,
    )
    s2 = add_skill(s1, "Functional Programming")

    render_student_card("Початковий стан s0 (не змінений)", s0)
    render_student_card("Після pure updates s2 (новий екземпляр)", s2)

    best = top_courses(s2.results, n=2)
    print("Топ-2 дисципліни:", ", ".join(f"{c.course} ({c.grade:.1f})" for c in best))


if __name__ == "__main__":
    main()
