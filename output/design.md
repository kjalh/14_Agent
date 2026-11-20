# 프로젝트 목적

학생의 이름과 점수를 등록하고, 등록된 성적 데이터를 기반으로 다음 기능을 제공하는 함수형 성적 관리 프로그램을 설계한다.

- 학생 등록
- 전체 학생 목록 조회
- 전체 학생 평균 점수 계산
- 최고 점수 학생 조회

프로그램은 `input()`이나 대화형 입력을 사용하지 않는다. 모든 기능은 함수 호출을 통해 데이터를 전달받고 결과를 반환하는 형태로 구성한다.

점수는 **0점 이상 100점 이하**로 제한하며, 최고 점수 학생이 여러 명이면 모두 반환한다.

---

# 필수 기능 목록

1. **성적 관리 객체 생성**
   - 빈 성적 관리 객체를 생성한다.

2. **학생 등록**
   - 학생 이름과 점수를 등록한다.
   - 이름은 공백을 제거한 뒤 저장한다.
   - 점수는 0 이상 100 이하만 허용한다.
   - 동일한 이름의 학생은 중복 등록하지 않는다.
   - 기존 객체를 변경하지 않고 새로운 객체를 반환한다.

3. **전체 학생 목록 조회**
   - 등록 순서대로 모든 학생을 반환한다.
   - 등록된 학생이 없으면 빈 튜플을 반환한다.

4. **평균 점수 계산**
   - 전체 학생의 평균 점수를 반환한다.
   - 학생이 없으면 `None`을 반환한다.

5. **최고 점수 학생 조회**
   - 최고 점수 학생을 모두 반환한다.
   - 동점자가 있으면 등록 순서를 유지한 채 모두 반환한다.
   - 학생이 없으면 빈 튜플을 반환한다.

---

# 자료구조

## `Student`

학생 한 명의 이름과 점수를 표현하는 불변 데이터 클래스이다.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Student:
    name: str
    score: float
```

## `GradeBook`

등록된 학생 전체를 표현하는 불변 데이터 클래스이다.

```python
@dataclass(frozen=True)
class GradeBook:
    students: tuple[Student, ...] = ()
```

### 자료구조 선택 이유

- `Student`
  - 이름과 점수를 하나의 의미 있는 객체로 관리할 수 있다.
  - `frozen=True`를 사용하여 등록된 학생 데이터가 임의로 변경되지 않도록 한다.

- `GradeBook`
  - 학생 목록을 튜플로 저장하여 불변성을 유지한다.
  - 학생 등록 시 기존 튜플을 수정하지 않고 새로운 `GradeBook` 객체를 생성한다.
  - 학생 등록 순서를 보존한다.

---

# 함수 목록과 함수별 역할

## 1. `create_gradebook`

```python
def create_gradebook() -> GradeBook:
    """빈 성적 관리 객체를 생성한다."""
```

### 역할

- 새로운 빈 `GradeBook` 객체를 반환한다.

---

## 2. `register_student`

```python
def register_student(
    gradebook: GradeBook,
    name: str,
    score: int | float,
) -> GradeBook:
    """학생을 등록한 새로운 GradeBook 객체를 반환한다."""
```

### 역할

- 학생 이름과 점수를 검증한다.
- 중복 이름 여부를 확인한다.
- 유효한 학생을 등록한 새로운 `GradeBook` 객체를 반환한다.
- 기존 `GradeBook` 객체는 변경하지 않는다.

---

## 3. `list_students`

```python
def list_students(
    gradebook: GradeBook,
) -> tuple[Student, ...]:
    """등록된 전체 학생 목록을 반환한다."""
```

### 역할

- 등록 순서대로 학생 전체 목록을 반환한다.
- 학생이 없으면 빈 튜플을 반환한다.

---

## 4. `average_score`

```python
def average_score(
    gradebook: GradeBook,
) -> float | None:
    """전체 학생의 평균 점수를 반환한다."""
```

### 역할

- 등록된 모든 학생의 평균 점수를 계산한다.
- 등록된 학생이 없으면 `None`을 반환한다.

---

## 5. `top_students`

```python
def top_students(
    gradebook: GradeBook,
) -> tuple[Student, ...]:
    """최고 점수를 받은 학생 전체를 반환한다."""
