"""Чисті функції та pure-оновлення для моделі студента (Лабораторна №3, Варіант 3)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from functools import lru_cache
from types import MappingProxyType

from model import CourseResult, Student


def calculate_average(results: Sequence[CourseResult]) -> float:
    """Чиста функція обчислення середнього арифметичного балу за курси."""
    if not results:
        return 0.0
    return round(sum(item.grade for item in results) / len(results), 2)


@lru_cache(maxsize=256)
def calculate_weighted_gpa(results: tuple[CourseResult, ...]) -> float:
    """Кешована чиста функція середньозваженого балу за кредитами ЄКТС."""
    total_credits = sum(item.credits for item in results)
    if total_credits == 0:
        return 0.0
    weighted_sum = sum(item.weighted_points() for item in results)
    return round(weighted_sum / total_credits, 2)


def add_course_result(
    student: Student,
    course: str,
    credits: int,
    grade: float,
) -> Student:
    """Pure update: додає нову оцінку з курсу та оновлює середній бал у профілі."""
    new_result = CourseResult(course=course, credits=credits, grade=grade)
    updated_student = student.with_result(new_result)
    return recalculate_average_in_profile(updated_student)


def add_skill(student: Student, skill: str) -> Student:
    """Pure update: додає навичку до frozenset без мутації вхідного об'єкта."""
    return student.with_skill(skill)


def remove_skill(student: Student, skill: str) -> Student:
    """Pure update: видаляє навичку, повертаючи новий екземпляр Student."""
    return replace(student, skills=student.skills - frozenset({skill}))


def recalculate_average_in_profile(student: Student) -> Student:
    """Pure update: перераховує середній і зважений бали та записує у новий профіль."""
    avg_score = calculate_average(student.results)
    weighted_gpa = calculate_weighted_gpa(student.results)
    new_profile = {
        **dict(student.profile),
        "average_grade": f"{avg_score:.2f}",
        "weighted_gpa": f"{weighted_gpa:.2f}",
    }
    return replace(student, profile=MappingProxyType(new_profile))


def top_courses(
    results: Sequence[CourseResult], n: int = 3
) -> tuple[CourseResult, ...]:
    """Повертає незмінний кортеж із N курсів із найвищими балами."""
    ordered = sorted(results, key=lambda r: (-r.grade, r.course))
    return tuple(ordered[: max(0, n)])
