# Eval fixtures

## Templates (`templates/`)

| File | Role | Provenance |
|------|------|------------|
| `dense-consulting-inner-chapter.pptx` | Dense consulting, many named layouts | [pptx-from-layouts-skill](https://github.com/tristan-mcinnis/pptx-from-layouts-skill) Inner Chapter template, MIT |
| `light-corporate-office-default.pptx` | Light corporate, 11 default Office layouts | Generated with python-pptx 1.0.2 from the blank 16:9 master |
| `dark-tech-navy.pptx` | Dark tech (navy master/layout fill) | Generated with python-pptx; same 11 layouts, `#0B1220` background |
| `impoverished-title-content.pptx` | Weak master: Title Slide + Title and Content only | Stripped from the light-corporate file |

A 24 MB GBIF `.potx` was downloaded then discarded: no LICENSE file in the upstream repo, too large to vendor.

## Source (`source/`)

`raschka-2026-llm-architectures.md` — extracted notes from [Recent Developments in LLM Architectures](https://magazine.sebastianraschka.com/p/recent-developments-in-llm-architectures) (Sebastian Raschka, 2026-05-16). Not a full republication. Eval must not invent numbers beyond this file.
