from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER

from work_ppt.onboard import SKIP_PH, onboard


def _delete_slides(prs: Presentation) -> None:
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        rId = sldId.get(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        )
        if rId:
            prs.part.drop_rel(rId)
        sldIdLst.remove(sldId)


def _layout_by_name(prs: Presentation, name: str):
    for layout in prs.slide_layouts:
        if layout.name == name:
            return layout
    raise KeyError(f"Layout not found: {name}")


def pick_layout(profile: dict, hint: str, slot_count: int) -> str:
    names = [l["name"] for l in profile["layouts"]]
    if hint in names:
        return hint
    aliases = {
        "cover": ["title-cover", "Title Slide"],
        "section": ["title-centered", "Section Header"],
        "title-body": ["content-centered-a", "content-centered-b", "Title and Content"],
        "two-col": ["column-2-centered", "Two Content", "Comparison"],
        "three-col": ["column-3-centered-a", "column-3", "column-3-centered-b", "column-3-centered-c"],
        "four-col": ["column-4-centered"],
        "blank": ["Blank", "master-base"],
    }
    for cand in aliases.get(hint, []):
        if cand in names:
            return cand
    # Weak master: only title + content
    if "Title and Content" in names:
        return "Title and Content"
    if "Title Slide" in names and hint == "cover":
        return "Title Slide"
    return names[0]


def _fill_placeholders(slide, slots: list[str]) -> None:
    fillable = []
    for shape in slide.placeholders:
        if shape.placeholder_format.type in SKIP_PH:
            continue
        if shape.placeholder_format.type == PP_PLACEHOLDER.PICTURE:
            continue
        fillable.append(shape)
    fillable.sort(key=lambda s: (0 if "TITLE" in str(s.placeholder_format.type) else 1, s.placeholder_format.idx))
    for shape, text in zip(fillable, slots):
        if not shape.has_text_frame:
            continue
        tf = shape.text_frame
        tf.clear()
        lines = text.split("\n")
        p0 = tf.paragraphs[0]
        p0.text = lines[0]
        for line in lines[1:]:
            p = tf.add_paragraph()
            p.text = line
            p.level = 0 if not line.startswith("- ") else 0


def compose(template: Path, plan: dict, dest: Path) -> Path:
    template = Path(template)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    profile = onboard(template)
    prs = Presentation(str(template))
    _delete_slides(prs)
    for slide_spec in plan["slides"]:
        slots = slide_spec.get("slots") or []
        hint = slide_spec.get("layout_hint") or "title-body"
        layout_name = pick_layout(profile, hint, len(slots))
        layout = _layout_by_name(prs, layout_name)
        slide = prs.slides.add_slide(layout)
        _fill_placeholders(slide, slots)
        slide_spec["resolved_layout"] = layout_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(dest))
    return dest


def load_plan(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
