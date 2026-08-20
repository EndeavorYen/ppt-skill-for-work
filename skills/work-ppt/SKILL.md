---
name: work-ppt
description: >
  Build or optimize a work technical-report PowerPoint from a user template.
  Use when the user wants a deck, readout, 技術報告, or to improve an existing
  .pptx while keeping its master. Do not invent layouts or numbers.
---

# Work PPT

Agent writes the story. Scripts fill the user's real slide layouts.

## Refuse until brief is complete

Required: `audience`, `language`, `path` (`compose` | `mutate` | `optimize`), `template` or `prior_deck`, `title`, `decision`, `sources`.

Missing any field → ask, do not render.

## Commands

```bash
python -m work_ppt onboard <template.pptx> -o profiles/<id>.json
python -m work_ppt extract <deck.pptx> -o extract.json
python -m work_ppt compose --template T.pptx --plan slide_plan.json -o out.pptx
python -m work_ppt gold-baseline -o eval/gold/original.pptx
python -m work_ppt gold-optimize -o eval/gold/optimized.pptx
```

Onboard is once per template and sits outside the 10–15 minute draft SLA.

## Story freeze (do this before compose)

Write `story.json` whose titles, read in order, tell the whole argument (ghost deck). Each title is a full takeaway sentence, not a topic label. Every number must appear in `sources` or `extract.json`. If a number is missing, stop.

Map each slide to a `layout_hint`: `cover` | `section` | `title-body` | `two-col` | `three-col` | `four-col`. Scripts resolve hints to **actual layout names** from the profile. If the master cannot host the hint (weak template), they downgrade to Title and Content / a table. Never draw a new master.

## Paths

- `compose` — new deck from onboarded template + sources.
- `optimize` — the `.pptx` is **both** master and source. Extract → story → compose onto the same file's layouts.
- `mutate` — surgical text/data edits; do not rebuild layouts unless >30% of slides change.

## Diagrams

Architecture / process / sequence → native shapes (`work_ppt.diagrams`) or OfficeCLI mermaid. Raster flowcharts are a defect. Generate images only in polish, and only when no required readable text.

## Draft vs polish

Draft (10–15 min): story + compose + native diagrams. No image model, no screenshot loop.

Polish (≤30 min, after freeze): `officecli view <file> issues`, `officecli view <file> screenshot`, overflow, second language (text only).

## Gold test

`eval/gold/original.pptx` vs `eval/gold/optimized.pptx`. Same Inner Chapter master. Optimized must win format, layout, narrative, technical depth, logic, and story flow. Same visual system. No Thank You closer.
