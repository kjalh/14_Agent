from __future__ import annotations

from typing import TypeAlias


StudentScore: TypeAlias = tuple[str, float]
GradeBook: TypeAlias = dict[str, float]


class GradeBookError(Exception):
    """성적 관리 프로그램의 기본 예외."""


class EmptyGradeBookError(GradeBookError):
    """등록된 학생이 없을 때 발생하는 예외."""


class DuplicateStudentError(GradeBookError):
    """동일한 학생 이름이 이미 등록되어 있을 때 발생하는 예외."""


def create_grade_book() -> GradeBook:
    """빈 성적부를 생성한다."""
    return {}


def _validate_student_name(name: str) -> str:
    """학생 이름을 검증하고 앞뒤 공백을 제거한 이름을 반환한다."""
    if not isinstance(name, str):
        raise TypeError("학생 이름은 문자열이어야 합니다.")

    normalized_name = name.strip()

    if not normalized_name:
        raise ValueError("학생 이름은 비어 있을 수 없습니다.")

    return normalized_name


def _validate_score(score: int | float) -> float:
    """점수를 검증하고 float으로 변환하여 반환한다."""
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        raise TypeError("점수는 숫자여야 합니다.")

    if not 0 <= score <= 100:
        raise ValueError("점수는 0점 이상 100점 이하이어야 합니다.")

    return float(score)


def _validate_grade_book(grade_book: GradeBook) -> None:
    """성적부의 자료형과 저장된 데이터의 유효성을 검증한다."""
    if not isinstance(grade_book, dict):
        raise TypeError("성적부는 dict 자료형이어야 합니다.")

    for name, score in grade_book.items():
        _validate_student_name(name)
        _validate_score(score)


def _ensure_not_empty(grade_book: GradeBook) -> None:
    """성적부가 비어 있지 않은지 검사한다."""
    if not grade_book:
        raise EmptyGradeBookError("등록된 학생이 없습니다.")


def register_student(
    grade_book: GradeBook,
    name: str,
    score: int | float,
) -> GradeBook:
    """
    학생 이름과 점수를 등록한 새로운 성적부를 반환한다.

    기존 성적부는 변경하지 않는다.
    """
    _validate_grade_book(grade_book)

    normalized_name = _validate_student_name(name)
    normalized_score = _validate_score(score)

    if normalized_name in grade_book:
        raise DuplicateStudentError(
            f"'{normalized_name}' 학생은 이미 등록되어 있습니다."
        )

    updated_grade_book = grade_book.copy()
    updated_grade_book[normalized_name] = normalized_score
    return updated_grade_book


def list_students(grade_book: GradeBook) -> list[StudentScore]:
    """전체 학생 목록을 등록 순서대로 반환한다."""
    _validate_grade_book(grade_book)
    _ensure_not_empty(grade_book)
    return list(grade_book.items())


def calculate_average(grade_book: GradeBook) -> float:
    """전체 학생의 평균 점수를 반환한다."""
    _validate_grade_book(grade_book)
    _ensure_not_empty(grade_book)
    return sum(grade_book.values()) / len(grade_book)


def find_top_student(grade_book: GradeBook) -> StudentScore:
    """
    최고 점수 학생의 이름과 점수를 반환한다.

    최고 점수가 같은 경우 등록 순서상 먼저 등록된 학생을 반환한다.
    """
    _validate_grade_book(grade_book)
    _ensure_not_empty(grade_book)

    return max(grade_book.items(), key=lambda item: item[1])


def _validate_student_score(student: StudentScore) -> StudentScore:
    """학생 점수 튜플을 검증하고 정규화하여 반환한다."""
    if not isinstance(student, tuple) or len(student) != 2:
        raise TypeError("학생 정보는 (이름, 점수) 형태의 튜플이어야 합니다.")

    name, score = student
    normalized_name = _validate_student_name(name)
    normalized_score = _validate_score(score)
    return normalized_name, normalized_score


def format_student_list(students: list[StudentScore]) -> str:
    """학생 목록을 표시용 문자열로 변환한다."""
    if not isinstance(students, list):
        raise TypeError("학생 목록은 list 자료형이어야 합니다.")

    if not students:
        raise EmptyGradeBookError("등록된 학생이 없습니다.")

    validated_students = [
        _validate_student_score(student)
        for student in students
    ]

    return "\n".join(
        f"{name}: {_format_score(score)}점"
        for name, score in validated_students
    )


def format_average(average: int | float) -> str:
    """평균 점수를 표시용 문자열로 변환한다."""
    normalized_average = _validate_score(average)
    return f"평균 점수: {_format_score(normalized_average)}점"


def format_top_student(student: StudentScore) -> str:
    """최고 점수 학생 정보를 표시용 문자열로 변환한다."""
    name, score = _validate_student_score(student)
    return f"최고 점수 학생: {name}, {_format_score(score)}점"


def _format_score(score: int | float) -> str:
    """정수 점수는 소수점 없이 표시하고, 실수는 필요한 만큼 표시한다."""
    normalized_score = _validate_score(score)

    if normalized_score.is_integer():
        return str(int(normalized_score))

    return f"{normalized_score:g}"


__all__ = [
    "StudentScore",
    "GradeBook",
    "GradeBookError",
    "EmptyGradeBookError",
    "DuplicateStudentError",
    "create_grade_book",
    "register_student",
    "list_students",
    "calculate_average",
    "find_top_student",
    "format_student_list",
    "format_average",
    "format_top_student",
]