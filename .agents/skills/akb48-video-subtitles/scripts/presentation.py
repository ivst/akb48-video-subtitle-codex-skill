"""Speaker-aware display contract and compact ASS/SRT rendering (stdlib only)."""
from __future__ import annotations
import re
import unicodedata

# Placeholder labels that pretend to name an unestablished voice. An unnamed row
# carries no label at all, so these are rejected instead of being rendered.
PLACEHOLDER_LABEL = re.compile(
    r"^(?:voice|голос|voz|suara|화자|เสียง|未知声[音音]?|unknown|неизвестн\w*)\s*\??$",
    re.IGNORECASE)



# Episode-12 remains the default; overrides preserve the speaker/display contract.
STYLE_DEFAULTS = {
    "panel_x": 110, "panel_width": 1700,
    "panel_fill": "#FFFFFF", "panel_border": "#D5CBD5", "panel_opacity": 245/255,
    "dialogue_color": "#252525", "sign_fill": "#87348F",
    "sign_border": "#46BCD7", "sign_color": "#FFFFFF", "sign_font_size": 26,
}
SIGN_STYLE_KEYS = {"sign_fill", "sign_border", "sign_color", "sign_font_size"}


def style_settings(overrides, base=None, allowed=None):
    if not isinstance(overrides, dict):
        raise ValueError("style must be an object")
    unknown = set(overrides) - (set(STYLE_DEFAULTS) if allowed is None else allowed)
    if unknown:
        raise ValueError("unsupported style keys: " + ", ".join(sorted(unknown)))
    style = dict(STYLE_DEFAULTS if base is None else base)
    style.update(overrides)
    for key in ("panel_fill", "panel_border", "dialogue_color", "sign_fill", "sign_border", "sign_color"):
        if not isinstance(style[key], str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", style[key]):
            raise ValueError(f"style {key} must be #RRGGBB")
    x, width = style["panel_x"], style["panel_width"]
    if type(x) is not int or type(width) is not int or x < 0 or width < 1200 or x + width > 1920:
        raise ValueError("style panel must fit the 1920px canvas and be at least 1200px wide")
    opacity = style["panel_opacity"]
    if type(opacity) not in (int, float) or not 0.5 <= opacity <= 1:
        raise ValueError("style panel_opacity must be a finite number from 0.5 to 1")
    if type(style["sign_font_size"]) is not int or not 22 <= style["sign_font_size"] <= 42:
        raise ValueError("style sign_font_size must be an integer from 22 to 42")
    return style


def bgr(color):
    return color[5:7] + color[3:5] + color[1:3]


def validate(data, episode):
    errors, warnings = [], []
    if not isinstance(episode,dict):
        return ["episode settings must be an object"], []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return ["presentation schema_version must be 1"], []
    try:
        style = style_settings(data.get("style", {}))
    except ValueError as exc:
        errors.append(str(exc))
        style = dict(STYLE_DEFAULTS)
    speakers, turns, events = data.get("speakers"), data.get("turns"), data.get("events")
    if not isinstance(speakers, dict) or not isinstance(turns, dict) or not isinstance(events, list) or not events:
        return ["presentation requires speakers/turns objects and nonempty events array"], []
    for key, speaker in speakers.items():
        if not isinstance(key,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}",key):
            errors.append("speaker IDs must be safe ASCII identifiers")
        if not isinstance(speaker, dict) or not isinstance(speaker.get("label"), str) or not speaker["label"].strip():
            errors.append(f"speaker {key}: label required")
        elif any(c in speaker['label'] for c in '\r\n'):
            errors.append(f"speaker {key}: label must be one line")
        elif PLACEHOLDER_LABEL.match(speaker['label'].strip()):
            errors.append(f"speaker {key}: placeholder label; leave unestablished voices unnamed "
                          "(speaker_id null) instead of using 'Голос ?' / 'Voice ?'")
        elif not re.fullmatch(r"#[0-9a-fA-F]{6}", speaker.get("color", "")):
            errors.append(f"speaker {key}: color must be #RRGGBB")
    policy = episode.get("lyrics_policy", "omit")
    if policy not in ("omit", "requested"):
        errors.append("lyrics_policy must be omit or requested")
    if policy == "requested" and (not isinstance(episode.get('lyrics_request'),str) or not episode['lyrics_request'].strip()):
        errors.append("requested lyrics require the user's instruction in lyrics_request")
    ids, intervals = set(), []
    for event in events:
        if not isinstance(event, dict):
            errors.append("event must be an object"); continue
        key = event.get("id")
        if not isinstance(key, str) or not key or key in ids:
            errors.append("event IDs must be unique nonempty strings")
        ids.add(str(key))
        start, end = event.get("start_ms"), event.get("end_ms")
        valid_time = all(type(x) is int for x in (start, end)) and 0 <= start < end
        if not valid_time:
            errors.append(f"event {key}: invalid millisecond times")
        elif end//10 <= start//10:
            errors.append(f"event {key}: interval collapses at ASS centisecond precision")
        elif episode.get("duration_seconds") is not None and end > float(episode["duration_seconds"]) * 1000 + 1:
            errors.append(f"event {key}: exceeds episode duration")
        kind = event.get("kind")
        if kind not in ("dialogue", "inscription", "song_title", "lyrics"):
            errors.append(f"event {key}: unsupported kind; background music must be omitted")
        if kind == "lyrics" and policy != "requested":
            errors.append(f"event {key}: lyrics not explicitly requested; omit from deliverables")
        if "style" in event:
            if kind not in ("inscription", "song_title"):
                errors.append(f"event {key}: style overrides are only supported for signs")
            else:
                try:
                    style_settings(event["style"], style, SIGN_STYLE_KEYS)
                except ValueError as exc:
                    errors.append(f"event {key}: {exc}")
        if kind != "dialogue":
            if not isinstance(event.get("text"), str) or not event["text"].strip():
                errors.append(f"event {key}: text required")
            continue
        if valid_time:
            intervals.append((start, end, str(key)))
        rows = event.get("rows")
        if not isinstance(rows, list) or not 1 <= len(rows) <= 2:
            errors.append(f"event {key}: one or two explicit speaker rows required"); continue
        if len(rows) == 2 and any(not isinstance(row, dict) or row.get("speaker_id") is None for row in rows):
            errors.append(f"event {key}: paired rows require two established voices; keep unnamed turns separate")
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("text"), str) or not row["text"].strip():
                errors.append(f"event {key}: row text required"); continue
            speaker_id, source_ids = row.get("speaker_id"), row.get("source_ids")
            if speaker_id is not None and speaker_id not in speakers:
                errors.append(f"event {key}: unknown speaker_id {speaker_id}")
            if not isinstance(source_ids, list) or not source_ids or any(not isinstance(s, str) for s in source_ids):
                errors.append(f"event {key}: row source_ids required"); continue
            if len(source_ids) != len(set(source_ids)):
                errors.append(f"event {key}: duplicate source IDs in row")
            if len(source_ids) > 1 and speaker_id is None:
                errors.append(f"event {key}: cannot merge unknown speakers")
            for source_id in source_ids:
                turn = turns.get(source_id)
                if not isinstance(turn, dict):
                    errors.append(f"event {key}: missing turn {source_id}"); continue
                if turn.get("speaker_id") != speaker_id:
                    errors.append(f"event {key}: merged source turn belongs to a different speaker")
                if speaker_id is not None and not str(turn.get("evidence") or "").strip():
                    errors.append(f"event {key}: named voice requires attribution evidence")
            if speaker_id is None:
                warnings.append(f"event {key}: unnamed voice; published without a speaker label, needs audio review")
            suspicious = " / " in row["text"] or row["text"].count("—") >= 2
            if suspicious and (row.get("turn_review") != "single_speaker_verified" or not row.get("review_evidence")):
                errors.append(f"event {key}: possible mixed voices; split turns or document a verified single speaker")
    last_end = -1
    for start, end, key in sorted(intervals):
        if start < last_end:
            errors.append(f"event {key}: overlapping dialogue; use explicit paired rows")
        last_end = max(last_end, end)
    return errors, warnings