```

### 역할

- 가장 높은 점수를 계산한다.
- 최고 점수와 동일한 학생을 모두 반환한다.
- 동점자는 등록 순서를 유지한다.
- 등록된 학생이 없으면 빈 튜플을 반환한다.

---

# 구현 코드

```python
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real


MIN_SCORE = 0.0
MAX_SCORE = 100.0


@dataclass(frozen=True)
class Student:
    """학생 한 명의 이름과 점수."""

    name: str
    score: float


@dataclass(frozen=True)
class GradeBook:
    """등록된 학생 목록."""

    students: tuple[Student, ...] = ()


def create_gradebook() -> GradeBook:
    """
    빈 성적 관리 객체를 생성한다.

    Returns:
        GradeBook: 학생이 등록되지 않은 빈 성적 관리 객체
    """
    return GradeBook()


def register_student(
    gradebook: GradeBook,
    name: str,
    score: int | float,
) -> GradeBook:
    """
    학생을 등록한 새로운 GradeBook 객체를 반환한다.

    Args:
        gradebook: 기존 성적 관리 객체
        name: 학생 이름
        score: 학생 점수. 0 이상 100 이하의 숫자

    Returns:
        GradeBook: 학생이 추가된 새로운 성적 관리 객체

    Raises:
        TypeError:
            gradebook이 GradeBook이 아니거나,
            name이 문자열이 아니거나,
            score가 숫자가 아닌 경우
        ValueError:
            이름이 비어 있거나, 점수 범위를 벗어나거나,
            동일한 이름이 이미 등록된 경우
    """
    if not isinstance(gradebook, GradeBook):
        raise TypeError("gradebook은 GradeBook 객체여야 합니다.")

    if not isinstance(name, str):
        raise TypeError("학생 이름은 문자열이어야 합니다.")

    normalized_name = name.strip()

    if not normalized_name:
        raise ValueError("학생 이름은 비어 있을 수 없습니다.")

    if isinstance(score, bool) or not isinstance(score, Real):
        raise TypeError("점수는 숫자여야 합니다.")

    normalized_score = float(score)

    if not isfinite(normalized_score):
        raise ValueError("점수는 유한한 숫자여야 합니다.")

    if not MIN_SCORE <= normalized_score <= MAX_SCORE:
        raise ValueError(
            f"점수는 {MIN_SCORE:g}점 이상 {MAX_SCORE:g}점 이하여야 합니다."
        )

    if any(student.name == normalized_name for student in gradebook.students):
        raise ValueError(
            f"이미 등록된 학생 이름입니다: {normalized_name}"
        )

    new_student = Student(
        name=normalized_name,
        score=normalized_score,
    )

    return GradeBook(
        students=gradebook.students + (new_student,)
    )


def list_students(
    gradebook: GradeBook,
) -> tuple[Student, ...]:
    """
    등록된 전체 학생 목록을 반환한다.

    Args:
        gradebook: 성적 관리 객체

    Returns:
        tuple[Student, ...]: 등록 순서대로 정렬된 학생 목록

    Raises:
        TypeError: gradebook이 GradeBook 객체가 아닌 경우
    """
    if not isinstance(gradebook, GradeBook):
        raise TypeError("gradebook은 GradeBook 객체여야 합니다.")

    return gradebook.students


def average_score(
    gradebook: GradeBook,
) -> float | None:
    """
    전체 학생의 평균 점수를 반환한다.

    Args:
        gradebook: 성적 관리 객체

    Returns:
        float | None:
            학생이 있으면 평균 점수,
            학생이 없으면 None

    Raises:
        TypeError: gradebook이 GradeBook 객체가 아닌 경우
    """
    if not isinstance(gradebook, GradeBook):
        raise TypeError("gradebook은 GradeBook 객체여야 합니다.")

    if not gradebook.students:
        return None

    total_score = sum(student.score for student in gradebook.students)

    return total_score / len(gradebook.students)


