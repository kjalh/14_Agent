# 프로젝트 목적

학생 이름과 점수를 등록하고, 등록된 성적을 조회·분석할 수 있는 함수형 성적 관리 API를 설계한다.

- Python 표준 라이브러리만 사용
- `input()`과 `print()`를 사용하지 않음
- 상태를 직접 변경하지 않고, 새로운 성적부를 반환하는 방식으로 구현
- 점수 범위는 `0점 이상 100점 이하`
- 동일한 이름의 학생은 중복 등록하지 않음
- 최고 점수 동점자는 모두 조회

# 필수 기능 목록

1. 학생 성적 등록
2. 전체 학생 목록 조회
3. 전체 학생 평균 점수 계산
4. 최고 점수 학생 조회
5. 입력값 검증
6. 학생이 없을 때의 예외 처리
7. 동일한 학생 이름 중복 등록 방지

# 자료구조

## 학생 정보

```python
StudentRecord(
    name="홍길동",
    score=95.0,
)
```

`StudentRecord`는 변경할 수 없는 불변 데이터 구조로 사용한다.

## 성적부

```python
GradeBook(
    students=(
        StudentRecord(name="홍길동", score=95.0),
        StudentRecord(name="김철수", score=88.0),
    )
)
```

- 학생 목록은 `tuple`로 저장한다.
- 등록 함수는 기존 객체를 변경하지 않고 새로운 `GradeBook`을 반환한다.
- 조회 함수는 원본 데이터를 변경하지 않는다.

# 함수 목록과 함수별 역할

| 함수 | 역할 |
|---|---|
| `create_grade_book` | 빈 성적부 생성 |
| `register_student` | 학생 이름과 점수 등록 |
| `get_all_students` | 전체 학생 목록 조회 |
| `calculate_average_score` | 전체 학생 평균 점수 계산 |
| `get_top_students` | 최고 점수 학생 조회 |
| `_validate_name` | 학생 이름 검증 |
| `_validate_score` | 점수 검증 |

## 구현 코드

```python
from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Tuple


class GradeBookError(Exception):
    """성적부 관련 예외의 기본 클래스."""


class InvalidStudentNameError(GradeBookError, ValueError):
    """학생 이름이 유효하지 않을 때 발생."""


class InvalidScoreError(GradeBookError, ValueError):
    """점수가 유효하지 않을 때 발생."""


class DuplicateStudentError(GradeBookError, ValueError):
    """동일한 학생 이름이 이미 등록되어 있을 때 발생."""


class NoStudentsError(GradeBookError, LookupError):
    """등록된 학생이 없을 때 발생."""


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
        GradeBook: 학생이 등록되지 않은 빈 성적부
    """
    return GradeBook()


def register_student(
    grade_book: GradeBook,
    name: str,
    score: Real,
) -> GradeBook:
    """
    학생 이름과 점수를 등록한 새로운 성적부를 반환한다.

    Args:
        grade_book: 기존 성적부
        name: 등록할 학생 이름
        score: 등록할 점수. 0 이상 100 이하의 숫자

    Returns:
        GradeBook: 학생이 추가된 새로운 성적부

    Raises:
        InvalidStudentNameError: 이름이 비어 있거나 문자열이 아닌 경우
        InvalidScoreError: 점수가 숫자가 아니거나 범위를 벗어난 경우
        DuplicateStudentError: 동일한 이름이 이미 등록된 경우
    """
    validated_name = _validate_name(name)
    validated_score = _validate_score(score)

    if any(student.name == validated_name for student in grade_book.students):
        raise DuplicateStudentError(
            f"이미 등록된 학생 이름입니다: {validated_name}"
        )

    new_student = StudentRecord(
        name=validated_name,
        score=validated_score,
    )

    return GradeBook(
        students=grade_book.students + (new_student,)
    )


def get_all_students(
    grade_book: GradeBook,
) -> Tuple[StudentRecord, ...]:
    """
    전체 학생 목록을 반환한다.

    Args:
        grade_book: 조회할 성적부

    Returns:
        Tuple[StudentRecord, ...]: 등록 순서대로 정렬된 학생 목록
    """
    return grade_book.students


def calculate_average_score(
    grade_book: GradeBook,
) -> float:
    """
    전체 학생의 평균 점수를 계산한다.

    Args:
        grade_book: 평균을 계산할 성적부

    Returns:
        float: 전체 학생의 평균 점수

    Raises:
        NoStudentsError: 등록된 학생이 없는 경우
    """
    if not grade_book.students:
        raise NoStudentsError("등록된 학생이 없습니다.")

    total_score = sum(student.score for student in grade_book.students)
    return total_score / len(grade_book.students)


def get_top_students(
    grade_book: GradeBook,
) -> Tuple[StudentRecord, ...]:
    """
    최고 점수 학생을 모두 반환한다.

    최고 점수가 같은 학생이 여러 명이면 모두 반환한다.

    Args:
        grade_book: 최고 점수 학생을 조회할 성적부

    Returns:
        Tuple[StudentRecord, ...]: 최고 점수 학생 목록

    Raises:
        NoStudentsError: 등록된 학생이 없는 경우
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
    학생 이름을 검증하고 양쪽 공백을 제거한 이름을 반환한다.

    Args:
        name: 검증할 학생 이름

    Returns:
        str: 정리된 학생 이름

    Raises:
        InvalidStudentNameError: 이름이 문자열이 아니거나 비어 있는 경우
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
    학생 점수를 검증하고 float으로 변환한다.

    Args:
        score: 검증할 점수

    Returns:
        float: 검증된 점수

    Raises:
        InvalidScoreError: 숫자가 아니거나 0~100 범위를 벗어난 경우
    """
    if isinstance(score, bool) or not isinstance(score, Real):
        raise InvalidScoreError(
            "점수는 숫자여야 합니다."
        )

    numeric_score = float(score)

    if not 0 <= numeric_score <= 100:
        raise InvalidScoreError(
            "점수는 0 이상 100 이하이어야 합니다."
        )

    return numeric_score
```

