import os
import numpy as np
import torch
import qwen_asr
from qwen_asr import Qwen3ASRModel
# 관련 정보를 하나의 객체로 묶어 관리
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

TARGET_SR = 16000
ASR_MODE_ENV = os.getenv("ASR_MODE", "auto").strip().lower()
ASR_MODEL_PATH = os.getenv("ASR_MODEL_PATH", "Qwen/Qwen3-ASR-1.7B")
ASR_LANGUAGE = os.getenv("ASR_LANGUAGE", "Korean")
MAX_SECONDS = float(os.getenv("ASR_MAX_SECONDS", 20))
SILENCE_RMS = float(os.getenv("ASR_SILENCE_RMS", "0.01"))

MOCK_TRANSCRIPT = (
    "김사과: 이번주 목표 공유\n"
    "이메론: API 완료 예정\n"
    "김사과: 문서화는 반하나가 담당\n"
    "반하나: 그럼 김사과가 README 작성해야함"
)

_MODEL = None

# 형식을 지정하기 위해서
@dataclass
class AudioFeatures: 
    wav: np.ndarray             # 음성 파일 > 음성 샘플 배열
    sample_rate: int            # 샘플링 레이트
    rms: float                  # 음성 신호의 전반적인 (평균적인) 크기 / root mean square. 왜 저장? 정규화된 음성 샘플을 기준으로 음성 파형을 비교하기 위해서 / (활용) 실제로 신호가 들어오면 평균과 비교해서 크기를 비교해보려고z
    peak: float                 # 음성 신호에서 절대값이 가장 큰 샘플의 크기 / (활용) 범위를 찾으려고
    skipped_silence: bool       # 무음으로 판단하여 음성 인식을 건너뛰었는지 여부를 저장
    path: str                   # 음성 파일의 경로

# 결과론적
@dataclass
class TranscriptResult:
    text: str                   # 인식된 음성 텍스트
    mode: str                   # 사용된 인식 방식
    rms: float                  # 입력 음성의 RMS
    peak: float                 # 입력 음성의 Peak(절댓값 가장 큰거)
    skipped_silence: bool       # 무음으로 인한 인식 생략 여부
    detail: SyntaxWarning       # 처리 과정에 대한 추가 설명

def resolve_asr_mode() -> str:
    if ASR_MODE_ENV in {"qwen", "mock"}:
        return ASR_MODE_ENV
    try:
        if torch.cuda.is_available():
            return "qwen"
    except Exception:
        pass
    return "mock"

def asr_status() -> dict:
    mode = resolve_asr_mode()
    cuda = False
    qwen = False
    try:
        cuda = bool(torch.cuda.is_available())
    except Exception:
        cuda = False
    try:
        qwen = True
    except Exception:
        qwen = False
    return {
        "mode": mode,
        "requested": ASR_MODE_ENV,
        "cuda": cuda,
        "qwen_asr_installed": qwen,
        "model_path": ASR_MODEL_PATH,
        "silence_rms": SILENCE_RMS,
        "max_seconds": MAX_SECONDS,
        "markdown": (
            f"### ASR 상태\n\n"
            f"- 사용 모드: {mode}\n"
            f"- 요청 모드: {ASR_MODE_ENV}\n"
            f"- CUDA: {cuda}\n"
            f"- qwen_asr: {qwen}\n"
            f"- 모델: {ASR_MODEL_PATH}\n"
            f"- 무음 RMS 임계값: {SILENCE_RMS}\n\n"
        )
    }