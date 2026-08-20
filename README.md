# ppt-skill-for-work

> **TL;DR** — Agent 寫故事，腳本套你提供的母版。Gold test：同一份 deck 既是母版也是素材，優化後必須在盲測中全面勝出。

## Quick start

```bash
pip install -r requirements.txt
python -m work_ppt onboard docs/fixtures/templates/dense-consulting-inner-chapter.pptx -o profiles/inner.json
python -m work_ppt gold-baseline -o eval/gold/original.pptx
python -m work_ppt gold-optimize -o eval/gold/optimized.pptx
python -m pytest tests/ -q
```

OfficeCLI（mutate / mermaid / preview）可選：`npm i -g @officecli/officecli`

## What this is

Not a pretty-PPT generator. A gated pipeline: brief → onboard → story freeze → compose or optimize → native diagrams.

Design: `docs/superpowers/specs/2026-08-21-work-ppt-workflow-design.md`  
Skill: `skills/work-ppt/SKILL.md`  
Eval fixtures: `docs/fixtures/`

## Gold test

`eval/gold/original.pptx` is a typical AI first draft (topic titles, bullets, Thank You).  
`eval/gold/optimized.pptx` is rebuilt on the same Inner Chapter master from that deck's facts. Blind review must keep the visual system and beat the original on format, layout, narrative, depth, logic, and story flow.
