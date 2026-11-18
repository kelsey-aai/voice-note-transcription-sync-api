import os
import sys

from assemblyai.sync.v1 import SyncTranscriber, SyncTranscriptionConfig

api_key = os.environ.get("ASSEMBLYAI_API_KEY") or sys.exit("Set ASSEMBLYAI_API_KEY")
transcriber = SyncTranscriber(api_key=api_key)

# You know this user's threads are in Spanish and English.
config = SyncTranscriptionConfig(model="universal-3-6-pro", language_codes=["es", "en"])
result = transcriber.transcribe("./voice_note.wav", config=config)

print(result.text)
