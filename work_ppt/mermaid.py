from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from work_ppt.gate import GateError
from work_ppt.qa import QaError


def add_mermaid(deck: Path, slide_index: int, source: str, officecli: str = "officecli") -> None:
    binary = shutil.which(officecli)
    if not binary:
        raise QaError("officecli missing")
    path = f"/slide[{slide_index}]"
    try:
        subprocess.check_output(
            [
                binary,
                "add",
                str(deck),
                path,
                "--type",
                "diagram",
                "--prop",
                f"mermaid={source}",
                "--prop",
                "render=native",
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        raise QaError(exc.output or str(exc)) from exc


def export_drawio(source: Path, dest_svg: Path) -> Path:
    exe = shutil.which("draw.io") or shutil.which("drawio")
    if not exe:
        raise GateError("draw.io CLI missing; export an SVG and set picture= on the slide")
    dest_svg = Path(dest_svg)
    dest_svg.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_output(
        [exe, "-x", "-f", "svg", "-o", str(dest_svg), str(source)],
        text=True,
        stderr=subprocess.STDOUT,
    )
    return dest_svg
