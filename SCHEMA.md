# File format

`tools/community_check.py` is the authority. This page describes what it enforces;
if the two ever disagree, the code wins and this page is wrong.

## Path

`trees/<number>/<contributor>-<YYYYMMDDTHHMMSSZ>.json`

- `<number>`: 10 digits, matching `number` inside the file.
- `<contributor>`: 12 lowercase hex characters.
- The stamp is the contribution time in UTC.

Files are immutable: added once, never edited.

## Contents

```json
{"format": 1, "number": "8885550199", "name": "Acme Wireless", "contributed_at": "2026-10-25T18:30:00Z",
 "observations": [{"path": "", "prompt_text": "...", "options": [{"key": "1", "label": "billing"}],
                   "outcome": "menu", "prompt_seconds": 19.04, "heard_at": "2026-10-25T18:01:02Z", "source": "crawl"}]}
```

Exactly these top level fields, no others: `format`, `number`, `name`,
`contributed_at`, `observations`.

| Field | Limit |
|---|---|
| file | at most 262144 bytes (256 KiB), UTF-8 JSON, one object; `NaN` and `Infinity` refused |
| `format` | the integer `1` |
| `number` | 10 digits, a US toll-free prefix: 800, 888, 877, 866, 855, 844 or 833; equals the folder |
| `name` | non-empty text, at most 80 characters |
| `contributed_at` | `YYYY-MM-DDTHH:MM:SSZ`, a real date and time |
| `observations` | a list of 1 to 500 entries |

Each observation has exactly: `path`, `prompt_text`, `options`, `outcome`,
`prompt_seconds`, `heard_at`, `source`.

| Field | Limit |
|---|---|
| `path` | `""` for the top menu, otherwise keys joined by dots such as `1.2`; each key is one of 0-9, `*`, `#`; at most 6 keys deep |
| `prompt_text` | text, at most 1000 characters, no run of 6 or more digits (spaces, dots and hyphens between digits count) |
| `options` | a list of `{"key", "label"}` objects and nothing else |
| `options[].key` | one of 0-9, `*`, `#`; not repeated in one menu |
| `options[].label` | text, at most 120 characters, no run of 6 or more digits |
| `outcome` | menu, hold, human, voicemail, hangup, invalid_input, needs_input or speech_menu |
| `prompt_seconds` | a number from 0 to 120 (not a boolean) |
| `heard_at` | `YYYY-MM-DDTHH:MM:SSZ`, a real date and time |
| `source` | crawl or phone |

No string anywhere in the file, including field names, may contain a control
character (line break, tab and so on).

A failing file reports at most 20 problems, each a plain sentence naming the field.
