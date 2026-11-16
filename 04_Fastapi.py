# /meeting
# /summarize
# 버튼을 누르면 이 두개의 값을 fastapi에서 받아와 json 형식으로 출력
# 서버 만들기
# pip install fastapi uvicorn
# uvicorn 04_Fastapi:app --reload --port 8000
# post/pipeline 탭3 데이터를 받음 > graph_04.py로 보내기

# 이 경로에 임시 폴더가 생성되는데 오류나면 임시 폴더 삭제하고 다시 진행
# C:\Users\Administrator\AppData\Local\Temp\gradio 


import uuid
import shutil # 파일을 다루는 메서드
from pathlib import Path
from contextlib import asynccontextmanager  # fastapi에서 데코레이터 달라고 하는 거임
from fastapi import FastAPI, HTTPException, UploadFile, File, Form # pip install fastapi
from pydantic import BaseModel
from graph_04 import run_meeting_pipeline # 숫자가 먼저 오면 안되니깐 04를 뒤로 올림
from db import (init_db, list_meetings, format_meetings_markdown, get_meeting)
from asr import asr_status, transcribe_file # 11.16

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@asynccontextmanager
# Fastapi가 뜨기 전에 이것부터 시작
async def lifespan(_app: FastAPI): # 서버가 시작될 때 이 처리를 하고 서버를 시작하라는 의미
    # 데이터베이스 처리
    init_db()
    yield


app = FastAPI(title="회의 관리 API", lifespan=lifespan)

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


def _save_upload(file: UploadFile) -> Path:
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}" # uuid: unique 값 추출
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    return dest


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

@app.get("/meetings")
def meetings_list(limit: int=20):
    rows = list_meetings(limit=limit)
    return{
        "items": rows,
        "markdown": format_meetings_markdown(rows),
        "result": format_meetings_markdown(rows)
    }


@app.get("/meetings/{meeting_id}")
def meetings_detail(meeting_id: int):
    row = get_meeting(meeting_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"회의 #{meeting_id} 없음")
    detail = format_meetings_markdown(row)
    return {"item": row, "markdown": detail, "result": detail}

@app.get("/asr/status")
def get_asr_status():
    return asr_status()



# 전사
@app.post("/transcribe")
async def transcribe_only(file: UploadFile = File(...)):   # 11.16
    path = _save_upload(file)
    try:
        tr = transcribe_file(path) # import 해서 사용 <- asr 파일에 추가
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "text": tr.text,
        "mode": tr.mode,
        "rms": tr.rms,
        "peak": tr.peak,
        "skipped_silence": tr.skipped_silence,
        "detail": tr.detail,
        "result": (
            f"### 전사 결과\n\n"
            f"- 모드: `{tr.mode}`\n"
            f"- RMS: `{tr.rms:.4f}` / peak: `{tr.peak:.4f}`\n"
            f"- {tr.detail}\n\n"
            f"```\n{tr.text or '(빈 결과)'}\n```"
        ),
        "markdown": (
            f"### 전사 결과\n\n"
            f"- 모드: `{tr.mode}`\n"
            f"- RMS: `{tr.rms:.4f}` / peak: `{tr.peak:.4f}`\n"
            f"- {tr.detail}\n\n"
            f"```\n{tr.text or '(빈 결과)'}\n```"
        ),
    }


# DB 저장 및 랭그래프 통과시키기
@app.post("/pipeline_audio")   # 11.16
async def run_pipeline_audio(
    title: str = Form(...),
    people: str = Form(""),
    file: UploadFile = File(...)
):
    path = _save_upload(file)

    try:
        tr = transcribe_file(path)
        if not tr.text.strip():
            raise HTTPException(
                status_code=400, detail="음성 인식 결과없음"
            )
        result = run_meeting_pipeline(
                    title=title,
                    people=people,
                    notes=tr.text,
                    audio_path=str(path)
        )
        result["transcript"] = tr.text
        result["asr_mode"] = tr.mode
        result["audio_rms"] = tr.rms
        result["audio_peak"] = tr.peak

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="음성 파이프라인 처리 오류"
        )

