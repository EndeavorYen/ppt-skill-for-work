# Deep Interview Spec: Template-Agnostic Work PPT Workflow

## Metadata
- Interview ID: 2026-08-21-ppt-workflow
- Rounds: 8
- Final Ambiguity Score: ~18%
- Type: greenfield (repo currently LICENSE-only)
- Generated: 2026-08-21
- Threshold: 20%
- Status: PASSED — awaiting user approval before implementation

## Clarity Breakdown

| Dimension | Score | Weight | Weighted | Gap |
|-----------|-------|--------|----------|-----|
| Goal Clarity | 0.88 | 0.40 | 0.352 | Eval brief topic not chosen yet; architecture is stable |
| Constraint Clarity | 0.90 | 0.30 | 0.270 | Template is any user-supplied .pptx/.potx, not one company file |
| Success Criteria | 0.78 | 0.30 | 0.234 | Need 4 onboard fixtures + one frozen test brief |
| **Total Clarity** | | | **0.856** | |
| **Ambiguity** | | | **14.4%** | |

## Goal

Build a **template-agnostic production workflow** (skill + scripts + gates) that turns work materials into a technical-report PowerPoint the user is willing to present.

It is not “a prettier PPT generator.” It is a gated pipeline:

1. Onboard **any** user-supplied `.pptx` / `.potx`.
2. Take a **creation brief** (audience, language, path, sources).
3. Freeze a **single story** before touching layouts.
4. Render into that template’s real masters/layouts (or surgically patch a previous deck).
5. Emit native editable diagrams; generate raster images only when the router allows.
6. Hit a **10–15 minute first draft**, then an optional **≤30 minute polish** after content freeze.

## Constraints

- **Any template, not a hardcoded company file.** User provides the template at creation time. Same pipeline must work on OpenAI / Claude / Grok / Apple / NVIDIA-like decks *if they are real `.pptx`/`.potx` with a slide master*. Keynote and investor PDFs are not templates.
- **Stacked visual contract:** (1) use the template’s slide master layouts / placeholders; (2) new decks must look like they belong with previous reports from the same template; (3) colors, fonts, logo, footer come from the template — never invented hex/font names.
- **Two first-class paths, ~50/50:** mutate last deck vs compose a new deck from the onboarded template.
- **Audience, language, and sources are creation-time parameters**, not baked-in defaults. First draft is one language; a second language is polish-only (translate text, do not re-layout).
- **Diagrams must stay editable.** Architecture, process/state, and sequence/API diagrams are native PowerPoint shapes (or native charts/tables). Rasterizing a flowchart is a defect.
- **Image routing is mandatory.** Some visuals may be generated; labeled diagrams, numbers, logos, and UI-accurate screenshots may not.
- **Speed SLA:**
  - Template onboard is **once per template**, outside the 10–15 minute draft budget.
  - First draft + small fix: **10–15 minutes** once the template is already profiled and materials exist.
  - After content freeze, polish: **≤30 minutes**.
- **No content invention.** If sources do not support a number or conclusion, stop and ask. Do not hallucinate.

## Non-Goals

- HTML-first slide decks (guizang, frontend-slides, magazine layouts) as the primary deliverable.
- Image-first whole-slide generation (Nano Banana, gpt-image-2 slide skills).
- Shipping or redistributing third-party corporate decks as repo assets.
- McKinsey-lookalike template packs that ignore the user-supplied master.
- One-shot regenerate-the-whole-deck as the default edit path.
- Video, Remotion, presenter-console HTML, style galleries of 4 rendered covers on the draft path.
- A mega-skill that “does PowerPoint” without a brief gate.

## Acceptance Criteria

- [ ] `onboard <template.pptx>` writes a reusable profile: theme (colors/fonts), slide size, layouts with placeholder names/types, footer/logo presence, density hints. Refuses if there is no usable master.
- [ ] Same technical brief rendered through **four** fixtures looks native to each template:
  1. Dark tech
  2. Light corporate
  3. Dense consulting
  4. Impoverished master (cover + one content layout only) — system uses only those layouts, does not freehand a fake “pretty” layout
- [ ] Ghost-deck test: reading action titles in order tells the story without opening the slides.
- [ ] First-draft path does not call an image model. Polish path may, and only for router-allowed slots.
- [ ] Flowcharts/architecture/sequence in the test brief exist as native shapes or native charts, and remain editable in PowerPoint.
- [ ] Mutate path changes text/data on an existing deck without rebuilding layouts.
- [ ] Brief missing audience, language, path, template, or sources → pipeline refuses to render.
- [ ] Draft SLA is a gate: draft workflow has no multi-round visual screenshot loop; polish workflow does.

