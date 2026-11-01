#!/usr/bin/env python3
"""Execute real validators and produce an auditable per-episode report.json."""
from __future__ import annotations

import argparse
import json
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
    args = parser.parse_args(argv)
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

    def execute(label, args_list):
        tool = SCRIPTS / (label + ".py")
        if not tool.is_file():
            not_run(label, "validator is not installed")
            return
        try:
            proc = subprocess.run([sys.executable, str(tool), *args_list, "--json"],
                                  capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", timeout=120, check=False)
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
    elif args.require_translation:
        not_run("check_translation", "required translated/source chunk JSON missing")
    if ass.is_file():
        arguments = [str(ass)]
        if duration is not None:
            arguments += ["--duration", str(duration)]
        if data.get("video_width") and data.get("video_height"):
            arguments += ["--width", str(data["video_width"]),
                          "--height", str(data["video_height"])]
        execute("check_ass", arguments)
    elif "ass" in requested:
        not_run("check_ass", "requested ASS not found")
    video = data.get("source", {}).get("media")
    if video:
        media = Path(video)
        if not media.is_absolute():
            media = root / media
        if media.is_file():
            execute("probe_media", [str(media)])
        else:
            not_run("probe_media", "declared source media does not exist")
    state = "fail" if failed else "incomplete" if missing else "pass"
    out = {
        "schema_version": 1, "episode_id": data["episode_id"],
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
