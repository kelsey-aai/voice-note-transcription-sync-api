import os
import sys

from assemblyai.sync.v1 import SyncTranscriber, SyncTranscriptionConfig

api_key = os.environ.get("ASSEMBLYAI_API_KEY") or sys.exit("Set ASSEMBLYAI_API_KEY")

config = SyncTranscriptionConfig(model="universal-3-6-pro")
transcriber = SyncTranscriber(api_key=api_key, config=config)
transcriber.warm()  # open the connection as soon as you know a note is coming
result = transcriber.transcribe("./voice_note.wav")

print(result.text)
