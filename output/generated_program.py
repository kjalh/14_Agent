from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real


MIN_SCORE = 0.0
MAX_SCORE = 100.0


@dataclass(frozen=True)
class Student:
    """학생 한 명의 이름과 점수를 표현한다."""

    name: str
    score: float


@dataclass(frozen=True)
class GradeBook:
    """등록된 학생 목록을 표현한다."""

    students: tuple[Student, ...] = ()


def create_gradebook() -> GradeBook:
    """빈 성적 관리 객체를 생성한다."""
    return GradeBook()


def _validate_gradebook(gradebook: GradeBook) -> None:
    """성적 관리 객체의 타입을 검증한다."""
    if not isinstance(gradebook, GradeBook):
        raise TypeError("gradebook은 GradeBook 객체여야 합니다.")


def register_student(
    gradebook: GradeBook,
    name: str,
    score: int | float,
) -> GradeBook:
    """
    학생을 등록한 새로운 GradeBook 객체를 반환한다.

    이름은 앞뒤 공백을 제거한 뒤 저장한다.
    점수는 0점 이상 100점 이하의 유한한 숫자만 허용한다.
    동일한 이름의 학생은 중복 등록할 수 없다.
    """
    _validate_gradebook(gradebook)

    if not isinstance(name, str):
        raise TypeError("학생 이름은 문자열이어야 합니다.")

    normalized_name = name.strip()

    if not normalized_name:
        raise ValueError("학생 이름은 비어 있을 수 없습니다.")

    if isinstance(score, bool) or not isinstance(score, Real):
        raise TypeError("점수는 숫자여야 합니다.")

    try:
        normalized_score = float(score)
    except (OverflowError, ValueError, TypeError) as error:
        raise ValueError("점수는 변환 가능한 숫자여야 합니다.") from error

    if not isfinite(normalized_score):
        raise ValueError("점수는 유한한 숫자여야 합니다.")

    if not MIN_SCORE <= normalized_score <= MAX_SCORE:
        raise ValueError(
            f"점수는 {MIN_SCORE:g}점 이상 {MAX_SCORE:g}점 이하여야 합니다."
        )

    if any(
        student.name == normalized_name
        for student in gradebook.students
    ):
        raise ValueError(
            f"이미 등록된 학생 이름입니다: {normalized_name}"
        )

    student = Student(
        name=normalized_name,
        score=normalized_score,
    )

    return GradeBook(
        students=gradebook.students + (student,)
    )


def list_students(
    gradebook: GradeBook,
) -> tuple[Student, ...]:
    """등록된 학생을 등록 순서대로 모두 반환한다."""
    _validate_gradebook(gradebook)
    return gradebook.students


def average_score(
    gradebook: GradeBook,
) -> float | None:
    """
    전체 학생의 평균 점수를 반환한다.

    등록된 학생이 없으면 None을 반환한다.
    """
    _validate_gradebook(gradebook)

    if not gradebook.students:
        return None

    total_score = sum(
        student.score
        for student in gradebook.students
    )

    return total_score / len(gradebook.students)


def top_students(
    gradebook: GradeBook,
) -> tuple[Student, ...]:
    """
    최고 점수를 받은 학생을 모두 반환한다.

    동점자는 등록 순서를 유지한다.
    등록된 학생이 없으면 빈 튜플을 반환한다.
    """
    _validate_gradebook(gradebook)

    if not gradebook.students:
        return ()

    highest_score = max(
        student.score
        for student in gradebook.students
    )

    return tuple(
        student
        for student in gradebook.students
        if student.score == highest_score
    )