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

Missing any field → ask, do not render. CLI compose / optimize / mutate exit 2 and write no pptx.

## Commands

```bash
python -m work_ppt onboard <template.pptx> -o profiles/<id>.json
python -m work_ppt extract <deck.pptx> -o extract.json
python -m work_ppt plan --brief B.json --story S.json --template T.pptx -o plan.json
python -m work_ppt compose --brief B.json --story S.json --template T.pptx -o out.pptx
python -m work_ppt optimize DECK.pptx --brief B.json --story S.json -o out.pptx
python -m work_ppt mutate DECK.pptx --brief B.json --story S.json -o out.pptx
python -m work_ppt qa DECK.pptx -o qa.json
python -m work_ppt gold-baseline -o eval/gold/original.pptx
python -m work_ppt gold-optimize --case all
python -m work_ppt gold-review --case ab
python -m work_ppt eval-prompt --case ab
python -m work_ppt eval-check --case ab
python -m work_ppt preview DECK.pptx -o preview.png
```

Onboard is once per template and sits outside the 10–15 minute draft SLA.

`--plan` may replace `--story` when layouts are already resolved. Compose still requires `--brief`.

## Story freeze (do this before compose)

Write `story.json` whose titles, read in order, tell the whole argument (ghost deck). Each title is a full takeaway sentence, not a topic label. Every number must appear in `sources` or `extract.json`. If a number is missing, stop.

Map each slide to a `layout_hint`: `cover` | `section` | `title-body` | `two-col` | `three-col` | `four-col`. Scripts resolve hints to **actual layout names** from the profile. If the master cannot host the hint (weak template), they downgrade to Title and Content / a table. Never draw a new master.

`diagram` values: `process` | `sequence` | `sibling` | `architecture` | `sibling-costs` | `decoder-callouts` | `csa-hca-fork`.

## Paths

- `compose` — new deck from onboarded template + sources.
- `optimize` — the `.pptx` is **both** master and source. Extract → story → compose onto the same file's layouts.
- `mutate` — surgical text/data edits on existing slides. If more than 30% of slides would change layout, exit 2 and use optimize.

## Draft vs polish

Draft (10–15 min): story + compose + native diagrams. No screenshot loop. Do not generate flowcharts or architecture as images.

Polish (≤30 min, after freeze): `python -m work_ppt qa` (`officecli view issues`), `officecli view <file> screenshot`, overflow. Second language is polish-only text rewrite; there is no translator CLI.

Each compose / optimize / mutate writes `runs/<UTC>/` with brief, profile, story, plan, and pptx.

## Gold test

Shared A: `eval/gold/original.pptx`. Two frozen B decks grown from that file:

- `eval/gold/ab/` — Inner Chapter, no extra source.
- `eval/gold/sourced/` — Inner Chapter + Raschka notes.
- Families in gold: `light/` and `dark/` each with `ab/` and `sourced/`. Impoverished (two-layout) masters are **not** a gold case; only unit-test that hints downgrade and no master is invented.

pytest does not call a model. Internal eval: `eval-prompt` / `eval-check` and `.grok/workflows/gold-eval-story.rhai` with `eval/gold/grill-answers.json`. Copy a new story into git only after review.

Slide fields: `picture` (existing file), `mermaid` (OfficeCLI native diagram), `drawio` (SVG or draw.io CLI export). `generate_image` on process/architecture/sequence exits 2.

Gold B: native shapes plus optional real image files named in the plan. No generated images. Product final decks may include generated images that are **not** flowcharts or architecture; those two kinds must stay editable.

## Diagrams

Architecture / process / sequence → native shapes (`work_ppt.diagrams`). Raster flowcharts are a defect. Product final decks may use generated images only when the image is not a process/architecture/sequence diagram. Real photos/screenshots only when the plan names an existing file.
