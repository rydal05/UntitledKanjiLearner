# UntitledKanjiLearner
[Untitled Kanji Learner] is a crossplatform software aimed to help users learn stroke order for the characters in the Japanese language from N5 all the way to N1.

## Data source strategy (no bundled SVGs in repo)

KanjiVG already ships release zips intended for consumers:

- `*-main.zip`: non-variant SVG files (recommended default)
- `*-all.zip`: includes variants

This project now uses `core/kanjivg_source.py` to:

1. query latest release from GitHub API,
2. download the selected zip,
3. extract it into a local cache folder outside this repository,
4. return the local `kanji/` directory path for runtime use.

Default cache location:

`~/.cache/untitled_kanji_learner/kanjivg/<release-tag>/<main-or-all>/kanji/`

That keeps your git repo small while still making SVG files available locally.

## SVG metadata parsing strategy

KanjiVG embeds metadata in namespaced attributes, mainly under `kvg:`.

Implemented parser: `core/kanjivg_parser.py`

- Finds `kvg:StrokePaths_XXXXX` root group.
- Walks nested `<g>` groups and `<path>` elements.
- Preserves stroke order exactly as path traversal order.
- Extracts key attributes:
	- groups: `kvg:element`, `kvg:original`, `kvg:part`, `kvg:number`, `kvg:position`, `kvg:radical`, `kvg:phon`, etc.
	- strokes: `d`, `kvg:type`

Data models are in `core/models.py` (`ParsedKanjiSvg`, `KanjiGroup`, `KanjiStroke`).

## Suggested project delegation

- `core/`: business logic
	- data source sync (`kanjivg_source.py`)
	- metadata parsing (`kanjivg_parser.py`)
	- practice/validation logic (next)
- `ui/`: rendering, interaction, animation timing
	- canvas and input widgets
	- stroke hint overlays (start/end markers)
- `db/`: user progress and review scheduling
	- SQLite schema and repository functions
	- due-card queries (Anki-style)
- `data/`: static project-owned assets only
	- JLPT mapping tables
	- pronunciation/meaning dictionaries (if licenses allow)

## Immediate next implementation steps

1. Build a `StrokeSession` service in `core/` that tracks expected stroke index.
2. Convert user pen input to polylines and compare against expected stroke path tolerance.
3. In `ui/`, reveal one stroke at a time and show start/end markers for the current expected stroke.
4. Add `db/` persistence for per-kanji accuracy, ease score, and next review date.

## License note

KanjiVG is licensed under CC BY-SA 3.0. If you distribute this app or derived assets, include attribution and comply with share-alike requirements.
