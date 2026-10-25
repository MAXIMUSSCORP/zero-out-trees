# Copied from zeroout/community_check.py; do not edit here
"""Checks one community contribution file. Standard library only: the trees repo's CI copies this file
and runs it where zeroout is not installed. Every error is a plain sentence that names the field."""
import hashlib
import json
import re
import unicodedata
from datetime import datetime

FORMAT = 1
MAX_BYTES = 256 * 1024
MAX_OBSERVATIONS = 500
MAX_DEPTH = 6
MAX_NAME = 80
MAX_LABEL = 120
MAX_TEXT = 1000
MAX_ERRORS = 20
TOLL_FREE = {"800", "888", "877", "866", "855", "844", "833"}
OUTCOMES = (
    "menu", "hold", "human", "voicemail", "hangup",
    "invalid_input", "needs_input", "speech_menu",
)
SOURCES = ("crawl", "phone")
KEYS = set("0123456789*#")
PATH = re.compile(r"trees/(\d{10})/([0-9a-f]{12})-(\d{8}T\d{6}Z)\.json")
OBS_PATH = re.compile(r"[0-9*#](\.[0-9*#])*")
STAMP = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ")
DIGITS = re.compile(r"\d(?:[ .\-]*\d){5,}")
TOP_KEYS = ("format", "number", "name", "contributed_at", "observations")
OBS_KEYS = ("path", "prompt_text", "options", "outcome", "prompt_seconds", "heard_at", "source")


