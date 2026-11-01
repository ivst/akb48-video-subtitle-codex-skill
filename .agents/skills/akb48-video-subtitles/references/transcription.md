# Optional Japanese transcription with faster-whisper

Use this when Japanese captions are missing or need an independent check. Whisper
recognizes speech; it does not establish speaker identity or translate into the
chosen subtitle language in this workflow. Keep the Japanese transcript and
compare uncertain names, jokes, numbers, lyrics and overlapping voices to audio.

Reliable captions do not require a second full transcript. For isolated uncertainties transcribe the relevant snippet and retain its offset into the source; expand to full ASR when captions are missing or coverage is poor. Reuse an existing compatible environment and downloaded weights.

The base skill and its validators do not install or require faster-whisper.
See the [upstream installation and usage guide](https://github.com/SYSTRAN/faster-whisper).
The example below uses CPU/int8 and does not require WSL, CUDA or a GPU. Use a
separate Python environment so optional ASR dependencies do not affect Codex's tools.
Python 3.11 is a conservative example; compatible versions depend on backend wheels.

## Install in a working folder

Windows PowerShell (Python 3.11 and its launcher must already be installed):

```powershell
py -3.11 -m venv .venv-asr
.\.venv-asr\Scripts\python.exe -m pip install faster-whisper
```

Linux/macOS (use an installed compatible Python interpreter):

```sh
python3.11 -m venv .venv-asr
.venv-asr/bin/python -m pip install faster-whisper
```

The first model load downloads weights and needs network access and cache space.
A downloaded compatible model directory can be supplied instead of `small` for
offline use. Audio is processed locally by this example. No translation API key
is required. GPU setup is optional: consult upstream for driver, CUDA, cuDNN and
CTranslate2 compatibility instead of copying a fixed CUDA recipe.

## Prepare audio

FFmpeg is needed for this command and the video workflow. faster-whisper itself
can decode supported media through PyAV.

```sh
ffmpeg -nostdin -i original.mp4 -map 0:a:0 -ar 16000 -ac 1 audio.wav
```

Check which audio track is Japanese before choosing `0:a:0`; the first track may
be a dub. The command intentionally does not overwrite an existing audio file.

## Transcribe Japanese, retaining word timestamps

Save this example as `transcribe_ja.py` in the working folder. Output paths are
examples, not the translation-chunk schema: the JSON contains raw ASR evidence,
and the SRT is a draft source transcript. The example refuses existing outputs.

```python
import json
import sys
from pathlib import Path
from faster_whisper import WhisperModel

audio = Path(sys.argv[1])
output = Path(sys.argv[2])
srt = output.with_suffix(".srt")
if not audio.is_file():
    raise SystemExit("Input audio does not exist")
if output.exists() or srt.exists():
    raise SystemExit("Choose new output paths; existing files are preserved")

model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8)
segments, info = model.transcribe(
    str(audio), language="ja", task="transcribe", beam_size=5,
    vad_filter=True, word_timestamps=True,
)
# Transcription is lazy: consuming segments performs the actual recognition.
rows = []
for segment in segments:
    if segment.text.strip():
        rows.append({
            "id": len(rows) + 1,
            "start": segment.start, "end": segment.end,
            "text": segment.text.strip(),
            "words": [{"start": w.start, "end": w.end, "word": w.word}
                      for w in (segment.words or [])],
        })
if not rows:
    raise SystemExit("No speech recognized; review the audio and VAD settings")

def stamp(seconds):
    total = max(0, round(seconds * 1000))
    hours, total = divmod(total, 3600000)
    minutes, total = divmod(total, 60000)
    seconds, milliseconds = divmod(total, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

payload = {
    "kind": "raw_asr", "time_unit": "seconds", "language": info.language,
    "model": "small", "device": "cpu", "compute_type": "int8",
    "settings": {"task": "transcribe", "beam_size": 5,
                 "vad_filter": True, "word_timestamps": True, "cpu_threads": 8},
    "segments": rows,
}
with output.open("x", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
with srt.open("x", encoding="utf-8") as f:
    for row in rows:
        f.write(f'{row["id"]}\n{stamp(row["start"])} --> {stamp(row["end"])}\n'
                f'{row["text"]}\n\n')
print(output, srt)
```

Run with the environment's Python, without needing shell activation:

```powershell
.\.venv-asr\Scripts\python.exe transcribe_ja.py audio.wav asr.ja.json
```

```sh
.venv-asr/bin/python transcribe_ja.py audio.wav asr.ja.json
```

For reproducibility, save `python -m pip freeze` from this ASR environment along
with the model identifier/revision and the settings used. A model/version change
may change the transcript. This guide is a usage example, not a benchmark or a
claim that every platform/model combination has been tested here.

## Review before translating

- Use the draft SRT as evidence, then create the reviewed Japanese source and
  ID-stable translation chunks described in [translation-protocol.md](translation-protocol.md).
- Word timestamps are approximate alignment hints, not diarization or verified
  boundaries of a speaker turn. Do not assign a voice solely from the current shot.
- An episode-specific `initial_prompt` can suggest verified names/terms; it does
  not prove that those words were spoken. Record any prompt if one is used.
- VAD may omit quiet speech or singing. Singing needs transcription only when lyric translation was explicitly requested; it is omitted by default. Recheck suspect speech intervals or transcribe
  them separately without VAD. Preserve the original time offset when using clips.
- Longer models may help some passages but cannot guarantee correct names or
  lyrics. Keep uncertainty visible and use fluent review where needed.
