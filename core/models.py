from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class KanjiStroke: # Single stroke path and its optional KanjiVG metadata.

    id: str
    d: str
    stroke_type: Optional[str] = None


@dataclass(slots=True)
class KanjiGroup: # Hierarchical stroke group from kanjivg metadata

    id: str
    element: Optional[str] = None
    original: Optional[str] = None
    part: Optional[int] = None
    number: Optional[int] = None
    variant: Optional[bool] = None
    partial: Optional[bool] = None
    trad_form: Optional[bool] = None
    radical_form: Optional[bool] = None
    position: Optional[str] = None
    radical: Optional[str] = None
    phon: Optional[str] = None
    groups: list["KanjiGroup"] = field(default_factory=list)
    strokes: list[KanjiStroke] = field(default_factory=list)


@dataclass(slots=True)
class ParsedKanjiSvg: # Parsed KanjiVG data needed for animation and validation.

    codepoint_hex: str
    root_group: KanjiGroup
    ordered_strokes: list[KanjiStroke]
