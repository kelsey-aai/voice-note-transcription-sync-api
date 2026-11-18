import os
import sys

import requests

api_key = os.environ.get("ASSEMBLYAI_API_KEY") or sys.exit("Set ASSEMBLYAI_API_KEY")

# /v1/transcribe takes the phone's original file: no conversion needed.
with open("voice_note.m4a", "rb") as f:
    response = requests.post(
        "https://sync.assemblyai.com/v1/transcribe",
        headers={
            "Authorization": api_key,
            "X-AAI-Model": "universal-3-6-pro",
        },
        files={"audio": ("voice_note.m4a", f, "audio/mp4")},
        timeout=60,
    )
response.raise_for_status()

result = response.json()
print(result["text"])
