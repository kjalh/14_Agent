# 프로젝트 목적

학생 이름과 점수를 등록하고, 등록된 성적을 조회·분석하는 프로그램을 설계한다.

프로그램은 `input()`이나 `print()`를 사용하지 않고, 외부에서 값을 전달받아 결과를 반환하는 함수형 API로 제공한다.

- 학생 성적 등록
- 전체 학생 목록 조회
- 전체 평균 점수 계산
- 최고 점수 학생 조회
- 잘못된 이름·점수·빈 성적부에 대한 예외 처리

정책은 다음과 같이 결정한다.

- 점수 범위: `0점 이상 100점 이하`
- 동일한 이름의 학생: 중복 등록 불가
- 학생 이름: 앞뒤 공백 제거 후 빈 문자열이면 등록 불가
- 점수: 정수와 실수 모두 허용
- `bool`은 Python에서 숫자로 취급되므로 점수로 허용하지 않음

---

# 필수 기능 목록

1. **학생 성적 등록**
   - 학생 이름과 점수를 등록한다.
   - 이름이 중복되면 등록하지 않는다.
   - 점수는 `0~100` 범위만 허용한다.

2. **전체 학생 목록 조회**
   - 등록 순서대로 모든 학생의 이름과 점수를 반환한다.
   - 등록된 학생이 없으면 예외를 발생시킨다.

3. **평균 점수 계산**
   - 전체 학생의 평균 점수를 계산한다.
   - 등록된 학생이 없으면 예외를 발생시킨다.

4. **최고 점수 학생 조회**
   - 가장 높은 점수의 학생을 반환한다.
   - 최고 점수 학생이 여러 명이면 등록 순서상 먼저 등록된 학생을 반환한다.
   - 등록된 학생이 없으면 예외를 발생시킨다.

5. **결과 문자열 변환**
   - API 결과를 사용자에게 표시할 수 있는 문자열로 변환한다.
   - 실제 출력은 호출하는 애플리케이션이 담당한다.

---

# 자료구조

## 학생 성적 저장 구조

학생 이름을 키로, 점수를 값으로 저장하는 딕셔너리를 사용한다.

```python
GradeBook = dict[str, float]
```

예시:

```python
{
    "김민수": 85.0,
    "이서연": 92.0,
}
```

Python 딕셔너리는 삽입 순서를 유지하므로 학생 목록 조회와 동점자 처리에 활용할 수 있다.

## 반환 자료구조

학생 한 명의 정보는 다음 튜플로 반환한다.

```python
StudentScore = tuple[str, float]
```

예시:

```python
("이서연", 92.0)
```

전체 학생 목록은 다음과 같다.

```python
list[StudentScore]
```

예시:

```python
[
    ("김민수", 85.0),
    ("이서연", 92.0),
]
```

## 예외 자료구조

```python
class GradeBookError(Exception):
    """성적 관리 프로그램의 기본 예외."""


class EmptyGradeBookError(GradeBookError):
    """등록된 학생이 없을 때 발생하는 예외."""


class DuplicateStudentError(GradeBookError):
    """동일한 학생 이름이 이미 등록되어 있을 때 발생하는 예외."""
```

---

# 함수 목록과 함수별 역할

## 함수 시그니처 요약

```python
def create_grade_book() -> GradeBook:
    ...


def register_student(
    grade_book: GradeBook,
    name: str,
    score: int | float,
) -> GradeBook:
    ...


def list_students(
    grade_book: GradeBook,
) -> list[StudentScore]:
    ...


def calculate_average(
    grade_book: GradeBook,
) -> float:
    ...


def find_top_student(
    grade_book: GradeBook,
) -> StudentScore:
    ...


def format_student_list(
    students: list[StudentScore],
) -> str:
    ...


def format_average(
    average: float,
) -> str:
    ...


def format_top_student(
    student: StudentScore,
) -> str:
    ...
```

## 1. `create_grade_book`

```python
def create_grade_book() -> GradeBook:
```

### 역할

새로운 빈 성적부를 생성한다.

### 반환값

```python
{}
```

---

## 2. `register_student`

```python
def register_student(
    grade_book: GradeBook,
    name: str,
    score: int | float,
) -> GradeBook:
```

### 역할

학생 이름과 점수를 성적부에 등록한다.

### 동작 규칙

