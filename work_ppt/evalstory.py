from __future__ import annotations

import json
from pathlib import Path

from work_ppt.extract import extract
from work_ppt.gate import load_json
from work_ppt.gold import GOLD, assert_ab_locked, extract_blob

ANSWERS = GOLD / "grill-answers.json"

PROMPT = """You write story.json for work-ppt. Do not invent numbers.
Case: {case}
Kind: {kind}
Grill answers (already decided; do not re-ask):
{answers}

Extract of A (the draft):
{extract}

Rules:
- Titles are full takeaway sentences and, read in order, tell the argument.
- layout_hint is one of cover, section, title-body, two-col, three-col, four-col.
- If kind is ab, every number token must appear in the extract. No 2.7 GB.
- If kind is sourced, numbers may come from docs/fixtures/source/raschka-2026-llm-architectures.md.
- No Thank You closer.
- diagram values: process, sibling, architecture, sibling-costs, decoder-callouts, csa-hca-fork.
- Do not set generate_image on process/architecture/sequence.
Write only JSON for story.json.
"""


def load_answers() -> dict:
    if not ANSWERS.is_file():
        return {}
    return json.loads(ANSWERS.read_text(encoding="utf-8"))


def prompt_for(case: str, original: Path) -> str:
    from work_ppt.gold import CASE_TABLE

    spec = CASE_TABLE[case]
    answers = load_answers().get(spec["kind"], {})
    blob = extract_blob(extract(original))
    return PROMPT.format(
        case=case,
        kind=spec["kind"],
        answers=json.dumps(answers, indent=2, ensure_ascii=False),
        extract=blob,
    )


def check_frozen(case: str, original: Path) -> dict:
    from work_ppt.gold import CASE_TABLE

    spec = CASE_TABLE[case]
    story = load_json(GOLD / spec["kind"] / "story.json")
    extracted = extract(original)
    if spec["kind"] == "ab":
        assert_ab_locked(extracted, story)
    return {"case": case, "ok": True, "slides": len(story.get("slides") or [])}
