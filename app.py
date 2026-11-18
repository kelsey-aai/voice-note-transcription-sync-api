"""Minimal upload endpoint: POST a voice note, get the transcript back."""

import os
import tempfile

from assemblyai.sync.v1 import SyncTranscriber, SyncTranscriptError
from flask import Flask, jsonify, request

from voicenotes import api_key, transcribe_note

KEY = api_key()
app = Flask(__name__)
transcriber = SyncTranscriber(api_key=KEY)


@app.post("/voice-notes")
def upload_voice_note():
    upload = request.files["audio"]
    suffix = os.path.splitext(upload.filename or "")[1] or ".m4a"
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "note" + suffix)
        upload.save(path)
        try:
            return jsonify(transcribe_note(path, transcriber, KEY))
        except SyncTranscriptError as error:
            return jsonify({"status": "failed", "error_code": error.error_code}), 502


if __name__ == "__main__":
    transcriber.warm()  # open the connection before the first upload arrives
    app.run(port=8000)