## 사용 예시

```python
grade_book = create_grade_book()

grade_book = register_student(grade_book, "홍길동", 95)
grade_book = register_student(grade_book, "김철수", 88)
grade_book = register_student(grade_book, "이영희", 95)

students = get_all_students(grade_book)
average = calculate_average_score(grade_book)
top_students = get_top_students(grade_book)

print(students)
# (
#     StudentRecord(name='홍길동', score=95.0),
#     StudentRecord(name='김철수', score=88.0),
#     StudentRecord(name='이영희', score=95.0)
# )

print(average)
# 92.66666666666667

print(top_students)
# (
#     StudentRecord(name='홍길동', score=95.0),
#     StudentRecord(name='이영희', score=95.0)
# )
```

`register_student()`는 성적부를 직접 변경하지 않으므로 반드시 반환값을 다시 할당해야 한다.

```python
grade_book = register_student(grade_book, "박민수", 77)
```

# 프로그램 흐름

1. `create_grade_book()`으로 빈 성적부를 생성한다.
2. `register_student()`에 성적부, 학생 이름, 점수를 전달한다.
3. 이름과 점수를 검증한다.
4. 동일한 이름의 학생이 있는지 확인한다.
5. 기존 성적부를 변경하지 않고 새로운 성적부를 반환한다.
6. `get_all_students()`로 전체 학생 목록을 조회한다.
7. `calculate_average_score()`로 평균 점수를 계산한다.
8. `get_top_students()`로 최고 점수 학생을 조회한다.
9. API 사용자는 필요한 경우 예외를 처리하여 화면 출력이나 다른 로직을 구현한다.

# 예외 처리 요구사항

## 학생 이름이 비어 있는 경우

```python
try:
    grade_book = register_student(grade_book, "", 90)
except InvalidStudentNameError as error:
    print(error)
```

발생 예외:

```text
InvalidStudentNameError
```

## 학생 이름이 문자열이 아닌 경우

```python
register_student(grade_book, 123, 90)
```

발생 예외:

```text
InvalidStudentNameError
```

## 점수가 숫자가 아닌 경우

```python
register_student(grade_book, "홍길동", "구십점")
```

발생 예외:

```text
InvalidScoreError
```

## 점수가 허용 범위를 벗어난 경우

```python
register_student(grade_book, "홍길동", 101)
```

발생 예외:

```text
InvalidScoreError
```

## 동일한 이름을 등록하는 경우

```python
grade_book = register_student(grade_book, "홍길동", 90)
grade_book = register_student(grade_book, "홍길동", 80)
```

발생 예외:

```text
DuplicateStudentError
```

## 등록된 학생이 없는 경우 평균 계산

```python
empty_grade_book = create_grade_book()
calculate_average_score(empty_grade_book)
```

발생 예외:

```text
NoStudentsError
```

## 등록된 학생이 없는 경우 최고 점수 조회

```python
empty_grade_book = create_grade_book()
get_top_students(empty_grade_book)
```

발생 예외:

```text
NoStudentsError
```

이 설계는 콘솔 입력이나 화면 출력에 의존하지 않으므로 콘솔, 웹 서버, GUI 등 다양한 외부 인터페이스에서 재사용할 수 있다.