def observation_uid(number: str, obs: dict) -> str:
    canon = json.dumps({"number": number, "observation": obs}, sort_keys=True,
                       separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _short(value, limit: int = 40) -> str:
    text = repr(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def _bad_constant(name: str):
    raise ValueError(name)


def _stamp_ok(value) -> bool:
    if not isinstance(value, str) or not STAMP.fullmatch(value):
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def _control_chars(node, where: str, out: list[str]) -> None:
    if isinstance(node, str):
        if any(unicodedata.category(c) == "Cc" for c in node):
            out.append(f"{where or 'The file'} contains a control character, such as a line break or tab.")
    elif isinstance(node, dict):
        for k, v in node.items():
            _control_chars(k, f"A field name under {where or 'the file'}", out)
            _control_chars(v, f"{where}.{k}" if where else str(k), out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _control_chars(v, f"{where}[{i}]", out)


def _keys_exact(obj: dict, wanted: tuple, where: str, out: list[str]) -> None:
    for k in wanted:
        if k not in obj:
            out.append(f"{where} is missing the field {k}.")
    for k in obj:
        if k not in wanted:
            out.append(f"{where} has an unknown field {_short(k)}.")


def _check_observation(i: int, o, out: list[str]) -> None:
    where = f"observations[{i}]"
    if not isinstance(o, dict):
        out.append(f"{where} must be an object, got {_short(o)}.")
        return
    _keys_exact(o, OBS_KEYS, where, out)
    path = o.get("path")
    if "path" in o:
        if not isinstance(path, str) or (path != "" and not OBS_PATH.fullmatch(path)):
            out.append(f"{where}.path must be keys joined by dots such as 1.2, got {_short(path)}.")
        elif path and path.count(".") + 1 > MAX_DEPTH:
            out.append(f"{where}.path is deeper than {MAX_DEPTH} keys: {_short(path)}.")
    if "outcome" in o and o["outcome"] not in OUTCOMES:
        out.append(f"{where}.outcome must be one of {', '.join(OUTCOMES)}, got {_short(o['outcome'])}.")
    text = o.get("prompt_text")
    if "prompt_text" in o:
        if not isinstance(text, str):
            out.append(f"{where}.prompt_text must be text, got {_short(text)}.")
        elif len(text) > MAX_TEXT:
            out.append(f"{where}.prompt_text is {len(text)} characters; the limit is {MAX_TEXT}.")
        elif DIGITS.search(text):
            out.append(f"{where}.prompt_text still holds a run of 6 or more digits, which could be a private number.")
    secs = o.get("prompt_seconds")
    if "prompt_seconds" in o:
        if isinstance(secs, bool) or not isinstance(secs, (int, float)) or not 0 <= secs <= 120:
            out.append(f"{where}.prompt_seconds must be a number from 0 to 120, got {_short(secs)}.")
    if "heard_at" in o and not _stamp_ok(o["heard_at"]):
        out.append(f"{where}.heard_at must look like 2026-10-25T18:01:02Z, got {_short(o['heard_at'])}.")
    if "source" in o and o["source"] not in SOURCES:
        out.append(f"{where}.source must be crawl or phone, got {_short(o['source'])}.")
    if "options" in o:
        _check_options(where, o["options"], out)


def _check_options(where: str, options, out: list[str]) -> None:
    if not isinstance(options, list):
        out.append(f"{where}.options must be a list, got {_short(options)}.")
        return
    seen: set = set()
    for j, opt in enumerate(options):
        at = f"{where}.options[{j}]"
        if not isinstance(opt, dict):
            out.append(f"{at} must be an object, got {_short(opt)}.")
            continue
        _keys_exact(opt, ("key", "label"), at, out)
        key = opt.get("key")
        if "key" in opt:
            if not isinstance(key, str) or key not in KEYS:
                out.append(f"{at}.key must be one of 0-9, * or #, got {_short(key)}.")
            elif key in seen:
                out.append(f"{at}.key {_short(key)} appears twice in one menu.")
            else:
                seen.add(key)
        label = opt.get("label")
        if "label" in opt:
            if not isinstance(label, str):
                out.append(f"{at}.label must be text, got {_short(label)}.")
            elif len(label) > MAX_LABEL:
                out.append(f"{at}.label is {len(label)} characters; the limit is {MAX_LABEL}.")
            elif DIGITS.search(label):
                out.append(f"{at}.label still holds a run of 6 or more digits, which could be a private number.")


def check(relpath: str, body: bytes) -> list[str]:
    """Plain-sentence errors for one file; an empty list means it is valid."""
    out: list[str] = []
    m = PATH.fullmatch(relpath or "")
    if not m:
        out.append(f"The path {_short(relpath, 80)} must look like trees/<10 digit number>/<12 hex contributor>-<YYYYMMDDTHHMMSSZ>.json.")
    if len(body) > MAX_BYTES:
        return out + [f"The file is {len(body)} bytes; the limit is {MAX_BYTES}."]
    try:
        doc = json.loads(body.decode("utf-8"), parse_constant=_bad_constant)
    except (UnicodeDecodeError, ValueError, RecursionError) as e:
        return out + [f"The file is not valid UTF-8 JSON ({type(e).__name__})."]
    if not isinstance(doc, dict):
        return out + ["The file must hold one JSON object."]
    _keys_exact(doc, TOP_KEYS, "The file", out)
    fmt = doc.get("format")
    if "format" in doc and (isinstance(fmt, bool) or fmt != FORMAT):
        out.append(f"format must be {FORMAT}, got {_short(fmt)}.")
    number = doc.get("number")
    if "number" in doc:
        if not isinstance(number, str) or not re.fullmatch(r"\d{10}", number) or number[:3] not in TOLL_FREE:
            out.append(f"number must be a 10 digit US toll-free number (800, 888, 877, 866, 855, 844 or 833), got {_short(number)}.")
        elif m and m.group(1) != number:
            out.append(f"The folder {m.group(1)} does not match the number {number} inside the file.")
    name = doc.get("name")
    if "name" in doc:
        if not isinstance(name, str) or not name.strip():
            out.append(f"name must be a company name, got {_short(name)}.")
        elif len(name) > MAX_NAME:
            out.append(f"name is {len(name)} characters; the limit is {MAX_NAME}.")
    if "contributed_at" in doc and not _stamp_ok(doc["contributed_at"]):
        out.append(f"contributed_at must look like 2026-10-25T18:30:00Z, got {_short(doc['contributed_at'])}.")
    obs = doc.get("observations")
    if "observations" in doc:
        if not isinstance(obs, list) or not 1 <= len(obs) <= MAX_OBSERVATIONS:
            n = len(obs) if isinstance(obs, list) else _short(obs)
            out.append(f"observations must be a list of 1 to {MAX_OBSERVATIONS} entries, got {n}.")
        else:
            for i, o in enumerate(obs):
                _check_observation(i, o, out)
    _control_chars(doc, "", out)
    if len(out) > MAX_ERRORS:
        out = out[:MAX_ERRORS] + [f"{len(out) - MAX_ERRORS} more problems were not listed."]
    return out
