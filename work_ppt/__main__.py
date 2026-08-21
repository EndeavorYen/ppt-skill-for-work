from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from work_ppt.compose import compose, load_plan
from work_ppt.extract import extract, save_extract
from work_ppt.gate import (
    GateError,
    assert_numbers_sourced,
    load_brief,
    load_json,
    source_corpus,
    story_to_plan,
)
from work_ppt.evalstory import check_frozen, prompt_for
from work_ppt.gold import (
    CASES,
    CASE_ORDER,
    CASE_TABLE,
    GOLD,
    build_case,
    build_family_original,
    build_original,
    case_dir,
    family_original_path,
    gold_review,
)
from work_ppt.mutate import mutate
from work_ppt.onboard import onboard, save_profile
from work_ppt.qa import QaError, qa, screenshot
from work_ppt.runlog import new_run_id, write_run


def _require_brief(args) -> dict:
    if not getattr(args, "brief", None):
        raise GateError("missing --brief")
    return load_brief(Path(args.brief))


def _plan_from_args(args, template: Path, extra_corpus: str = "") -> tuple[dict, dict | None, dict]:
    brief = _require_brief(args)
    profile = onboard(template)
    story = None
    if getattr(args, "story", None):
        story = load_json(Path(args.story))
        corpus = source_corpus(brief, extra_corpus)
        assert_numbers_sourced(story, corpus)
        plan = story_to_plan(story, profile)
    elif getattr(args, "plan", None):
        plan = load_plan(Path(args.plan))
    else:
        raise GateError("missing --story or --plan")
    return brief, story, plan


def _persist(args, brief, profile, story, plan, pptx: Path) -> None:
    run_root = Path(getattr(args, "run_dir", None) or "runs")
    write_run(
        run_root / new_run_id(),
        brief=brief,
        profile=profile,
        story=story,
        plan=plan,
        pptx=pptx,
    )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="work_ppt")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("onboard")
    s.add_argument("template")
    s.add_argument("-o", required=True)

    s = sub.add_parser("extract")
    s.add_argument("deck")
    s.add_argument("-o", required=True)

    s = sub.add_parser("plan")
    s.add_argument("--brief", required=True)
    s.add_argument("--story", required=True)
    s.add_argument("--template", required=True)
    s.add_argument("-o", required=True)

    s = sub.add_parser("compose")
    s.add_argument("--template", required=True)
    s.add_argument("--brief", required=True)
    s.add_argument("--story")
    s.add_argument("--plan")
    s.add_argument("-o", required=True)
    s.add_argument("--run-dir", default="runs")

    s = sub.add_parser("optimize")
    s.add_argument("deck")
    s.add_argument("--brief", required=True)
    s.add_argument("--story")
    s.add_argument("--plan")
    s.add_argument("-o", required=True)
    s.add_argument("--run-dir", default="runs")

    s = sub.add_parser("mutate")
    s.add_argument("deck")
    s.add_argument("--brief", required=True)
    s.add_argument("--story")
    s.add_argument("--plan")
    s.add_argument("-o", required=True)
    s.add_argument("--run-dir", default="runs")

    s = sub.add_parser("qa")
    s.add_argument("deck")
    s.add_argument("-o", required=True)
    s.add_argument("--screenshot")

    s = sub.add_parser("preview")
    s.add_argument("deck")
    s.add_argument("-o", required=True)

    s = sub.add_parser("eval-prompt")
    s.add_argument("--case", choices=list(CASES), default="ab")
    s.add_argument("--original", default="eval/gold/original.pptx")

    s = sub.add_parser("eval-check")
    s.add_argument("--case", choices=list(CASES), default="ab")
    s.add_argument("--original", default="eval/gold/original.pptx")

    s = sub.add_parser("gold-baseline")
    s.add_argument("-o", default="eval/gold/original.pptx")
    s.add_argument("--family", default="inner")

    s = sub.add_parser("gold-optimize")
    s.add_argument("--case", choices=list(CASES) + ["all"], default="all")
    s.add_argument("--original", default="eval/gold/original.pptx")

    s = sub.add_parser("gold-review")
    s.add_argument("--case", choices=list(CASES), default="sourced")
    s.add_argument("--original", default="")
    s.add_argument("--optimized", default="")
    s.add_argument("-o", default="")

    args = p.parse_args(argv)
    try:
        return _dispatch(args)
    except GateError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code
    except QaError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code