## Assumptions Exposed & Resolved

| Assumption | Challenge | Resolution |
|------------|-----------|------------|
| Need a better SKILL.md | Previous skills failed because they generate a whole deck in one shot | Pipeline with freeze points, not a longer prompt |
| Company has one locked template | User wants any supplied template | Onboard is a first-class verb |
| Pick one audience | User needs all audiences | Creation parameter; story layer switches, visual layer does not |
| Pick one language | User may want zh and en | First draft = one language; second language = polish, text-only |
| HTML PPT skills are “better looking” | They cannot honor a real Office master in 10–15 min | Rejected as primary renderer |
| Image models can draw flowcharts | User requires editable diagrams | Mermaid/connectors → native shapes; raster flowchart is a defect |
| Speed means faster generation | Speed means patch, not regenerate | OfficeCLI resident/batch + frozen story |
| Apple/NVIDIA public reports are templates | Those are often Keynote/PDF | Eval uses real `.pptx`/`.potx` with masters |

## Ontology (Key Entities)

| Entity | Type | Fields | Relationships |
|--------|------|--------|---------------|
| Brief | core | audience, language, path, sources, template_id, timebox | drives Story |
| TemplateProfile | core | theme, layouts, placeholders, footer, logo, slide_size | produced by Onboard |
| Story | core | audience_state_in, audience_state_out, action_titles[], per_slide intent | frozen before Render |
| SlidePlan | core | layout_name, slots, diagram_kind, media_kind | maps Story → TemplateProfile layouts |
| Path | supporting | mutate \| compose | mutate needs prior deck; compose needs profile |
| DiagramJob | supporting | mermaid \| native-chart \| table \| forbidden-raster | rendered as editable OOXML |
| MediaJob | supporting | screenshot \| generate \| none | generate only if no required text/labels |
| Draft | supporting | pptx, story.md, slide_plan.json | 10–15 min artifact |
| Polish | supporting | visual QA, 2nd language, allowed images | after content freeze |

## Technical Context

Empty repo (`LICENSE` only). User already feels pain from existing PPT skills (AI tone, weak language, ugly layout, no story, ugly flowcharts, slow). Grok bundled `pptx` skill is PptxGenJS-from-scratch unless a file is attached — that is the wrong default here.

This machine did not have OfficeCLI installed at interview time.

## Architecture (proposed)

```
Brief gate
    │  refuse if audience / language / path / template / sources missing
    ▼
Onboard (once per template)     ← outside draft SLA
    │  profile.json + layout catalog
    ▼
Story freeze                    ← humanize-ppt AST + academic action titles
    │  story.md (ghost deck) + slide_plan.json
    │  user may edit story.md; render never invents a new story
    ▼
Render
    ├─ mutate:  clone last.pptx → OfficeCLI set/batch
    └─ compose: add slides from profiled layouts → fill placeholders
    ▼
Diagram router
    ├─ architecture / process / sequence → Mermaid → native shapes
    ├─ numbers comparison → native chart or table
    └─ generate image? only atmosphere/metaphor with no required text
    ▼
Draft ship (10–15 min)          ← mechanical checks only
    ▼
Polish (≤30 min, after freeze)  ← screenshot QA, layout tight, 2nd language, allowed images
```

### Layer ownership

| Layer | Owns | Does not own |
|-------|------|----------------|
| Brief | parameters, refusal | visuals |
| Story | one argument, action titles, density vs audience | colors, layouts |
| Onboard / Render | template fidelity, placeholders, mutate vs compose | narrative |
| Diagram router | editable vs generated | slide titles |
| Draft vs Polish | SLA split | “keep generating until pretty” |

### OfficeCLI role

OfficeCLI is the **mechanical engine**, not the writer.

Use it for: `dump` / profile, `merge` or placeholder `set`, `add` slides from layouts, mermaid → native shapes, `batch` + resident mode, `view issues` / screenshot in **polish only**, `watch` during polish.

Do not use it to invent story, action titles, or brand tokens.

## Open-source map (steal vs reject)

### Steal (cite, adapt, do not vendor illegal templates)