def top_students(
    gradebook: GradeBook,
) -> tuple[Student, ...]:
    """
    최고 점수를 받은 학생 전체를 반환한다.

    Args:
        gradebook: 성적 관리 객체

    Returns:
        tuple[Student, ...]:
            최고 점수 학생 목록.
            동점자는 모두 반환하며 등록 순서를 유지한다.
            학생이 없으면 빈 튜플

    Raises:
        TypeError: gradebook이 GradeBook 객체가 아닌 경우
    """
    if not isinstance(gradebook, GradeBook):
        raise TypeError("gradebook은 GradeBook 객체여야 합니다.")

    if not gradebook.students:
        return ()

    highest_score = max(
        student.score for student in gradebook.students
    )

    return tuple(
        student
        for student in gradebook.students
        if student.score == highest_score
    )
```

---

# 프로그램 흐름

함수형 API에서는 다음과 같이 사용할 수 있다.

```python
gradebook = create_gradebook()

gradebook = register_student(gradebook, "김민수", 85)
gradebook = register_student(gradebook, "이서연", 92)
gradebook = register_student(gradebook, "박지훈", 92)

students = list_students(gradebook)
average = average_score(gradebook)
best_students = top_students(gradebook)
```

각 결과는 다음과 같이 확인할 수 있다.

```python
print(students)
# (
#     Student(name='김민수', score=85.0),
#     Student(name='이서연', score=92.0),
#     Student(name='박지훈', score=92.0)
# )

print(average)
# 89.66666666666667

print(best_students)
# (
#     Student(name='이서연', score=92.0),
#     Student(name='박지훈', score=92.0)
# )
```

전체 흐름은 다음과 같다.

1. `create_gradebook()`으로 빈 성적 관리 객체를 생성한다.
2. `register_student()`를 호출하여 학생을 등록한다.
3. 반환된 새로운 `GradeBook` 객체를 다시 저장한다.
4. `list_students()`로 전체 학생을 조회한다.
5. `average_score()`로 평균 점수를 계산한다.
6. `top_students()`로 최고 점수 학생을 조회한다.

`GradeBook`은 불변 객체이므로 다음과 같이 반드시 반환값을 다시 저장해야 한다.

```python
gradebook = register_student(gradebook, "김민수", 85)
```

다음과 같이 호출하면 등록 결과가 반영되지 않는다.

```python
register_student(gradebook, "김민수", 85)
```

---

# 예외 처리 요구사항

## 1. 학생 이름이 문자열이 아닌 경우

```python
register_student(gradebook, 123, 80)
```

처리 결과:

```python
TypeError
```

## 2. 학생 이름이 비어 있는 경우

```python
register_student(gradebook, "   ", 80)
```

처리 결과:

```python
ValueError
```

이름 앞뒤의 공백은 제거하며, 제거 후 빈 문자열이면 등록하지 않는다.

## 3. 점수가 숫자가 아닌 경우

```python
register_student(gradebook, "김민수", "80")
```

처리 결과:

```python
TypeError
```

함수형 API에서는 문자열을 자동 변환하지 않고, 호출자가 `int` 또는 `float` 값을 전달해야 한다.

## 4. 점수가 허용 범위를 벗어나는 경우

허용 범위는 0점 이상 100점 이하이다.

```python
register_student(gradebook, "김민수", -1)
register_student(gradebook, "김민수", 101)
```

처리 결과:

```python
ValueError
```

## 5. 무한대 또는 `NaN` 점수

```python
register_student(gradebook, "김민수", float("nan"))
register_student(gradebook, "김민수", float("inf"))
```

처리 결과:

```python
ValueError
```

## 6. 동일한 학생 이름을 중복 등록하는 경우

```python
gradebook = register_student(gradebook, "김민수", 80)
gradebook = register_student(gradebook, "김민수", 90)
```

처리 결과:

```python
ValueError
```

현재 정책에서는 학생 이름을 고유 식별자로 사용하므로 동일한 이름을 중복 등록하지 않는다.

## 7. 등록된 학생이 없는 경우

### 평균 점수

```python
empty_gradebook = create_gradebook()

result = average_score(empty_gradebook)
print(result)
```

결과:

```python
None
```

### 최고 점수 학생

```python
result = top_students(empty_gradebook)
print(result)
```

결과:

```python
()
```

### 전체 학생 목록

```python
result = list_students(empty_gradebook)
print(result)
```

결과:

```python
()
```

이 설계는 입력 대기 없이 함수 호출과 반환값만으로 동작하며, Python 표준 라이브러리만 사용한다.