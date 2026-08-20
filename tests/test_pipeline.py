from pathlib import Path

from work_ppt.compose import pick_layout
from work_ppt.extract import extract
from work_ppt.gold import TEMPLATE, build_optimized, build_original
from work_ppt.onboard import onboard

REPO = Path(__file__).resolve().parents[1]


def test_onboard_inner_chapter():
    profile = onboard(TEMPLATE)
    assert profile["layout_count"] >= 20
    names = {l["name"] for l in profile["layouts"]}
    assert "title-cover" in names
    assert "column-3" in names


def test_onboard_impoverished_has_two_layouts():
    profile = onboard(REPO / "docs/fixtures/templates/impoverished-title-content.pptx")
    assert profile["layout_count"] == 2
    chosen = pick_layout(profile, "three-col", 3)
    assert chosen in {"Title and Content", "Title Slide"}


def test_gold_original_and_optimized(tmp_path):
    original = build_original(tmp_path / "original.pptx")
    optimized = build_optimized(tmp_path / "optimized.pptx")
    src = extract(original)
    out = extract(optimized)
    assert src["slide_count"] >= 8
    assert out["slide_count"] >= src["slide_count"]
    titles = " ".join(
        b["text"]
        for s in out["slides"]
        for b in s["blocks"]
        if b["role"] == "title"
    )
    assert "Thank You" not in titles
    assert "KV" in titles or "KV" in " ".join(
        b["text"] for s in out["slides"] for b in s["blocks"]
    )
