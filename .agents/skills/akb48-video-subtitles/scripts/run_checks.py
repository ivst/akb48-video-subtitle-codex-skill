#!/usr/bin/env python3
"""Execute real validators and produce an auditable per-episode report.json."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
MEMBERS = SCRIPTS.parent / "glossaries" / "members"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--require-translation", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--media-timeout", type=float, default=1800,
                        help="maximum decode seconds per media file")
    args = parser.parse_args(argv)
    if not math.isfinite(args.media_timeout) or args.media_timeout <= 0:
        parser.error("--media-timeout must be finite and positive")
    root = args.project.resolve()
    try:
        data = json.loads((root / "episode.json").read_text(encoding="utf-8"))
        if data.get("schema_version") != 1:
            raise ValueError("unsupported episode.json schema_version")
        locale = data["locale"]
        source_srt = root / data["source"]["srt"]
        target_srt = root / data["output"]["srt"]
        input_chunks = root / data["work"]["input"]
        translated_chunks = root / data["work"]["translated"]
        ass = root / data["output"]["ass"]
        duration = data.get("duration_seconds")
        requested = data.get("requested_outputs", ["srt"])
        if not isinstance(requested, list):
            raise ValueError("requested_outputs must be an array")
    except (OSError, UnicodeError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    events = []
    failed = []
    missing = []

    def not_run(label, reason):
        events.append({"tool": label, "status": "not_run", "reason": reason})
        missing.append(label)

    def execute(label, args_list, timeout=120):
        tool = SCRIPTS / (label + ".py")
        if not tool.is_file():
            not_run(label, "validator is not installed")
            return
        try:
            proc = subprocess.run([sys.executable, str(tool), *args_list, "--json"],
                                  capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", timeout=timeout, check=False)
            try:
                body = json.loads(proc.stdout)
            except json.JSONDecodeError:
                body = {"tool": label, "status": "fail", "errors": [
                    proc.stderr.strip() or "validator did not emit JSON"], "warnings": []}
            state = "pass" if proc.returncode == 0 and body.get("status") == "pass" else "fail"
            events.append({"tool": label, "status": state, "exit_code": proc.returncode,
                           "argv": args_list, "result": body})
            if state == "fail":
                failed.append(label)
        except (OSError, subprocess.TimeoutExpired) as exc:
            events.append({"tool": label, "status": "fail", "reason": str(exc)})
            failed.append(label)

    if target_srt.is_file():
        arguments = [str(target_srt), "--profile", "ru"] if locale == "ru" else [
            str(target_srt), "--target-lang", locale]
        if duration is not None:
            arguments += ["--duration", str(duration)]
        execute("check_srt", arguments)
    elif "srt" in requested:
        not_run("check_srt", "requested SRT not found")
    if source_srt.is_file() and target_srt.is_file():
        execute("check_names", ["--source", str(source_srt), "--target", str(target_srt),
                                "--members", str(MEMBERS / (locale + ".csv")),
                                "--episode", str(root / "episode.json")])
    else:
        not_run("check_names", "Japanese or translated SRT missing")
    if input_chunks.is_file() and translated_chunks.is_file():
        execute("check_translation", ["--input", str(input_chunks),
                "--translated", str(translated_chunks), "--target-lang", locale,
                "--members", str(MEMBERS / (locale + ".csv")),
                "--episode", str(root / "episode.json")])
        execute("check_song_titles", ["--input", str(input_chunks), "--translated", str(translated_chunks),
                "--episode", str(root / "episode.json"), "--strict"])
    elif args.require_translation:
        not_run("check_translation", "required translated/source chunk JSON missing")
        not_run("check_song_titles", "required translated/source chunk JSON missing")
    if ass.is_file():
        arguments = [str(ass)]
        if duration is not None:
            arguments += ["--duration", str(duration)]
        if data.get("video_width") and data.get("video_height"):
            arguments += ["--width", str(data["video_width"]),
                          "--height", str(data["video_height"])]
        execute("check_ass", arguments)
    elif "ass" in requested or "video" in requested:
        not_run("check_ass", "requested ASS not found")
    presentation = root / data['work'].get('presentation','work/presentation.json')
    if presentation.is_file():
        arguments = ['--input', str(presentation), '--episode', str(root/'episode.json')]
        if ass.is_file(): arguments += ['--ass',str(ass)]
        if target_srt.is_file(): arguments += ['--srt',str(target_srt)]
        execute('check_presentation',arguments)
    elif any(output in requested for output in ('ass','video')):
        not_run('check_presentation','reviewed speaker-aware presentation missing; cannot approve styled outputs')
    video = data.get("source", {}).get("media")
    rendered = data.get("output", {}).get("video")
    source_media = None
    rendered_media = None
    if video:
        source_media = Path(video)
        if not source_media.is_absolute():
            source_media = root / source_media
        if source_media.is_file():
            execute("probe_media", [str(source_media)])
        else:
            not_run("probe_media", "declared source media does not exist")
    if rendered:
        rendered_media = Path(rendered)
        if not rendered_media.is_absolute():
            rendered_media = root / rendered_media
        if rendered_media.is_file():
            execute("probe_media", [str(rendered_media)])
            if source_media and source_media.is_file():
                execute("compare_media", ["--source", str(source_media), "--rendered", str(rendered_media)])
                execute("check_decode", ["--source", str(source_media), "--rendered", str(rendered_media),
                        "--timeout", str(args.media_timeout)], timeout=2 * args.media_timeout + 30)
                if data.get("audio_preservation", "unchanged") == "unchanged":
                    execute("compare_audio", ["--source", str(source_media), "--rendered", str(rendered_media),
                            "--timeout", str(args.media_timeout)], timeout=2 * args.media_timeout + 30)
            else:
                not_run("compare_media", "source media unavailable; cannot compare output")
                not_run("check_decode", "source media unavailable; cannot compare decoded frames")
                if data.get("audio_preservation", "unchanged") == "unchanged":
                    not_run("compare_audio", "source media unavailable; cannot verify source audio")
        elif "video" in requested:
            not_run("rendered_video", "requested rendered video not found")
            not_run("check_decode", "requested rendered video not found")
    elif "video" in requested:
        not_run("rendered_video", "requested rendered video path not set")
        not_run("check_decode", "requested rendered video path not set")
    state = "fail" if failed else "incomplete" if missing else "pass"
    out = {
        "schema_version": 1, "episode_id": data["episode_id"],
        "scope": "automated structure, presentation correspondence and media checks; not editorial acceptance",
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "status": state,
        "executed_checks": len([r for r in events if r["status"] != "not_run"]),
        "failed_checks": failed, "missing_checks": missing, "checks": events,
        "limitations": [
            "Automated validation cannot establish translation meaning or speaker identity.",
            "Visual review and publishing rights are not assessed by these checks."
        ]
    }
    dest = root / "report.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out if args.json else {"status": state, "path": str(dest),
          "executed": out["executed_checks"], "missing": missing, "failed": failed}, ensure_ascii=True))
    return 0 if state == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