def _dispatch(args) -> int:
    if args.cmd == "onboard":
        profile = onboard(Path(args.template))
        save_profile(profile, Path(args.o))
        print(json.dumps({"layouts": profile["layout_count"], "out": args.o}))
    elif args.cmd == "extract":
        data = extract(Path(args.deck))
        save_extract(data, Path(args.o))
        print(json.dumps({"slides": data["slide_count"], "out": args.o}))
    elif args.cmd == "plan":
        brief, story, plan = _plan_from_args(args, Path(args.template))
        Path(args.o).parent.mkdir(parents=True, exist_ok=True)
        Path(args.o).write_text(
            json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(args.o)
    elif args.cmd == "compose":
        template = Path(args.template)
        brief, story, plan = _plan_from_args(args, template)
        dest = compose(template, plan, Path(args.o))
        _persist(args, brief, onboard(template), story, plan, dest)
        print(dest)
    elif args.cmd == "optimize":
        deck = Path(args.deck)
        extracted = extract(deck)
        brief, story, plan = _plan_from_args(
            args, deck, extra_corpus=json.dumps(extracted, ensure_ascii=False)
        )
        dest = compose(deck, plan, Path(args.o))
        _persist(args, brief, onboard(deck), story, plan, dest)
        print(dest)
    elif args.cmd == "mutate":
        deck = Path(args.deck)
        extracted = extract(deck)
        brief, story, plan = _plan_from_args(
            args, deck, extra_corpus=json.dumps(extracted, ensure_ascii=False)
        )
        dest = mutate(deck, plan, Path(args.o))
        _persist(args, brief, onboard(deck), story, plan, dest)
        print(dest)
    elif args.cmd == "qa":
        dest = qa(Path(args.deck), Path(args.o))
        if args.screenshot:
            screenshot(Path(args.deck), Path(args.screenshot))
        print(dest)
    elif args.cmd == "preview":
        print(screenshot(Path(args.deck), Path(args.o)))
    elif args.cmd == "eval-prompt":
        original = Path(args.original)
        if not original.exists():
            original = build_original(GOLD / "original.pptx")
        print(prompt_for(args.case, original))
    elif args.cmd == "eval-check":
        original = Path(args.original)
        if not original.exists():
            original = build_original(GOLD / "original.pptx")
        print(json.dumps(check_frozen(args.case, original)))
    elif args.cmd == "gold-baseline":
        dest = build_family_original(args.family, Path(args.o))
        if args.family == "inner":
            save_extract(extract(dest), GOLD / "original.extract.json")
        print(dest)
    elif args.cmd == "gold-optimize":
        inner = Path(args.original)
        if not inner.exists():
            inner = build_original(GOLD / "original.pptx")
            save_extract(extract(inner), GOLD / "original.extract.json")
        names = CASE_ORDER if args.case == "all" else (args.case,)
        written = []
        for name in names:
            spec = CASE_TABLE[name]
            orig = inner if spec["family"] == "inner" else None
            dest = build_case(name, orig)
            family_orig = family_original_path(spec["family"])
            folder = case_dir(name)
            review = gold_review(
                family_orig,
                dest,
                folder / "blind_review.json",
                family=spec["family"],
            )
            save_extract(extract(dest), folder / "optimized.extract.json")
            written.append({"case": name, "out": str(dest), "pass": review["pass"]})
        print(json.dumps(written, ensure_ascii=False))
    elif args.cmd == "gold-review":
        spec = CASE_TABLE[args.case]
        optimized = (
            Path(args.optimized) if args.optimized else case_dir(args.case) / "optimized.pptx"
        )
        original = Path(args.original) if args.original else family_original_path(spec["family"])
        out = Path(args.o) if args.o else case_dir(args.case) / "blind_review.json"
        payload = gold_review(original, optimized, out, family=spec["family"])
        print(json.dumps({"pass": payload["pass"], "out": str(out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
