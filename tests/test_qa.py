from pathlib import Path

from work_ppt.__main__ import main
from work_ppt.gold import build_original
from work_ppt.qa import QaError, qa


def test_qa_writes_json(tmp_path):
    deck = build_original(tmp_path / "original.pptx")
    dest = tmp_path / "qa.json"
    try:
        qa(deck, dest)
    except QaError:
        code = main(["qa", str(deck), "-o", str(dest)])
        assert code == 3
        return
    assert dest.exists()
    assert dest.read_text(encoding="utf-8").strip().startswith("{")
