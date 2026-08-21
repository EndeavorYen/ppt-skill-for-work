from pathlib import Path

from work_ppt.compose import compose, pick_layout
from work_ppt.gate import story_to_plan
from work_ppt.onboard import onboard

REPO = Path(__file__).resolve().parents[1]
TEMPLATES = REPO / "docs/fixtures/templates"

STORY = {
    "slides": [
        {"action_title": "Cover takeaway", "layout_hint": "cover", "slots": ["Cover takeaway", "subtitle"]},
        {
            "action_title": "Three facts in a row",
            "layout_hint": "three-col",
            "slots": ["Three facts in a row", "A", "B", "C"],
        },
    ]
}


def test_four_templates_compose(tmp_path):
    files = {
        "inner": TEMPLATES / "dense-consulting-inner-chapter.pptx",
        "light": TEMPLATES / "light-corporate-office-default.pptx",
        "dark": TEMPLATES / "dark-tech-navy.pptx",
        "weak": TEMPLATES / "impoverished-title-content.pptx",
    }
    for name, path in files.items():
        profile = onboard(path)
        plan = story_to_plan(STORY, profile)
        dest = compose(path, plan, tmp_path / f"{name}.pptx")
        assert dest.exists()
        if name == "weak":
            assert plan["slides"][1]["resolved_layout"] in {"Title and Content", "Title Slide"}
        if name == "inner":
            assert "column-3" in plan["slides"][1]["resolved_layout"]


def test_impoverished_three_col_downgrades():
    profile = onboard(TEMPLATES / "impoverished-title-content.pptx")
    assert pick_layout(profile, "three-col", 3) in {"Title and Content", "Title Slide"}