def stamp(ms, ass=False):
    h, rest = divmod(ms, 3600000); m, rest = divmod(rest, 60000); s, milli = divmod(rest, 1000)
    return f"{h}:{m:02}:{s:02}.{milli//10:02}" if ass else f"{h:02}:{m:02}:{s:02},{milli:03}"


def safe(text):
    # Prevent user text from injecting ASS overrides or hard-break escapes.
    return text.replace("\\", "＼").replace("{", "｛").replace("}", "｝").replace("\r", "")


def units(text):
    return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def wrap(text, limit):
    lines = []
    for part in text.splitlines():
        current = ""
        for word in part.split():
            if units(word) > limit:
                raise ValueError("unbreakable text is too wide; provide explicit language-appropriate line breaks")
            if current and units(current + " " + word) > limit:
                lines.append(current); current = word
            else:
                current = (current + " " + word).strip()
        if current: lines.append(current)
    return lines


def render(data, episode):
    errors, warnings = validate(data, episode)
    if errors: raise ValueError("; ".join(errors))
    # Fixed logical 1080p canvas scales to the video frame in libass.
    # 30 logical pixels = 20 actual pixels in a 720p render.
    preset = data.get("style_preset", "episode-12")
    if preset != "episode-12":
        raise ValueError("unsupported style_preset; use episode-12")
    style = style_settings(data.get("style", {}))
    panel_x, panel_width = style["panel_x"], style["panel_width"]
    panel_alpha = f'{round((1-style["panel_opacity"])*255):02X}'
    dialogue_color = bgr(style["dialogue_color"])
    sign_color = bgr(style["sign_color"])
    font = data.get("font", "Segoe UI Semibold")
    if not isinstance(font, str) or any(c in font for c in ",\r\n"):
        raise ValueError("invalid font family")
    bottom = data.get("bottom_margin", 30)
    if type(bottom) is not int or not 15 <= bottom <= 180:
        raise ValueError("bottom_margin must be 15–180 pixels on the logical 1080p canvas")
    if bottom > 60 and not data.get("placement_reason"):
        raise ValueError("raised dialogue requires a scene/placement reason")
    ass = [f"""[Script Info]
ScriptType: v4.00+
; Style preset: episode-12 / revision 1
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Speech,{font},40,&H00{dialogue_color},&H00{dialogue_color},&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Speaker,{font},26,&H00252525,&H00252525,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Shape,{font},20,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Sign,{font},{style["sign_font_size"]},&H00{sign_color},&H00{sign_color},&H004D384F,&H004D384F,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Lyrics,{font},34,&H00252525,&H00252525,&H00FFFFFF,&H00FFFFFF,0,-1,0,0,100,100,0,0,3,4,0,2,100,100,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""]
    tracks = {"dialogue": [], "inscriptions": [], "lyrics": []}
    def event(e, style, text, layer=2, name=""):
        ass.append(f'Dialogue: {layer},{stamp(e["start_ms"],True)},{stamp(e["end_ms"],True)},{style},{name},0,0,0,,{text}\n')
    def rect(e, x, y, w, h, color, layer=0, alpha="00", border="D5CBD5"):
        event(e, "Shape", f"{{\\an7\\pos({x},{y})\\p1\\1c&H{color}&\\1a&H{alpha}&\\bord3\\3c&H{border}&\\3a&H00&\\shad0}}m 0 0 l {w} 0 l {w} {h} l 0 {h}{{\\p0}}", layer)
    for e in sorted(data["events"], key=lambda x: (x["start_ms"], x["id"])):
        kind = e["kind"]
        if kind == "dialogue":
            scene_bottom=e.get('bottom_margin',bottom)
            if type(scene_bottom) is not int or not 15 <= scene_bottom <= 180:
                raise ValueError(f'event {e["id"]}: invalid bottom_margin')
            if scene_bottom > 60 and not e.get('placement_reason') and not data.get('placement_reason'):
                raise ValueError(f'event {e["id"]}: raised dialogue requires a scene/placement reason')
            rendered, portable = [], []
            for i, row in enumerate(e["rows"]):
                sp = data["speakers"].get(row.get("speaker_id"))
                # No placeholder: an unestablished voice is published without any name or rail.
                label = sp["label"] if sp else None
                color = sp["color"] if sp else None
                speaker_color = bgr(color) if color else None
                if label and units(label) > 17: raise ValueError(f"speaker label too long: {label}; choose a concise label")
                limit = min(62, (panel_width - (260 if label else 70)) // 20)
                lines = wrap(safe(row["text"]), limit)
                if not 1 <= len(lines) <= 2: raise ValueError(f'event {e["id"]}: split long dialogue into timed events')
                rendered.append((label, speaker_color, lines, row.get("speaker_id") or "unnamed"))
                portable.append((label + ": " if label else "") + row["text"])
            heights = [82 if len(x[2]) == 1 else 128 for x in rendered]
            y = 1080 - scene_bottom - sum(heights)
            if sum(len(x[2]) for x in rendered) > 3:
                raise ValueError(f'event {e["id"]}: split paired exchange longer than three lines')
            for (label, color, lines, voice), height in zip(rendered, heights):
                rect(e, panel_x, y, panel_width, height, bgr(style["panel_fill"]),
                     alpha=panel_alpha, border=bgr(style["panel_border"]))
                if label:
                    rect(e, panel_x+16, y+18, 5, height-36, color, 1, border=color)
                    fs = 22 if len(label)>12 else 26
                    event(e, "Speaker", f"{{\\pos({panel_x+115},{y+height/2})\\fs{fs}\\1c&H{color}&}}"+safe(label))
                fs = (38 if len(lines) == 1 else 32) if len(rendered) == 2 else 40
                x = panel_x + (panel_width + 190)/2 if label else panel_x + panel_width/2
                x = int(x) if x == int(x) else x
                event(e, "Speech", f"{{\\pos({x},{y+height/2})\\fs{fs}}}"+r"\N".join(lines),
                      name=voice if label else "")
                y += height
            tracks["dialogue"].append((e, "\n".join(portable)))
        elif kind in ("inscription", "song_title"):
            lines = wrap(safe(e["text"]), 64)
            if not 1 <= len(lines) <= 3: raise ValueError(f'event {e["id"]}: inscription too long')
            # Explicit position required: signs must follow their source region.
            box = e.get("box")
            if not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box):
                raise ValueError(f'event {e["id"]}: inscription box [x,y,width,height] required in 1920x1080 units')
            x,y,w,h = box
            if min(x,y)<0 or min(w,h)<=0 or x+w>1920 or y+h>1080:
                raise ValueError(f'event {e["id"]}: inscription box outside canvas')
            sign = style_settings(e.get("style", {}), style, SIGN_STYLE_KEYS)
            sign_fs = sign["sign_font_size"]
            if w < max(units(line) for line in lines)*20*sign_fs/26 or h < len(lines)*43*sign_fs/26:
                raise ValueError(f'event {e["id"]}: inscription box too small for text')
            rect(e,x,y,w,h,bgr(sign["sign_fill"]),3,border=bgr(sign["sign_border"]))
            extra = ""
            if sign_fs != style["sign_font_size"]:
                extra += f"\\fs{sign_fs}"
            if sign["sign_color"] != style["sign_color"]:
                extra += f"\\1c&H{bgr(sign['sign_color'])}&"
            event(e,"Sign",f"{{\\pos({x+w/2},{y+h/2}){extra}}}"+r"\N".join(lines),4)
            tracks["inscriptions"].append((e,e["text"]))
        else:
            event(e,"Lyrics",r"\N".join(wrap(safe(e["text"]),70)))
            tracks["lyrics"].append((e,e["text"]))
    def srt(rows):
        return "".join(f'{i}\n{stamp(e["start_ms"])} --> {stamp(e["end_ms"])}\n{text}\n\n' for i,(e,text) in enumerate(rows,1))
    return "".join(ass), {k:srt(v) for k,v in tracks.items()}, warnings
