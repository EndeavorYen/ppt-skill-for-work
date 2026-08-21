from pathlib import Path

import pytest
from PIL import Image

from work_ppt.compose import compose
from work_ppt.gate import GateError
from work_ppt.gold import TEMPLATE


def _png(path: Path) -> Path:
    Image.new("RGB", (8, 8), (0, 68, 121)).save(path)
    return path


def test_generate_image_cannot_replace_flowchart(tmp_path):
    png = _png(tmp_path / "flow.png")
    plan = {
        "slides": [
            {
                "layout_hint": "section",
                "slots": ["A process"],
                "diagram": "process",
                "diagram_labels": ["A", "B"],
                "generate_image": str(png),
            }
        ]
    }
    with pytest.raises(GateError, match="generated images cannot replace"):
        compose(TEMPLATE, plan, tmp_path / "out.pptx")


def test_picture_inserts(tmp_path):
    png = _png(tmp_path / "real.png")
    plan = {
        "slides": [
            {
                "layout_hint": "title-body",
                "slots": ["Provided photo"],
                "picture": str(png),
            }
        ]
    }
    dest = compose(TEMPLATE, plan, tmp_path / "pic.pptx")
    assert dest.exists()
