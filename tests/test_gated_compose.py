import json
from pathlib import Path

from work_ppt.__main__ import main
from work_ppt.extract import extract
from work_ppt.gold import TEMPLATE


def _write(path: Path, payload) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _brief(tmp: Path, sources: Path, path="compose") -> Path:
    return _write(
        tmp / "brief.json",
        {
            "audience": "mixed-room",
            "language": "zh-Hant-en-terms",
            "path": path,
            "template": str(TEMPLATE),
            "title": "Test",
            "decision": "Ship gated compose",
            "sources": [str(sources)],
        },
    )


def test_compose_rejects_missing_brief_field(tmp_path):
    brief = _write(
        tmp_path / "brief.json",
        {"audience": "x", "language": "en", "path": "compose", "title": "T"},
    )
    story = _write(tmp_path / "story.json", {"slides": [{"action_title": "Hi", "layout_hint": "cover", "slots": ["Hi"]}]})
    out = tmp_path / "out.pptx"
    code = main(
        [
            "compose",
            "--template",
            str(TEMPLATE),
            "--brief",
            str(brief),
            "--story",
            str(story),
            "-o",
            str(out),
            "--run-dir",
            str(tmp_path / "runs"),
        ]
    )
    assert code == 2
    assert not out.exists()


def test_compose_rejects_unsourced_number(tmp_path):
    sources = tmp_path / "src.md"
    sources.write_text("no figures here", encoding="utf-8")
    brief = _brief(tmp_path, sources)
    story = _write(
        tmp_path / "story.json",
        {
            "slides": [
                {
                    "action_title": "Saves 2.7 GB",
                    "layout_hint": "title-body",
                    "slots": ["Saves 2.7 GB", "from nowhere"],
                }
            ]
        },
    )
    out = tmp_path / "out.pptx"
    code = main(
        [
            "compose",
            "--template",
            str(TEMPLATE),
            "--brief",
            str(brief),
            "--story",
            str(story),
            "-o",
            str(out),
            "--run-dir",
            str(tmp_path / "runs"),
        ]
    )
    assert code == 2
    assert not out.exists()


def test_compose_writes_run_and_diagram(tmp_path):
    sources = tmp_path / "src.md"
    sources.write_text("KV cache 2.7 GB at 128K", encoding="utf-8")
    brief = _brief(tmp_path, sources)
    story = _write(
        tmp_path / "story.json",
        {
            "title": "KV",
            "decision": "share first",
            "slides": [
                {
                    "action_title": "KV cache 2.7 GB at 128K is the constraint",
                    "layout_hint": "section",
                    "slots": ["KV cache 2.7 GB at 128K is the constraint"],
                    "diagram": "process",
                    "diagram_labels": ["KV", "FLOPs", "Residual"],
                }
            ],
        },
    )
    out = tmp_path / "out.pptx"
    runs = tmp_path / "runs"
    code = main(
        [
            "compose",
            "--template",
            str(TEMPLATE),
            "--brief",
            str(brief),
            "--story",
            str(story),
            "-o",
            str(out),
            "--run-dir",
            str(runs),
        ]
    )
    assert code == 0
    assert out.exists()
    run_dirs = list(runs.iterdir())
    assert len(run_dirs) == 1
    assert (run_dirs[0] / "brief.json").exists()
    assert (run_dirs[0] / "story.json").exists()
    assert (run_dirs[0] / "plan.json").exists()
    data = extract(out)
    assert any("Rounded Rectangle" in (b.get("shape") or "") for s in data["slides"] for b in s["blocks"])
    assert data["slides"][0]["blocks"][0]["text"].startswith("KV cache")
