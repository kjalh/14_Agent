from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real
from typing import Tuple


__all__ = [
    "GradeBookError",
    "InvalidStudentNameError",
    "InvalidScoreError",
    "DuplicateStudentError",
    "NoStudentsError",
    "StudentRecord",
    "GradeBook",
    "create_grade_book",
    "register_student",
    "get_all_students",
    "calculate_average_score",
    "get_top_students",
]


class GradeBookError(Exception):
    """성적부 관련 예외의 기본 클래스."""


class InvalidStudentNameError(GradeBookError, ValueError):
    """학생 이름이 유효하지 않을 때 발생하는 예외."""


class InvalidScoreError(GradeBookError, ValueError):
    """학생 점수가 유효하지 않을 때 발생하는 예외."""


class DuplicateStudentError(GradeBookError, ValueError):
    """동일한 학생 이름이 이미 등록되어 있을 때 발생하는 예외."""


class NoStudentsError(GradeBookError, LookupError):
    """등록된 학생이 없을 때 발생하는 예외."""


@dataclass(frozen=True)
class StudentRecord:
    """학생 이름과 점수를 저장하는 불변 자료구조."""

    name: str
    score: float


@dataclass(frozen=True)
class GradeBook:
    """학생 성적 목록을 저장하는 불변 성적부."""

    students: Tuple[StudentRecord, ...] = ()


def create_grade_book() -> GradeBook:
    """
    빈 성적부를 생성한다.

    Returns:
        학생이 등록되지 않은 빈 GradeBook
    """
    return GradeBook()


def register_student(
    grade_book: GradeBook,
    name: str,
    score: Real,
) -> GradeBook:
    """
    학생을 등록한 새로운 성적부를 반환한다.

    기존 성적부는 변경되지 않는다. 동일한 이름의 학생은 등록할 수 없다.

    Args:
        grade_book: 기존 성적부
        name: 등록할 학생 이름
        score: 등록할 점수. 0 이상 100 이하의 유한한 숫자

    Returns:
        학생이 추가된 새로운 GradeBook

    Raises:
        InvalidStudentNameError:
            이름이 문자열이 아니거나 공백인 경우
        InvalidScoreError:
            점수가 숫자가 아니거나 0~100 범위를 벗어난 경우
        DuplicateStudentError:
            동일한 이름이 이미 등록된 경우
    """
    validated_name = _validate_name(name)
    validated_score = _validate_score(score)

    if any(
        student.name == validated_name
        for student in grade_book.students
    ):
        raise DuplicateStudentError(
            f"이미 등록된 학생 이름입니다: {validated_name}"
        )

    new_student = StudentRecord(
        name=validated_name,
        score=validated_score,
    )

    return GradeBook(
        students=grade_book.students + (new_student,),
    )


def get_all_students(
    grade_book: GradeBook,
) -> Tuple[StudentRecord, ...]:
    """
    등록된 전체 학생 목록을 등록 순서대로 반환한다.

    Returns:
        StudentRecord의 불변 튜플
    """
    return grade_book.students


def calculate_average_score(grade_book: GradeBook) -> float:
    """
    등록된 전체 학생의 평균 점수를 계산한다.

    Returns:
        전체 학생 점수의 평균

    Raises:
        NoStudentsError:
            등록된 학생이 없는 경우
    """
    if not grade_book.students:
        raise NoStudentsError("등록된 학생이 없습니다.")

    total_score = sum(
        student.score for student in grade_book.students
    )

    return total_score / len(grade_book.students)


def get_top_students(
    grade_book: GradeBook,
) -> Tuple[StudentRecord, ...]:
    """
    최고 점수 학생을 모두 반환한다.

    최고 점수가 같은 학생이 여러 명이면 등록 순서를 유지하여
    모두 반환한다.

    Returns:
        최고 점수 학생들의 불변 튜플

    Raises:
        NoStudentsError:
            등록된 학생이 없는 경우
    """
    if not grade_book.students:
        raise NoStudentsError("등록된 학생이 없습니다.")

    highest_score = max(
        student.score for student in grade_book.students
    )

    return tuple(
        student
        for student in grade_book.students
        if student.score == highest_score
    )


def _validate_name(name: str) -> str:
    """
    학생 이름을 검증하고 앞뒤 공백을 제거한 이름을 반환한다.

    Raises:
        InvalidStudentNameError:
            이름이 문자열이 아니거나 비어 있는 경우
    """
    if not isinstance(name, str):
        raise InvalidStudentNameError(
            "학생 이름은 문자열이어야 합니다."
        )

    normalized_name = name.strip()

    if not normalized_name:
        raise InvalidStudentNameError(
            "학생 이름은 비어 있을 수 없습니다."
        )

    return normalized_name


def _validate_score(score: Real) -> float:
    """
    학생 점수를 검증하고 float으로 변환하여 반환한다.

    점수는 0 이상 100 이하인 유한한 숫자만 허용한다.

    Raises:
        InvalidScoreError:
            점수가 숫자가 아니거나 유효한 범위를 벗어난 경우
    """
    if isinstance(score, bool) or not isinstance(score, Real):
        raise InvalidScoreError("점수는 숫자여야 합니다.")

    try:
        numeric_score = float(score)
    except (TypeError, ValueError, OverflowError) as error:
        raise InvalidScoreError(
            "점수는 숫자로 변환할 수 있어야 합니다."
        ) from error

    if not isfinite(numeric_score):
        raise InvalidScoreError(
            "점수는 유한한 숫자여야 합니다."
        )

    if not 0 <= numeric_score <= 100:
        raise InvalidScoreError(
            "점수는 0 이상 100 이하이어야 합니다."
        )

    return numeric_score