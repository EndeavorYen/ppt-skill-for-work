import json
from pathlib import Path

from work_ppt.__main__ import main
from work_ppt.extract import extract
from work_ppt.gold import build_original

REPO = Path(__file__).resolve().parents[1]


def test_mutate_refuses_layout_rebuild(tmp_path):
    original = build_original(tmp_path / "original.pptx")
    sources = tmp_path / "src.md"
    sources.write_text(REPO.joinpath("docs/fixtures/source/raschka-2026-llm-architectures.md").read_text(encoding="utf-8"), encoding="utf-8")
    brief = {
        "audience": "mixed-room",
        "language": "zh-Hant-en-terms",
        "path": "mutate",
        "prior_deck": str(original),
        "title": "T",
        "decision": "D",
        "sources": [str(sources)],
    }
    (tmp_path / "brief.json").write_text(json.dumps(brief), encoding="utf-8")
    src = extract(original)
    slides = []
    for slide in src["slides"]:
        title = next((b["text"] for b in slide["blocks"] if b["role"] == "title"), "X")
        slides.append(
            {
                "action_title": title,
                "layout_hint": "three-col",
                "slots": [title, "a", "b"],
            }
        )
    (tmp_path / "story.json").write_text(json.dumps({"slides": slides}), encoding="utf-8")
    out = tmp_path / "mut.pptx"
    code = main(
        [
            "mutate",
            str(original),
            "--brief",
            str(tmp_path / "brief.json"),
            "--story",
            str(tmp_path / "story.json"),
            "-o",
            str(out),
            "--run-dir",
            str(tmp_path / "runs"),
        ]
    )
    assert code == 2
    assert not out.exists()


def test_mutate_patches_text_on_same_layouts(tmp_path):
    original = build_original(tmp_path / "original.pptx")
    sources = tmp_path / "src.md"
    sources.write_text("LLM Architecture Update", encoding="utf-8")
    brief = {
        "audience": "mixed-room",
        "language": "en",
        "path": "mutate",
        "prior_deck": str(original),
        "title": "T",
        "decision": "D",
        "sources": [str(sources)],
    }
    (tmp_path / "brief.json").write_text(json.dumps(brief), encoding="utf-8")
    src = extract(original)
    first = src["slides"][0]
    title = first["blocks"][0]["text"]
    story = {
        "slides": [
            {
                "action_title": title,
                "layout_hint": first["layout"],
                "slots": [title, "patched subtitle", "Internal sharing"],
            }
        ]
    }
    (tmp_path / "story.json").write_text(json.dumps(story), encoding="utf-8")
    out = tmp_path / "mut.pptx"
    code = main(
        [
            "mutate",
            str(original),
            "--brief",
            str(tmp_path / "brief.json"),
            "--story",
            str(tmp_path / "story.json"),
            "-o",
            str(out),
            "--run-dir",
            str(tmp_path / "runs"),
        ]
    )
    assert code == 0
    patched = extract(out)
    assert patched["slide_count"] == src["slide_count"]
    assert patched["slides"][0]["layout"] == first["layout"]
    assert any("patched subtitle" in b["text"] for b in patched["slides"][0]["blocks"])
