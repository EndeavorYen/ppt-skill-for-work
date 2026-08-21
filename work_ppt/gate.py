from __future__ import annotations

import json
import re
from pathlib import Path

REQUIRED_BRIEF = ("audience", "language", "path", "title", "decision", "sources")
ALLOWED_PATHS = ("compose", "mutate", "optimize")
NUM_RE = re.compile(r"\d+(?:[.,]\d+)?(?:%|[KkMmBbGg]B?)?")


class GateError(ValueError):
    exit_code = 2


def load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_brief(brief: dict) -> dict:
    missing = [key for key in REQUIRED_BRIEF if not brief.get(key)]
    if not brief.get("template") and not brief.get("prior_deck"):
        missing.append("template or prior_deck")
    if missing:
        raise GateError("missing brief fields: " + ", ".join(missing))
    if brief["path"] not in ALLOWED_PATHS:
        raise GateError(f"invalid path: {brief['path']}")
    return brief


def load_brief(path: Path) -> dict:
    return validate_brief(load_json(path))


def number_tokens(text: str) -> list[str]:
    return NUM_RE.findall(text)


def source_corpus(brief: dict, extra: str = "") -> str:
    parts = [extra]
    sources = brief.get("sources")
    if isinstance(sources, str):
        sources = [sources]
    for item in sources or []:
        path = Path(item)
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8"))
        else:
            parts.append(str(item))
    return "\n".join(parts)


def assert_numbers_sourced(story: dict, corpus: str) -> None:
    for index, slide in enumerate(story.get("slides") or [], start=1):
        blob = "\n".join(slide.get("slots") or [])
        for token in number_tokens(blob):
            if token not in corpus:
                raise GateError(f"unsourced number {token!r} on slide {index}")


def story_to_plan(story: dict, profile: dict) -> dict:
    from work_ppt.compose import pick_layout

    slides = []
    for slide in story.get("slides") or []:
        title = slide.get("action_title") or ""
        slots = list(slide.get("slots") or [])
        if title:
            if slots:
                slots[0] = title
            else:
                slots = [title]
        hint = slide.get("layout_hint") or "title-body"
        spec = {
            "action_title": title,
            "intent": slide.get("intent") or "",
            "layout_hint": hint,
            "slots": slots,
            "resolved_layout": pick_layout(profile, hint, len(slots)),
        }
        if slide.get("diagram"):
            spec["diagram"] = slide["diagram"]
            spec["diagram_labels"] = list(slide.get("diagram_labels") or [])
        for key in ("picture", "generate_image", "mermaid", "drawio"):
            if slide.get(key) is not None:
                spec[key] = slide[key]
        slides.append(spec)
    return {
        "title": story.get("title") or "",
        "decision": story.get("decision") or "",
        "slides": slides,
    }
