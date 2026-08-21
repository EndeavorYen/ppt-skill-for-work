from pathlib import Path

from work_ppt.extract import extract
from work_ppt.gate import number_tokens
from work_ppt.gold import (
    assert_ab_locked,
    build_case,
    build_original,
    extract_blob,
    gold_review,
    load_json,
    story_blob,
)

REPO = Path(__file__).resolve().parents[1]
GOLD = REPO / "eval/gold"


def _numbers(blob: str) -> set[str]:
    return set(number_tokens(blob))


def test_frozen_ab_story_is_locked_to_original_facts():
    original = extract(GOLD / "original.pptx") if (GOLD / "original.pptx").exists() else None
    if original is None:
        return
    story = load_json(GOLD / "ab" / "story.json")
    assert_ab_locked(original, story)
    assert "Thank You" not in " ".join(
        slide.get("action_title") or "" for slide in story["slides"]
    )
    assert "2.7" not in story_blob(story)


def test_ab_grows_from_original_without_new_numbers(tmp_path):
    original = build_original(tmp_path / "original.pptx")
    out = build_case("ab", original, tmp_path / "ab.pptx")
    src = extract(original)
    got = extract(out)
    titles = " ".join(
        b["text"] for s in got["slides"] for b in s["blocks"] if b["role"] == "title"
    )
    assert "Thank You" not in titles
    assert _numbers(extract_blob(got)) <= _numbers(extract_blob(src))
    assert any("Rounded Rectangle" in (b.get("shape") or "") for s in got["slides"] for b in s["blocks"])
    review = gold_review(original, out, tmp_path / "ab-review.json")
    assert review["same_template"]
    assert review["structural"]["no_thank_you"]
    assert review["structural"]["has_native_shapes"]


def test_sourced_is_deeper_than_original(tmp_path):
    original = build_original(tmp_path / "original.pptx")
    out = build_case("sourced", original, tmp_path / "sourced.pptx")
    src = extract(original)
    got = extract(out)
    assert got["slide_count"] >= src["slide_count"]
    assert "Thank You" not in extract_blob(got)
    assert "2.7" in extract_blob(got)
    assert len(_numbers(extract_blob(got))) > len(_numbers(extract_blob(src)))
    review = gold_review(original, out, tmp_path / "sourced-review.json")
    assert review["pass"]
