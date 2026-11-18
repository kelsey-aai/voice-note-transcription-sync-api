# Voice note transcription with the AssemblyAI Sync API

Companion code for [How to add voice-note transcription to your app](https://www.assemblyai.com/blog/add-voice-memo-transcription-to-your-app).

Every voice note is converted to 16 kHz mono WAV with ffmpeg, measured from its WAV header, and routed:

| Note length | Path | Model |
| --- | --- | --- |
| under 80 ms | skipped (accidental tap) | none |
| up to 120 s | Python SDK `SyncTranscriber` (`/v1/transcribe/live`) | `universal-3-6-pro` |
| 120 s to 20 min | HTTP `POST https://sync.assemblyai.com/v1/transcribe` | `universal-3-6-pro` |
| over 20 min | pre-recorded (async) job | AssemblyAI-STT-3.7 (`assemblyai-stt-3-7`) |

## 1. Clone

```bash
git clone https://github.com/kelsey-aai/voice-note-transcription-sync-api.git
cd voice-note-transcription-sync-api
```

## 2. Install

Needs Python 3.8+ and ffmpeg (`brew install ffmpeg` or `apt install ffmpeg`).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install            # only for the JavaScript examples (Node.js 18+)
```

## 3. Configure

```bash
cp .env.example .env    # then paste your key from https://www.assemblyai.com/dashboard
```

`quickstart.*`, `quickstart_http.py`, and `multilingual.*` read the key from the environment, so `export ASSEMBLYAI_API_KEY=...` for those.

## 4. Run

| File | What it does |
| --- | --- |
| `quickstart.py` | Smallest SDK call on `./voice_note.wav` |
| `quickstart.mjs` | Same call with the JavaScript SDK (`node quickstart.mjs`) |
| `quickstart_http.py` | Same over HTTP, sending the original `./voice_note.m4a` |
| `multilingual.py`, `multilingual.mjs` | Steer a note toward Spanish and English with `language_codes` |
| `transcribe.py note.m4a` | Convert, check, and route one note |
| `app.py` | Flask server: `curl -F audio=@note.m4a localhost:8000/voice-notes` |
| `backfill.py <folder>` | Transcribe a folder of WAV notes (up to 120 s each), newest first, 10 at a time |

Without a key, every script exits with `Set ASSEMBLYAI_API_KEY ...`.

## Limits (from the Sync API docs)

- SDK `transcribe()`: WAV or raw PCM, up to 120 s.
- HTTP `/v1/transcribe`: 80 ms to 20 minutes, up to 256 MB; WAV, PCM, AAC, MP3, M4A, Ogg/Opus, FLAC, or WebM.
- 200 requests per minute per account. Retry 429 and 503 after `Retry-After`; retry 500 and 504 once; fix 400, 413, and 415.
