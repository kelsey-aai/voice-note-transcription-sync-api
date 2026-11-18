"""Voice-note transcription helpers: convert, check, and route each note."""

import os
import shutil
import subprocess
import sys
import wave

import assemblyai as aai
import requests
from assemblyai.sync.v1 import SyncTranscriber, SyncTranscriptionConfig
from dotenv import load_dotenv

load_dotenv()

SYNC_MODEL = "universal-3-6-pro"           # Sync runs on Universal-3.6 Pro
SYNC_URL = "https://sync.assemblyai.com/v1/transcribe"
MIN_MS = 80                                 # below this: Audio Too Short
SDK_MAX_MS = 120_000                        # SDK path (/v1/transcribe/live) cap
HTTP_MAX_MS = 20 * 60_000                   # HTTP /v1/transcribe cap


def api_key() -> str:
    key = os.environ.get("ASSEMBLYAI_API_KEY")
    if not key:
        sys.exit("Set ASSEMBLYAI_API_KEY (copy .env.example to .env and add your key).")
    return key


def to_wav(source_path: str, target_path: str) -> None:
    """Normalize any incoming voice note to 16 kHz mono 16-bit WAV."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found: install it (brew install ffmpeg or apt install ffmpeg).")
    subprocess.run(
        ["ffmpeg", "-i", source_path, "-ar", "16000", "-ac", "1",
         "-c:a", "pcm_s16le", "-y", target_path],
        check=True,
        capture_output=True,
    )


def duration_ms(wav_path: str) -> int:
    """Read the duration from the WAV header; no network call needed."""
    with wave.open(wav_path, "rb") as w:
        return int(w.getnframes() * 1000 / w.getframerate())


def sync_transcribe(transcriber: SyncTranscriber, wav_path: str, language_codes=None) -> str:
    """Up to 120 s: the SDK, which sends WAV or PCM to /v1/transcribe/live."""
    config = SyncTranscriptionConfig(model=SYNC_MODEL, language_codes=language_codes)
    result = transcriber.transcribe(wav_path, config=config)
    print(f"session_id: {result.session_id}")
    return result.text


def sync_transcribe_http(wav_path: str, key: str) -> str:
    """120 s to 20 min: POST the finished file to /v1/transcribe over HTTP."""
    with open(wav_path, "rb") as f:
        response = requests.post(
            SYNC_URL,
            headers={"Authorization": key, "X-AAI-Model": SYNC_MODEL},
            files={"audio": ("voice_note.wav", f, "audio/wav")},
            timeout=60,
        )
    response.raise_for_status()
    result = response.json()
    print(f"session_id: {result['session_id']}")
    return result["text"]


def submit_async(path: str, key: str, webhook_url=None) -> str:
    """Over 20 min: submit a pre-recorded job on AssemblyAI-STT-3.7."""
    config = aai.TranscriptionConfig(
        speech_models=["assemblyai-stt-3-7", "universal-2"],
        webhook_url=webhook_url,
    )
    transcript = aai.Transcriber(api_key=key, config=config).submit(path)
    return transcript.id


def transcribe_note(source_path: str, transcriber: SyncTranscriber, key: str) -> dict:
    wav_path = os.path.splitext(source_path)[0] + ".16k.wav"
    to_wav(source_path, wav_path)
    ms = duration_ms(wav_path)

    if ms < MIN_MS:
        return {"status": "skipped", "reason": "too_short", "duration_ms": ms}
    if ms <= SDK_MAX_MS:
        return {"status": "done", "text": sync_transcribe(transcriber, wav_path)}
    if ms <= HTTP_MAX_MS:
        return {"status": "done", "text": sync_transcribe_http(wav_path, key)}
    return {"status": "pending", "job_id": submit_async(wav_path, key)}
