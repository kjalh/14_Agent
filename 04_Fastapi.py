# /meeting
# /summarize
# 버튼을 누르면 이 두개의 값을 fastapi에서 받아와 json 형식으로 출력
# 서버 만들기
# pip install fastapi uvicorn
# uvicorn 4_Fastapi:app --reload --port 8000
# post/pipeline 탭3 데이터를 받음 > 4_graph.py로 보내기

from fastapi import FastAPI
from pydantic import BaseModel

# 회의 관리 API 앱을 만듭니다.
app = FastAPI(title="회의 관리 API")

# 회의 생성 요청에 필요한 데이터를 정의합니다.
class MeetingRequest(BaseModel):
    title: str
    # title: str은 title이 필수 문자열이라는 뜻입니다.
    people: str
    # people은 쉼표로 구분한 참가자 이름을 담는 문자열입니다.

# 회의록 요약 요청에 필요한 데이터를 정의합니다.
class Summaryrequest(BaseModel):
    text: str
    # text는 회의록 내용을 담는 필수 문자열입니다.

# 매개변수의 : str은 문자열을 받는다는 뜻이고, -> str은 문자열을 반환한다는 뜻입니다.
def make_meeting(title: str, people: str) -> str:
    # 제목 앞뒤의 공백을 제거합니다.
    title = (title or "").strip()
    if not title:
        return "제목을 입력하세요"
    # 참가자 이름을 쉼표로 나누고 빈 값은 제외합니다.
    names = [p.strip() for p in (people or "").split(",") if p.strip()]
    # 회의 제목과 참가자를 문자열로 만들어 반환합니다.
    return (f"### 회의 생성됨\n"
            f"- 제목: {title}\n"
            f"- 참가자: {','.join(names) or '(없음)'}")

# 회의록의 줄 수와 첫 줄의 앞부분을 반환합니다.
def summarize(text:str) -> str:
    # 회의록 앞뒤의 공백을 제거합니다.
    text = (text or "").strip()
    if not text:
        return "회의록이 비어 있습니다."
    # 내용이 있는 줄만 모읍니다.
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return f"발화 {len(lines)}줄 / 앞부분: {lines[0][:50] if lines else ""}"

# POST /meeting 요청을 처리합니다.
@app.post("/meeting")
def create_meeting(request: MeetingRequest):
    return {'result': make_meeting(request.title, request.people)}

# POST /summarize 요청을 처리합니다.
@app.post("/summarize")
def summarize_meeting(request: Summaryrequest):
    return {'result': summarize(request.text)}