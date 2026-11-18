"""Transcribe one voice note from the command line: python transcribe.py note.m4a"""

import sys

from assemblyai.sync.v1 import SyncTranscriber

from voicenotes import api_key, transcribe_note

if len(sys.argv) != 2:
    sys.exit("usage: python transcribe.py <voice-note file>")

key = api_key()
with SyncTranscriber(api_key=key) as transcriber:
    transcriber.warm()
    print(transcribe_note(sys.argv[1], transcriber, key))
