from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


class QaError(RuntimeError):
    exit_code = 3


def qa(deck: Path, dest: Path, officecli: str = "officecli") -> Path:
    deck = Path(deck)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    binary = shutil.which(officecli)
    if not binary:
        raise QaError("officecli missing")
    try:
        raw = subprocess.check_output(
            [binary, "view", str(deck), "issues", "--json"],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        raise QaError(exc.output or str(exc)) from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {"raw": raw}
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest


def screenshot(deck: Path, dest: Path, officecli: str = "officecli") -> Path:
    deck = Path(deck)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    binary = shutil.which(officecli)
    if not binary:
        raise QaError("officecli missing")
    try:
        subprocess.check_output(
            [
                binary,
                "view",
                str(deck),
                "screenshot",
                "-o",
                str(dest),
                "--grid",
                "auto",
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        raise QaError(exc.output or str(exc)) from exc
    if not dest.exists():
        raise QaError(f"screenshot not written: {dest}")
    return dest
