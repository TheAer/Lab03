"""Тести на незмінність, pure updates, read-only proxy та хешованість (Варіант 3)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core import (
    add_course_result,
    add_skill,
    calculate_average,
    calculate_weighted_gpa,
    recalculate_average_in_profile,
    remove_skill,
)
from model import CourseResult, Student, freeze, make_profile


@pytest.fixture
def sample_student() -> Student:
    base = Student(
        student_id=101,
        full_name="Коваленко Олена",
        results=(
            CourseResult("Математичний аналіз", 5, 84.0),
            CourseResult("Програмування на Python", 5, 94.0),
        ),
        skills=frozenset({"Python", "Git"}),
        profile=make_profile(group="ФЕП-21с", city="Львів"),
    )
    return recalculate_average_in_profile(base)


def test_frozen_dataclass_prevents_attribute_mutation(
    sample_student: Student,
) -> None:
    """Перевіряє, що спроба змінити поля frozen dataclass викликає FrozenInstanceError."""
    with pytest.raises(FrozenInstanceError):
        sample_student.full_name = "Інше Ім'я"  # type: ignore[misc]

    first_course = sample_student.results[0]
    with pytest.raises(FrozenInstanceError):
        first_course.grade = 100.0  # type: ignore[misc]


def test_mappingproxy_is_read_only_and_isolated() -> None:
    """Перевіряє read-only поведінку MappingProxyType та ізоляцію від вихідного dict."""
    raw = {"group": "ФЕП-21с", "status": "active"}
    proxy = make_profile(**raw)
    raw["status"] = "expelled"

    assert proxy["status"] == "active"
    with pytest.raises(TypeError):
        proxy["group"] = "ФЕП-22с"  # type: ignore[index]


def test_pure_updates_do_not_mutate_original(sample_student: Student) -> None:
    """Перевіряє, що pure-оновлення повертають нові копії без зміни вхідного студента."""
    orig_ref = sample_student
    orig_results = sample_student.results
    orig_skills = sample_student.skills
    orig_profile = dict(sample_student.profile)

    s_with_grade = add_course_result(sample_student, "Бази даних", 4, 92.0)
    s_with_skill = add_skill(s_with_grade, "PostgreSQL")
    s_final = remove_skill(s_with_skill, "Git")

    assert sample_student is orig_ref
    assert sample_student.results == orig_results
    assert sample_student.skills == orig_skills
    assert dict(sample_student.profile) == orig_profile
    assert len(sample_student.results) == 2
    assert sample_student.profile["average_grade"] == "89.00"

    assert s_final is not sample_student
    assert len(s_final.results) == 3
    assert s_final.profile["average_grade"] == "90.00"
    assert s_final.skills == frozenset({"Python", "PostgreSQL"})


def test_hashability_and_unhashable_explanation(sample_student: Student) -> None:
    """CourseResult є хешованим; Student не хешується через MappingProxyType у profile."""
    c1 = CourseResult("Бази даних", 4, 92.0)
    c2 = CourseResult("Бази даних", 4, 92.0)
    c3 = CourseResult("Алгоритми", 5, 88.0)

    unique_courses = {c1, c2, c3}
    assert len(unique_courses) == 2
    assert hash(c1) == hash(c2)

    with pytest.raises(TypeError, match="mappingproxy"):
        hash(sample_student)


def test_deep_freeze_utility() -> None:
    """Перевіряє рекурсивне заморожування вкладених мутабельних структур."""
    nested = {"tags": {"fp", "python"}, "scores": [90, 95], "meta": {"term": 3}}
    frozen = freeze(nested)

    assert isinstance(frozen["tags"], frozenset)
    assert isinstance(frozen["scores"], tuple)
    with pytest.raises(TypeError):
        frozen["meta"]["term"] = 4


def test_lru_cache_on_tuple_results(sample_student: Student) -> None:
    """Перевіряє роботу lru_cache для обчислення зваженого GPA по tuple-оцінках."""
    calculate_weighted_gpa.cache_clear()
    avg = calculate_average(sample_student.results)
    gpa1 = calculate_weighted_gpa(sample_student.results)
    gpa2 = calculate_weighted_gpa(sample_student.results)
    info = calculate_weighted_gpa.cache_info()

    assert avg == gpa1 == gpa2 == 89.0
    assert info.hits >= 1
