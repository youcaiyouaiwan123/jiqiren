"""语音转文字服务：使用 faster-whisper 本地推理"""
import asyncio
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

_model = None
_model_lock = asyncio.Lock()

# 使用 medium 模型，中文准确率显著优于 small，CPU 推理 5-10 秒
MODEL_SIZE = "medium"


def _sanitize_sslkeylogfile_env() -> None:
    """避免无权限的 SSLKEYLOGFILE 影响 requests/urllib3 初始化。"""
    sslkeylogfile = os.environ.get("SSLKEYLOGFILE")
    if not sslkeylogfile:
        return

    try:
        with Path(sslkeylogfile).expanduser().open("a", encoding="utf-8"):
            pass
    except OSError as exc:
        os.environ.pop("SSLKEYLOGFILE", None)
        logger.warning(
            "[STT] SSLKEYLOGFILE 不可用，已在当前进程禁用 TLS key logging | path=%s | error=%s",
            sslkeylogfile,
            exc,
        )


def _load_model():
    """同步加载 faster-whisper 模型（首次调用时下载，约 500MB）"""
    global _model
    if _model is not None:
        return _model
    try:
        _sanitize_sslkeylogfile_env()
        from faster_whisper import WhisperModel
        logger.info("[STT] 正在加载 faster-whisper 模型: %s ...", MODEL_SIZE)
        _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        logger.info("[STT] 模型加载完成")
        return _model
    except ImportError:
        logger.error("[STT] faster-whisper 未安装，请执行: pip install faster-whisper")
        raise RuntimeError("faster-whisper 未安装")
    except Exception as exc:
        logger.exception("[STT] 模型加载失败")
        raise RuntimeError(f"STT 模型加载失败: {exc}")


def _transcribe_sync(audio_path: str) -> str:
    """同步转写音频文件，返回识别文本"""
    model = _load_model()
    segments, info = model.transcribe(
        audio_path,
        language="zh",
        beam_size=8,
        best_of=3,
        temperature=[0.0, 0.2, 0.4, 0.6],
        condition_on_previous_text=True,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=300,
            speech_pad_ms=200,
        ),
        initial_prompt=(
            "以下是一段中文智能客服系统的语音转录。"
            "涉及账号登录、套餐会员、退款售后、密码修改等话题。"
            "请使用简体中文标点符号。"
        ),
    )
    logger.info("[STT] 识别语言: %s (概率 %.2f)", info.language, info.language_probability)
    texts = [segment.text.strip() for segment in segments]
    return "".join(texts)


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    异步转写音频。
    接收原始音频字节，写入临时文件后调用 faster-whisper。
    """
    suffix = Path(filename).suffix or ".webm"
    async with _model_lock:
        # 写入临时文件
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            # 在线程池中执行同步转写，避免阻塞事件循环
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, _transcribe_sync, tmp_path)
            return text
        finally:
            # 清理临时文件
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass
