# Blind review (v0, text extract + OfficeCLI issues)

Reviewer evidence: `original.extract.json`, `optimized.extract.json`, `officecli view issues` on optimized (0 issues).

## same_template

**Yes.** Both decks resolve Inner Chapter layouts: `title-cover`, `content-centered-a`, `column-2-centered`. Optimized additionally uses `title-centered` and `column-4-centered` from the same master (layouts 02 and 31 in the template profile). Theme is not swapped.

## Dimensions

| Dimension | Winner | Evidence |
|-----------|--------|----------|
| Format | optimized | No leftover Thank You; titles are complete takeaway sentences; numbers cited with units and caveats (128K bf16 2.7 GB / 6 GB; V4-Pro 27%/10%). |
| Layout | optimized | Cover / two-col / four-col / section layouts used on purpose. Original dumps almost everything onto `content-centered-a`. Native rounded-rectangles on slides 3 and 8, not a raster flowchart. |
| Narrative | optimized | Ghost deck: constraint → transformer still here → three costs → four designs → numbers table → decision. Original is Agenda / Background / Overview / Thank You. |
| Technical depth | optimized | Layer counts, head budgets, m vs m', MLA vs CCA distinction, “no independent ablation”. Original says “saves memory”, “better than V3.2”. |
| Logic | optimized | Claims stay inside Raschka notes; decision is the cheapest reversible bet. Original asserts “architecture is important” with no ask. |
| Story flow | optimized | Each title moves the audience. Original repeats model names then thanks the room. |

## Invented numbers

None found beyond the source notes (2.7 GB, 6 GB, 27%, 10%, 10%, 7%, 35/15/20 layers, 42/24/18, 40=30+10, window 512, KV heads 8, 6 vs 8 query heads, m=4, m'=128, 128-token near window).

## Verdict

**PASS (text/structure).** Visual screenshot QA is polish-stage and was not run overnight (OfficeCLI `issues` = 0). Human should still open both pptx at work and look for overflow on long Chinese action titles.

## Residual risks

1. Long action titles on `column-2-centered` may wrap tightly on 16:9.
2. Diagram boxes on `title-centered` are overlaid, not in placeholders — still native and editable.
3. `optimize` does not yet auto-write story.json from extract; gold uses a frozen plan in `work_ppt/gold.py`.
