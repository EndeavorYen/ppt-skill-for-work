from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_run(
    run_dir: Path,
    *,
    brief: dict,
    profile: dict,
    story: dict | None,
    plan: dict,
    pptx: Path,
    extra: dict | None = None,
) -> Path:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    payloads = {
        "brief.json": brief,
        "profile.json": profile,
        "plan.json": plan,
    }
    if story is not None:
        payloads["story.json"] = story
    if extra:
        payloads.update(extra)
    for name, value in payloads.items():
        (run_dir / name).write_text(
            json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    shutil.copy2(pptx, run_dir / Path(pptx).name)
    return run_dir
