import os
import numpy as np
import torch
import qwen_asr
from qwen_asr import Qwen3ASRModel
# 관련 정보를 하나의 객체로 묶어 관리
from dataclasses import dataclass
from dotenv import load_dotenv

from pathlib import Path  # 11.16

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

_model = None  # 11.16  대->소



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

def load_audio_file(path: str | Path) -> tuple[np.ndarray, int]: # 11.16
    path = Path(path)

    if not path.is_file():
        raise FileNotFoundError(f"음성 파일 없음: {path}")

    try:
        import soundfile as sf
    except ImportError as e:
        raise ImportError("soundfile 모듈 에러!") from e

    # 5초짜리 44100hz라면 wav.shape는 5*44100=22500
    # always_2d=True: 모노 또는 스테레오 관계없이 항상 스테레오(2차원 배열)로 반환
    wav, sr = sf.read(str(path), dtype = "float32", always_2d=True)
    wav = wav.mean(axis=1)

    if sr != TARGET_SR:
        # len(wav): 음성 샘플 수
        duration = len(wav) / sr  # 음성 길이
        new_len = max(1, int(round(duration * TARGET_SR)))
        
        # interp(새로운 x값, 기존 x값, 기존 y값): 기존 데이터 사이의 값을 선형 보간으로 계산하는 함수
        # 보간: OpenCV에서 이미지 resize할 때 어떻게 픽셀을 채워 넣을거냐
        # linspace(시작값, 끝값, 생성할 숫자 개수, endpoint=끝값 포함 여부): 지정한 범위에서 일정한 간격으로 숫자를 생성하는 함수

        # interp: 1차원 선형 보간(OpenCV에서 interpolration). 기존에 측정한 샘플 사이의 값을 직선으로 연결하여 새로운 위치의 값을 추정   
        # 시간 0초의 음성 진폭: 0.2
        # 시간 1초의 음성 진폭: 0.8
        # 0.5초 지점의 진폭은 얼마? y = 0.2 + (0.8 - 0.2) * 0.5 = 0.5
        # interp(새롭게 값을 구하려는 위치, 기존 데이터의 위치, 기존 위치에 해당하는 실제 값)
        # linspace: 지정한 구간에 일정한 간격으로 숫자를 생성
        # linspace(0, 1, 4) > [0, 0.25, 0.5, 0.75]. endpoint=False 마지막 값 생략 
        # 기존 시간과 진폭을 참고하여 새로운 시간 좌표에서 진폭을 계산
        wav = np.interp(
            np.linspace(0, duration, new_len, endpoint=False), np.arange(len(wav)) / sr, wav
            ).astype(np.float32)
        sr = TARGET_SR

    # 당연히 0보다 크지만 확인
    if MAX_SECONDS > 0:
        wav = wav[: int(MAX_SECONDS * TARGET_SR)]

    return wav.astype(np.float32), sr


def compute_rms(wav: np.ndarray) -> float:  # 11.16
    if wav.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(wav**2)))
        

def peak_normalize(wav: np.ndarray, target: float = 0.9) -> np.ndarray:  # 11.16
    peak = float(np.max(np.abs(wav))) if wav.size else 0.0

    if 1e-6 <= peak < target:
        return (wav * (target / peak)).astype(np.float32)
    
    return wav.astype(np.float32)


# RMS: 음성 신호의 평균적인 크기를 측정
# Peak: 음성 신호에서 가장 큰 진폭을 측정
# Peak Normalization: 가장 큰 진폭을 기준으로 음성 전체의 크기를 조절
# 같은 사람이 같은 문장을 녹음하더라도 녹음 환경에 따라 음성 신호의 크기가 달라짐 -> 정규화
def preprocess_audio_file(path: str | Path) -> AudioFeatures:  # 11.16
    wav, sr = load_audio_file(path)
    rms = compute_rms(wav)
    peak = float(np.max(np.abs(wav))) if wav.size else 0.0
    skipped = rms < SILENCE_RMS

    if not skipped:
        wav = peak_normalize(wav)
        peak = float(np.max(np.abs(wav))) if wav.size else 0.0
        rms = compute_rms(wav)

    return AudioFeatures(
        wav=wav,
        sample_rate=sr,
        rms=rms,
        peak=peak,
        skipped_silence=skipped,
        path=str(path)
    )


# def _get_qwen_model():  #  11.16
#     global _model
#     if _model is not None:
#         return _model
#     if not torch.cuda.is_available():
#         raise RuntimeError("GPU 필요!")
#     dtype = (torch.float16 if os.getenv("ASR_DTYPE", "bfloat16").lower() == "float16" else torch.bfloat16)
#     _model = Qwen3ASRModel.from_pretrained(
#         ASR_MODEL_PATH, dtype=dtype, device_map="cuda", max_inference_batch_size=1, max_new_tokens=256
#     )
#     return _model


# gpu 없을 때 
def _get_qwen_model():  # 11.16
    global _model
    if _model is not None:
        return _model

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float32
    if device == "cuda":
        dtype = (
            torch.float16
            if os.getenv("ASR_DTYPE", "bfloat16").lower() == "float16"
            else torch.bfloat16
        )

    _model = Qwen3ASRModel.from_pretrained(
        ASR_MODEL_PATH,
        dtype=dtype,
        device_map=device,
        max_inference_batch_size=1,
        max_new_tokens=256,
    )
    return _model


def transcribe_features(features: AudioFeatures, mode: str | None = None) -> TranscriptResult:  # 11.16
    mode = mode or resolve_asr_mode()
    if features.skipped_silence:
        return TranscriptResult(
            text="",
            mode=mode,
            rms=features.rms,
            peak=features.peak,
            skipped_silence=True,
            detail=f"무음으로 건너뜀 (RMS={features.rms:.4f} < {SILENCE_RMS})"
        )
    
    if mode == "qwen":
        model = _get_qwen_model()
        result = model.transcribe(audio=(features.wav, features.sample_rate), language=ASR_LANGUAGE)
        text = (getattr(result[0], "text", "") or "").strip()

        return TranscriptResult(
            text=text,
            mode="qwen",
            rms=features.rms,
            peak=features.peak,
            skipped_silence=False,
            detail="Qwen3-ASR 실전사"
        )
    
    return TranscriptResult(
        text=MOCK_TRANSCRIPT,
        mode="mock",
        rms=features.rms,
        peak=features.peak,
        skipped_silence=False,
        detail=f"mock 전사"
    )
        


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

def transcribe_file(path: str | Path) -> TranscriptResult:  # 11.16
    features = preprocess_audio_file(path)
    return transcribe_features(features)