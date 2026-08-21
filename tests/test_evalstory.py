from pathlib import Path

from work_ppt.evalstory import check_frozen, prompt_for
from work_ppt.gold import GOLD


def test_eval_prompt_contains_grill_answers():
    original = GOLD / "original.pptx"
    text = prompt_for("ab", original)
    assert "extract_only" in text
    assert "Do not invent numbers" in text


def test_eval_check_ab_frozen():
    result = check_frozen("ab", GOLD / "original.pptx")
    assert result["ok"] is True
    assert result["slides"] >= 8
