from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from core.models import KanjiGroup, KanjiStroke, ParsedKanjiSvg

SVG_NS = "http://www.w3.org/2000/svg"
KVG_NS = "http://kanjivg.tagaini.net"
NS = {"svg": SVG_NS, "kvg": KVG_NS}


class KanjiVGParseError(Exception):
    """Raised when an SVG does not match expected KanjiVG structure."""


def parse_kanjivg_svg(svg_path: str | Path) -> ParsedKanjiSvg:
    """Parse a KanjiVG SVG into a hierarchy and an ordered stroke list."""

    path = Path(svg_path)
    tree = ET.parse(path)
    root = tree.getroot()

    stroke_paths_root = None
    for g in root.findall(".//svg:g", NS):
        gid = g.attrib.get("id", "")
        if gid.startswith("kvg:StrokePaths_"):
            stroke_paths_root = g
            break

    if stroke_paths_root is None:
        raise KanjiVGParseError(f"Could not find StrokePaths root in {path}")

    codepoint_hex = stroke_paths_root.attrib["id"].split("_", 1)[1].split("-", 1)[0]

    ordered_strokes: list[KanjiStroke] = []
    parsed_root = _parse_group(stroke_paths_root, ordered_strokes)

    return ParsedKanjiSvg(
        codepoint_hex=codepoint_hex,
        root_group=parsed_root,
        ordered_strokes=ordered_strokes,
    )


def _parse_group(group_el: ET.Element, ordered_strokes: list[KanjiStroke]) -> KanjiGroup:
    group = KanjiGroup(
        id=group_el.attrib.get("id", ""),
        element=group_el.attrib.get(f"{{{KVG_NS}}}element"),
        original=group_el.attrib.get(f"{{{KVG_NS}}}original"),
        part=_to_int(group_el.attrib.get(f"{{{KVG_NS}}}part")),
        number=_to_int(group_el.attrib.get(f"{{{KVG_NS}}}number")),
        variant=_to_bool(group_el.attrib.get(f"{{{KVG_NS}}}variant")),
        partial=_to_bool(group_el.attrib.get(f"{{{KVG_NS}}}partial")),
        trad_form=_to_bool(group_el.attrib.get(f"{{{KVG_NS}}}tradForm")),
        radical_form=_to_bool(group_el.attrib.get(f"{{{KVG_NS}}}radicalForm")),
        position=group_el.attrib.get(f"{{{KVG_NS}}}position"),
        radical=group_el.attrib.get(f"{{{KVG_NS}}}radical"),
        phon=group_el.attrib.get(f"{{{KVG_NS}}}phon"),
    )

    for child in list(group_el):
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "g":
            group.groups.append(_parse_group(child, ordered_strokes))
        elif tag == "path":
            stroke = KanjiStroke(
                id=child.attrib.get("id", ""),
                d=child.attrib.get("d", ""),
                stroke_type=child.attrib.get(f"{{{KVG_NS}}}type"),
            )
            group.strokes.append(stroke)
            ordered_strokes.append(stroke)

    return group


def _to_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() == "true"


def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    return int(value)
