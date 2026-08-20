from __future__ import annotations

import argparse
import json
from pathlib import Path

from work_ppt.compose import compose, load_plan
from work_ppt.extract import extract, save_extract
from work_ppt.gold import TEMPLATE, build_optimized, build_original
from work_ppt.onboard import onboard, save_profile


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="work_ppt")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("onboard")
    s.add_argument("template")
    s.add_argument("-o", required=True)

    s = sub.add_parser("extract")
    s.add_argument("deck")
    s.add_argument("-o", required=True)

    s = sub.add_parser("compose")
    s.add_argument("--template", required=True)
    s.add_argument("--plan", required=True)
    s.add_argument("-o", required=True)

    s = sub.add_parser("gold-baseline")
    s.add_argument("-o", default="eval/gold/original.pptx")

    s = sub.add_parser("optimize")
    s.add_argument("deck", help="Deck that is both master and source")
    s.add_argument("--plan", required=True)
    s.add_argument("-o", required=True)

    s = sub.add_parser("gold-optimize")
    s.add_argument("--template", default="")
    s.add_argument("-o", default="eval/gold/optimized.pptx")

    args = p.parse_args(argv)
    if args.cmd == "onboard":
        profile = onboard(Path(args.template))
        save_profile(profile, Path(args.o))
        print(json.dumps({"layouts": profile["layout_count"], "out": args.o}))
    elif args.cmd == "extract":
        data = extract(Path(args.deck))
        save_extract(data, Path(args.o))
        print(json.dumps({"slides": data["slide_count"], "out": args.o}))
    elif args.cmd == "compose":
        compose(Path(args.template), load_plan(Path(args.plan)), Path(args.o))
        print(args.o)
    elif args.cmd == "optimize":
        compose(Path(args.deck), load_plan(Path(args.plan)), Path(args.o))
        print(args.o)
    elif args.cmd == "gold-baseline":
        print(build_original(Path(args.o)))
    elif args.cmd == "gold-optimize":
        template = Path(args.template) if args.template else Path("eval/gold/original.pptx")
        if not template.exists():
            template = TEMPLATE
        print(build_optimized(Path(args.o), template))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