| Project | Stars (approx) | Steal what |
|---------|----------------|------------|
| [iOfficeAI/OfficeCLI](https://github.com/iOfficeAI/OfficeCLI) | 29k | Path addressing, batch/resident, mermaid→native shapes, dump/merge, view issues, watch. Apache-2.0 |
| [tristan-mcinnis/pptx-from-layouts-skill](https://github.com/tristan-mcinnis/pptx-from-layouts-skill) | small | Profile master layouts → `[HINT: layout]` → fill real placeholders. Edit vs regenerate rule |
| [ferdinandobons/brand-docs](https://github.com/ferdinandobons/brand-docs) | — | Extract brand from a real template; never write hex/font literals; fail-closed verify. PPTX still alpha — steal the contract, not a hard dependency if it cannot onboard our fixtures |
| [LearnPrompt/humanize-ppt](https://github.com/LearnPrompt/humanize-ppt) | ~0.9k | AST (audience state transfer), ghost-deck / outline preview, “don’t render until the line exists”. **Do not** take guizang/HTML as renderer |
| [Gabberflast/academic-pptx-skill](https://github.com/Gabberflast/academic-pptx-skill) | ~0.8k | Action titles, situation→complication→resolution, one exhibit per results slide, no “Thank You” closer |
| [GordenSun/GordenPPTSkill](https://github.com/GordenSun/GordenPPTSkill) | ~3k | `edits.json` non-destructive fill. **Do not** use bundled templates (non-commercial) |
| [EveryInc/hands-on-deck](https://github.com/EveryInc/hands-on-deck) | ~0.2k | Inspect / lint / patch helpers |
| [icip-cas/PPTAgent](https://github.com/icip-cas/PPTAgent) | ~5k | Edit-based generation from reference slides (research pattern), not the product |

### Reject as primary path

| Project class | Why it fails *this* user |
|---------------|--------------------------|
| HTML-first (frontend-slides, guizang, huashu, presenton) | Cannot honor an arbitrary Office master in 10–15 min; conversion to PPTX is lossy |
| Image-first (codex-ppt-skill, banana-slides, nbp_slides) | Uneditable, slow, flowcharts become pictures |
| ppt-master default SVG pipeline | Powerful native objects, but default is not “fill this master”; template-fill is a side route only |
| McKinsey template skills | Pretty, off-brand the moment a real company master exists |
| Grok bundled `pptx` creating.md | PptxGenJS from blank unless a file is attached |

### Honest OfficeCLI caveats

- It **will** speed inspect / patch / mermaid / preview. That attacks pains 3, 5, 6.
- It **will not** fix AI tone or empty technical writing. That is the story layer.
- First-time onboard of a messy real-world master may still need a human glance. Cache the profile.
- SmartArt / locked masters / missing placeholders: profile must record “this layout cannot hold a 7-box process” instead of overlaying text boxes.

## Image / diagram router (draft vs polish)

| Visual | Draft | Polish |
|--------|-------|--------|
| Process / state / architecture / sequence | Mermaid → native shapes | Re-layout connectors, still native |
| Chart from numbers in sources | Native chart | Series/color from template theme |
| Table | Native table | Tighten column widths |
| Real UI / product screenshot | Place the real file if provided | Crop/align |
| Atmosphere / metaphor with no required text | Skip (blank slot or simple shape) | Optional image model |
| Logo, wordmark, exact UI copy, labeled flowchart as PNG | Forbidden | Forbidden |

## Creation brief (required fields)

```yaml
audience: engineering-review | manager | mixed-room | external
language: zh-Hant-en-terms | zh-Hant-full | en | (second language is polish-only)
path: mutate | compose
template: path/to.pptx   # or profile id if already onboarded
prior_deck: path/to.pptx # required if path=mutate
sources: [files...]
title: string
decision: "what the room must be able to decide"
```

Missing any field → refuse.

## Eval fixtures (v0)

Four templates, **one frozen technical brief**, four output decks.

1. Dark tech master
2. Light corporate master
3. Dense consulting master
4. Impoverished master (title + content only)

Weak-master test: if the plan asks for a 5-column comparison layout that does not exist, split into allowed layouts or a table on the content layout — never draw a new master.

## Interview Transcript (compressed)

1. Template constraint → user: goals 1+2+3 together (master layouts, look like prior reports, brand tokens).
2. Work mix → ~50/50 mutate vs compose.
3. Audience → all of them, specified at creation.
4. Ugly diagrams → all types possible; need a router.
5. Sources → kinds vary, specified each time; no invention.
6. SLA → 10–15 min draft + small fix; ≤30 min polish after freeze.
7. Language → specified each time; possible second language of the same deck.
8. Template supply → not one company file; any user template. Validate on public-style decks.
9. Eval set → four templates including a poor master.

## Implementation sequence (after approval)

1. Install OfficeCLI; smoke `create` / `dump` / mermaid add / `view issues`.
2. `onboard` script + profile schema.
3. Brief gate + story freeze (markdown) + ghost-deck check.
4. Compose path: layouts → placeholders.
5. Mutate path: OfficeCLI `set`/`batch` on a copy.
6. Diagram router.
7. Four-fixture eval with one brief.
8. Skill.md that *only* orchestrates the above (no layout invention).
