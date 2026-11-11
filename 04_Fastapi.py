# /meeting
# /summarize
# 버튼을 누르면 이 두개의 값을 fastapi에서 받아와 json 형식으로 출력
# 서버 만들기
# pip install fastapi uvicorn
# uvicorn 4_Fastapi:app --reload --port 8000
# post/pipeline 탭3 데이터를 받음 > 4_graph.py로 보내기

from fastapi import FastAPI  # pip install fastapi
from pydantic import BaseModel
from graph_04 import run_meeting_pipeline # 숫자가 먼저 오면 안되니깐 04를 뒤로 올림

app = FastAPI(title="회의 관리 API")

class MeetingRequest(BaseModel):
    title: str
    people: str

class Summaryrequest(BaseModel):
    text: str

class PipelineRequest(BaseModel):
    title: str
    people: str
    notes: str

def make_meeting(title: str, people: str) -> str:
    title = (title or "").strip()
    if not title:
        return "제목을 입력하세요"
    names = [p.strip() for p in (people or "").split(",") if p.strip()]
    return (f"### 회의 생성됨\n"
            f"- 제목: {title}\n"
            f"- 참가자: {','.join(names) or '(없음)'}")

def summarize(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "회의록이 비어 있습니다."
    lines = [ln for ln in text.splitlines() if ln.strip()]
    return f"발화 {len(lines)}줄 / 앞부분: {lines[0][:50] if lines else ''}"

@app.post("/meeting")
def create_meeting(request: MeetingRequest):
    return {"result": make_meeting(request.title, request.people)}

@app.post("/summarize")
def summarize_meeting(request: Summaryrequest):
    return {"result": summarize(request.text)}

@app.post("/pipeline")
def run_pipeline(request: PipelineRequest):
    return {
        "result": run_meeting_pipeline(
            title = request.title,
            people = request.people,
            notes = request.notes
        )
    }
