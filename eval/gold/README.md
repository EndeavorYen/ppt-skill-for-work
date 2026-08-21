# Gold test

Shared fact A for Inner Chapter: `original.pptx`.

| Case | A master | Extra source | Directory |
|---|---|---|---|
| ab | Inner Chapter | no | `ab/` |
| sourced | Inner Chapter | Raschka notes | `sourced/` |
| light-ab | Office default | no | `light/ab/` |
| dark-ab | dark navy | no | `dark/ab/` |
| light-sourced | Office default | Raschka | `light/sourced/` |
| dark-sourced | dark navy | Raschka | `dark/sourced/` |

`ab` stories share `eval/gold/ab/story.json`. `sourced` stories share `eval/gold/sourced/story.json`.

Impoverished (Title + Content only) is **out of gold**. Dumping the dense story onto two layouts fails visual QA (palette, overflow, bogus diagrams). Downgrade is a unit test in `tests/test_templates.py`, not a gold pass.

```bash
python -m work_ppt gold-baseline -o eval/gold/original.pptx
python -m work_ppt gold-optimize --case all
python -m work_ppt eval-prompt --case ab
python -m work_ppt eval-check --case ab
python -m pytest tests/ -q
```

pytest does not call a model. Internal eval: `.grok/workflows/gold-eval-story.rhai` plus `eval/gold/grill-answers.json`. Copy scratch `story.json` into git only after review.

Gold B: native shapes; optional `picture=` file. No generated flowcharts.