- 이름 앞뒤의 공백을 제거한다.
- 이름이 문자열이 아니면 예외를 발생시킨다.
- 이름이 빈 문자열이면 예외를 발생시킨다.
- 점수가 숫자가 아니면 예외를 발생시킨다.
- `bool`은 점수로 허용하지 않는다.
- 점수가 `0~100` 범위를 벗어나면 예외를 발생시킨다.
- 동일한 이름이 이미 존재하면 `DuplicateStudentError`를 발생시킨다.
- 기존 딕셔너리를 직접 변경하지 않고 복사본을 반환한다.

---

## 3. `list_students`

```python
def list_students(
    grade_book: GradeBook,
) -> list[StudentScore]:
```

### 역할

전체 학생 목록을 등록 순서대로 반환한다.

### 반환 예시

```python
[
    ("김민수", 85.0),
    ("이서연", 92.0),
]
```

### 예외

성적부가 비어 있으면 `EmptyGradeBookError`를 발생시킨다.

---

## 4. `calculate_average`

```python
def calculate_average(
    grade_book: GradeBook,
) -> float:
```

### 역할

전체 학생의 평균 점수를 계산한다.

### 반환 예시

```python
88.5
```

### 예외

성적부가 비어 있으면 `EmptyGradeBookError`를 발생시킨다.

---

## 5. `find_top_student`

```python
def find_top_student(
    grade_book: GradeBook,
) -> StudentScore:
```

### 역할

가장 높은 점수를 받은 학생 한 명을 반환한다.

### 반환 예시

```python
("이서연", 92.0)
```

### 동점자 처리

최고 점수가 같은 학생이 여러 명이면 딕셔너리의 등록 순서에 따라 먼저 등록된 학생을 반환한다.

### 예외

성적부가 비어 있으면 `EmptyGradeBookError`를 발생시킨다.

---

## 6. `format_student_list`

```python
def format_student_list(
    students: list[StudentScore],
) -> str:
```

### 역할

학생 목록을 표시용 문자열로 변환한다.

### 반환 예시

```text
김민수: 85점
이서연: 92점
```

---

## 7. `format_average`

```python
def format_average(
    average: float,
) -> str:
```

### 역할

평균 점수를 표시용 문자열로 변환한다.

### 반환 예시

```text
평균 점수: 88.5점
```

---

## 8. `format_top_student`

```python
def format_top_student(
    student: StudentScore,
) -> str:
```

### 역할

최고 점수 학생 정보를 표시용 문자열로 변환한다.

### 반환 예시

```text
최고 점수 학생: 이서연, 92점
```

---

# 프로그램 흐름

## 전체 흐름

1. `create_grade_book()`으로 빈 성적부를 생성한다.
2. `register_student()`에 이름과 점수를 전달한다.
3. 반환된 새로운 성적부를 다음 작업에 사용한다.
4. `list_students()`로 전체 목록을 조회한다.
5. `calculate_average()`로 평균을 계산한다.
6. `find_top_student()`로 최고 점수 학생을 조회한다.
7. 필요할 경우 `format_*()` 함수로 결과를 문자열로 변환한다.
8. 실제 화면 출력이나 웹 응답은 호출 측에서 처리한다.

## 사용 예시

```python
grade_book = create_grade_book()

grade_book = register_student(grade_book, "김민수", 85)
grade_book = register_student(grade_book, "이서연", 92)

students = list_students(grade_book)
average = calculate_average(grade_book)
top_student = find_top_student(grade_book)

print(format_student_list(students))
print(format_average(average))
print(format_top_student(top_student))
```

실행 결과:

```text
김민수: 85점
이서연: 92점
평균 점수: 88.5점
최고 점수 학생: 이서연, 92점
```

## 함수형 API 사용 방식

`register_student()`는 기존 딕셔너리를 직접 수정하지 않고 새로운 딕셔너리를 반환한다.

```python
original = create_grade_book()
updated = register_student(original, "김민수", 85)

assert original == {}
assert updated == {"김민수": 85.0}
```

---

# 예외 처리 요구사항

## 예외 종류

| 상황 | 예외 |
|---|---|
| 이름이 문자열이 아님 | `TypeError` |
| 이름이 빈 문자열임 | `ValueError` |
| 점수가 숫자가 아님 | `TypeError` |
| 점수가 `0~100` 범위를 벗어남 | `ValueError` |
| 동일한 이름을 중복 등록함 | `DuplicateStudentError` |
| 등록된 학생이 없음 | `EmptyGradeBookError` |
| 성적부 자료형이 잘못됨 | `TypeError` |

## 구현 코드

