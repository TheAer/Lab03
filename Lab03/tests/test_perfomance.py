"""Порівняння часу виконання операцій: мутабельний (deepcopy) vs незмінний підхід."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from core import add_course_result, add_skill, calculate_weighted_gpa
from model import CourseResult, Student, make_profile


@dataclass
class MutableCourse:
    course: str
    credits: int
    grade: float


@dataclass
class MutableStudent:
    student_id: int
    full_name: str
    results: list[MutableCourse]
    skills: set[str]
    profile: dict[str, str]


def _mutable_safe_updates(iterations: int) -> MutableStudent:
    """Імітація безпечних оновлень на мутабельних колекціях (потрібен deepcopy)."""
    st = MutableStudent(
        student_id=1,
        full_name="Тестовий Студент",
        results=[MutableCourse("Курс 0", 4, 85.0)],
        skills={"Python"},
        profile={"group": "ФЕП-21с"},
    )
    for idx in range(1, iterations + 1):
        st = deepcopy(st)
        st.results.append(MutableCourse(f"Курс {idx}", 4, 90.0))
        st.skills.add(f"Skill_{idx}")
        st.profile["last_course"] = f"Курс {idx}"
    return st


def _immutable_pure_updates(iterations: int) -> Student:
    """Pure updates на незмінних структурах (structural sharing без deepcopy)."""
    st = Student(
        student_id=1,
        full_name="Тестовий Студент",
        results=(CourseResult("Курс 0", 4, 85.0),),
        skills=frozenset({"Python"}),
        profile=make_profile(group="ФЕП-21с"),
    )
    for idx in range(1, iterations + 1):
        st = add_course_result(st, f"Курс {idx}", 4, 90.0)
        st = add_skill(st, f"Skill_{idx}")
    return st


def test_mutable_deepcopy_workload() -> None:
    """Базовий замір: серія безпечних оновлень на мутабельній моделі через deepcopy."""
    res = _mutable_safe_updates(500)
    assert len(res.results) == 501


def test_immutable_structural_sharing_workload() -> None:
    """Замір після переходу на immutable-модель (tuple + frozenset + frozen dataclass)."""
    calculate_weighted_gpa.cache_clear()
    res = _immutable_pure_updates(500)
    assert len(res.results) == 501
