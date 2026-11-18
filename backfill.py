"""Backfill transcripts for voice notes already on disk, newest first.

usage: python backfill.py <folder of 16 kHz WAV notes up to 120 s>
"""

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

from assemblyai.sync.v1 import (
    AsyncSyncTranscriber,
    SyncTranscriptError,
    SyncTranscriptionConfig,
)

from voicenotes import SYNC_MODEL, api_key


@dataclass
class Note:
    id: str
    path: str


CONFIG = SyncTranscriptionConfig(model=SYNC_MODEL)


async def transcribe_one(transcriber, note, semaphore):
    async with semaphore:
        for attempt in range(3):
            try:
                result = await transcriber.transcribe(note.path, config=CONFIG)
                return note.id, result.text
            except SyncTranscriptError as error:
                transient = error.status_code in (429, 503) or (
                    error.status_code in (500, 504) and attempt == 0
                )
                if transient and attempt < 2:
                    await asyncio.sleep(error.retry_after or 2 ** attempt)
                    continue
                print(f"{note.id}: {error.status_code} {error.error_code}", file=sys.stderr)
                return note.id, None       # mark the row, move on


async def backfill(notes):
    semaphore = asyncio.Semaphore(10)      # 429s mean lower it; default limit is 200 req/min
    async with AsyncSyncTranscriber(api_key=api_key()) as transcriber:
        return await asyncio.gather(
            *(transcribe_one(transcriber, n, semaphore) for n in notes)
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python backfill.py <folder of WAV notes>")
    files = sorted(Path(sys.argv[1]).glob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)
    notes = [Note(id=p.stem, path=str(p)) for p in files]
    for note_id, text in asyncio.run(backfill(notes)):
        print(note_id, "->", text)