```python
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
    """
    빈 성적부를 생성한다.
    """
    return {}


def _validate_grade_book(grade_book: GradeBook) -> None:
    """
    성적부의 기본 자료형을 검증한다.
    """
    if not isinstance(grade_book, dict):
        raise TypeError("성적부는 dict 자료형이어야 합니다.")

    for name, score in grade_book.items():
        if not isinstance(name, str):
            raise TypeError("학생 이름은 문자열이어야 합니다.")

        if not isinstance(score, (int, float)) or isinstance(score, bool):
            raise TypeError("점수는 숫자여야 합니다.")


def _validate_student_name(name: str) -> str:
    """
    학생 이름을 검증하고 앞뒤 공백을 제거한 이름을 반환한다.
    """
    if not isinstance(name, str):
        raise TypeError("학생 이름은 문자열이어야 합니다.")

    normalized_name = name.strip()

    if not normalized_name:
        raise ValueError("학생 이름은 비어 있을 수 없습니다.")

    return normalized_name


def _validate_score(score: int | float) -> float:
    """
    점수를 검증하고 float으로 변환하여 반환한다.
    """
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        raise TypeError("점수는 숫자여야 합니다.")

    if not 0 <= score <= 100:
        raise ValueError("점수는 0점 이상 100점 이하이어야 합니다.")

    return float(score)


def _ensure_not_empty(grade_book: GradeBook) -> None:
    """
    성적부가 비어 있지 않은지 검사한다.
    """
    if not grade_book:
        raise EmptyGradeBookError("등록된 학생이 없습니다.")


def register_student(
    grade_book: GradeBook,
    name: str,
    score: int | float,
) -> GradeBook:
    """
    학생 이름과 점수를 등록한 새로운 성적부를 반환한다.
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


def list_students(
    grade_book: GradeBook,
) -> list[StudentScore]:
    """
    전체 학생 목록을 등록 순서대로 반환한다.
    """
    _validate_grade_book(grade_book)
    _ensure_not_empty(grade_book)

    return list(grade_book.items())


def calculate_average(
    grade_book: GradeBook,
) -> float:
    """
    전체 학생의 평균 점수를 반환한다.
    """
    _validate_grade_book(grade_book)
    _ensure_not_empty(grade_book)

    return sum(grade_book.values()) / len(grade_book)


def find_top_student(
    grade_book: GradeBook,
) -> StudentScore:
    """
    최고 점수 학생의 이름과 점수를 반환한다.

    최고 점수가 같은 경우 등록 순서상 먼저 등록된 학생을 반환한다.
    """
    _validate_grade_book(grade_book)
    _ensure_not_empty(grade_book)

    return max(grade_book.items(), key=lambda item: item[1])


def format_student_list(
    students: list[StudentScore],
) -> str:
    """
    학생 목록을 표시용 문자열로 변환한다.
    """
    if not students:
        raise EmptyGradeBookError("등록된 학생이 없습니다.")

    return "\n".join(
        f"{name}: {_format_score(score)}점"
        for name, score in students
    )


def format_average(
    average: float,
) -> str:
    """
    평균 점수를 표시용 문자열로 변환한다.
    """
    return f"평균 점수: {_format_score(average)}점"


def format_top_student(
    student: StudentScore,
) -> str:
    """
    최고 점수 학생 정보를 표시용 문자열로 변환한다.
    """
    name, score = student
    return f"최고 점수 학생: {name}, {_format_score(score)}점"


def _format_score(score: float) -> str:
    """
    정수 점수는 소수점 없이, 실수 점수는 필요한 만큼 표시한다.
    """
    if score.is_integer():
        return str(int(score))

    return f"{score:g}"
```

## 예외 처리 사용 예시

```python
try:
    grade_book = create_grade_book()
    grade_book = register_student(grade_book, "김민수", 85)
    grade_book = register_student(grade_book, "김민수", 90)
except DuplicateStudentError as error:
    message = str(error)
```

`message`의 값:

```text
'김민수' 학생은 이미 등록되어 있습니다.
```

빈 성적부 조회 예시:

```python
try:
    empty_grade_book = create_grade_book()
    average = calculate_average(empty_grade_book)
except EmptyGradeBookError as error:
    message = str(error)
```

`message`의 값:

```text
등록된 학생이 없습니다.
```

이 설계는 Python 표준 라이브러리만 사용하며, 입력 대기나 직접적인 콘솔 출력 없이 다른 프로그램, 웹 API, 테스트 코드에서 함수 호출 방식으로 사용할 수 있다.