"""Незмінні доменні моделі успішності студентів (Лабораторна №3, Варіант 3)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any


def freeze(obj: Any) -> Any:
    """Рекурсивно перетворює мутабельні колекції на незмінні аналоги."""
    if isinstance(obj, Mapping):
        frozen_dict = {k: freeze(v) for k, v in obj.items()}
        return MappingProxyType(frozen_dict)
    if isinstance(obj, set):
        return frozenset(freeze(item) for item in obj)
    if isinstance(obj, (list, tuple)):
        return tuple(freeze(item) for item in obj)
    return obj


def make_profile(**kwargs: str) -> Mapping[str, str]:
    """Створює read-only відображення профілю з попередньою копією словника."""
    base: dict[str, str] = dict(kwargs)
    return MappingProxyType(base)


@dataclass(frozen=True, slots=True)
class CourseResult:
    """Незмінний запис оцінки студента з окремої дисципліни (повністю хешований)."""

    course: str
    credits: int
    grade: float

    def weighted_points(self) -> float:
        """Повертає добуток оцінки на кількість кредитів ЄКТС."""
        return self.grade * self.credits


@dataclass(frozen=True, slots=True)
class Student:
    """Незмінна модель студента з tuple-оцінками, frozenset-навичками та proxy-профілем."""

    student_id: int
    full_name: str
    results: tuple[CourseResult, ...]
    skills: frozenset[str]
    profile: Mapping[str, str]

    def with_result(self, result: CourseResult) -> Student:
        """Pure update: повертає копію студента з доданою оцінкою з курсу."""
        return replace(self, results=self.results + (result,))

    def with_skill(self, skill: str) -> Student:
        """Pure update: повертає копію студента з новою навичкою."""
        normalized = skill.strip()
        if not normalized:
            return self
        return replace(self, skills=self.skills | frozenset({normalized}))

    def with_profile_entry(self, key: str, value: str) -> Student:
        """Pure update: повертає копію студента з оновленим полем профілю."""
        updated = {**dict(self.profile), key: value}
        return replace(self, profile=MappingProxyType(updated))
