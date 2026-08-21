from pathlib import Path

import pytest

from work_ppt.extract import extract
from work_ppt.gold import CASE_TABLE, build_case, extract_blob, gold_review
from work_ppt.onboard import onboard

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("case", ["weak-ab", "light-ab", "dark-ab"])
def test_ab_families_do_not_invent_master(case, tmp_path):
    dest = tmp_path / f"{case}.pptx"
    out = build_case(case, dest=dest)
    spec = CASE_TABLE[case]
    family_orig = REPO / "eval" / "gold" / spec["family"] / "original.pptx"
    if spec["family"] == "inner":
        family_orig = REPO / "eval" / "gold" / "original.pptx"
    review = gold_review(family_orig, out, tmp_path / "review.json", family=spec["family"])
    assert review["structural"]["no_invented_master"]
    assert review["structural"]["no_thank_you"]
    got = extract(out)
    names = {layout["name"] for layout in onboard(family_orig)["layouts"]}
    assert {slide["layout"] for slide in got["slides"]} <= names
    if spec["family"] == "weak":
        assert {slide["layout"] for slide in got["slides"]} <= {"Title Slide", "Title and Content"}
        assert review["pass"]


@pytest.mark.parametrize("case", ["light-sourced", "dark-sourced", "weak-sourced"])
def test_sourced_families_deeper_and_same_master(case, tmp_path):
    dest = tmp_path / f"{case}.pptx"
    out = build_case(case, dest=dest)
    spec = CASE_TABLE[case]
    family_orig = REPO / "eval" / "gold" / spec["family"] / "original.pptx"
    review = gold_review(family_orig, out, tmp_path / "review.json", family=spec["family"])
    assert review["same_template"]
    assert "2.7" in extract_blob(extract(out))
    if spec["family"] == "weak":
        assert {s["layout"] for s in extract(out)["slides"]} <= {"Title Slide", "Title and Content"}
        assert review["pass"]
    else:
        assert review["pass"]
