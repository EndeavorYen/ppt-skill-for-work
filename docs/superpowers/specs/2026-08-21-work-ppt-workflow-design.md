# Work PPT Workflow Design

| Field | Value |
|-------|--------|
| Status | Accepted for Inner Chapter gold split (ab + sourced) |
| Date | 2026-08-21 |
| Repo | `ppt-skill-for-work` |

> **TL;DR** — 這不是「更會畫 PPT 的 skill」。Agent 寫故事，腳本套使用者提供的母版。Gold test：一份既是母版又是素材的 deck，優化後必須在盲測中全面勝出，且版型一致。

## Overview

工作簡報的失敗來自一次生成整份、不管母版、把流程圖畫成死圖。本系統拆成閘門式管線：Brief → Onboard → Story freeze → Compose/Mutate → Diagram router → Draft → Polish。

機械層以 python-pptx 填 **真實 slide layout placeholders**，並做 compose / mutate。OfficeCLI 負責 theme、`qa`；Mermaid→原生 shape 與 screenshot polish 列為後續。敘事層（ghost deck / action title）由 Agent 依 skill 寫入 `story.json`，腳本不發明結論。

## Goals

- 任意 `.pptx` / `.potx` 可 onboard（非鎖死一家公司檔）。
- 兩條路徑：`compose`（從母版組新份）與 `mutate`/`optimize`（改上份或優化同一份）。
- 流程圖、架構圖、時序圖必須是原生 shape；帶字的圖禁止生圖。
- Draft 10–15 分鐘（樣板已 profile）；Polish ≤30 分鐘。
- **Gold test：** 同一份淺 AI 初稿當 A。兩場 B 都從該檔長出：`ab/` 無額外 source（數字 ⊆ extract）；`sourced/` 可讀 Raschka 筆記且深度廣度必須勝出。兩場不可混在一對檔。

## Non-goals

HTML-first 簡報、整頁生圖、把第三方公司檔當 repo 資產、預設重產整份、在 draft 做多輪截圖 QA。

## Proposed design

```mermaid
flowchart TD
  brief[Brief gate] --> onboard[Onboard template]
  onboard --> story[Story freeze]
  story --> path{path}
  path -->|compose| compose[Fill real layouts]
  path -->|mutate / optimize| mutate[Patch or rebuild on same master]
  compose --> diagrams[Native diagram router]
  mutate --> diagrams
  diagrams --> draft[Draft ship]
  draft --> polish[Polish after freeze]
```

### Layer ownership

| Layer | Owns | Forbidden |
|-------|------|-----------|
| Brief | audience, language, path, template, sources, decision | 視覺 |
| Story | action titles, state transfer, density | 色碼、字體、自由畫 layout |
| Onboard / Render | 母版 fidelity | 發明數字 |
| Diagram router | mermaid/native vs generate vs forbid | 標題文案 |
| Draft vs Polish | SLA | 沒凍結就精修 |

### CLI

```text
python -m work_ppt onboard <template.pptx> -o profiles/<id>.json
python -m work_ppt extract <deck.pptx> -o extract.json
python -m work_ppt compose --brief B.json --story S.json --template T.pptx -o out.pptx
python -m work_ppt optimize <deck.pptx> --brief B.json --story S.json -o out.pptx
python -m work_ppt gold-baseline -o eval/gold/original.pptx
python -m work_ppt gold-optimize --case all
```

缺 brief 欄位則拒畫。新樣板 onboard 不算進 15 分鐘 SLA。

### Layout mapping

Onboard 產出每個 layout 的 placeholder 清單（idx, type, name）。Compose 只填 TITLE / BODY / OBJECT，跳過 SLIDE_NUMBER 與 PICTURE（除非 plan 明確給真實圖檔）。

若 plan 要的視覺在母版不存在（弱母版 gold：只有 Title + Title and Content），降級為表格或拆頁，**禁止自創新 master**。

### Diagram router

| Kind | Draft | Polish |
|------|-------|--------|
| architecture / process / sequence | native shapes | 仍可編輯；禁止 PNG 流程圖 |
| numbers | native table/shape | theme 色 |
| real screenshot | plan 提供的檔 | 裁切 |
| generated image | gold B 禁止 | 最終檔可，但不得代替流程／架構／時序 |
| labeled flowchart as PNG | defect | defect |

### Gold test

1. 用 Inner Chapter 母版產出淺 AI 初稿 `eval/gold/original.pptx`（主題式標題、子彈清單、Thank you）。這份檔同時是 A 與 B 的母版。
2. `eval/gold/ab/`：optimize 只讀該 pptx。B 的數字必須出現在 A 的 extract。可改敘事、排版、新增原生圖。
3. `eval/gold/sourced/`：同一份 A + `docs/fixtures/source/raschka-2026-llm-architectures.md`。B 深度廣度必須勝出。
4. 凍結 `story.json` + pptx 進 git。pytest 不呼叫模型。六維裡 narrative/depth/logic/story 由人看凍結稿。
5. 弱母版（Title + Content only）不進 gold。硬套密母版故事無法通過視覺 QA。降級只做單元測試。

## Data model

`brief.json` required: `audience`, `language`, `path` (`compose`|`mutate`|`optimize`), `template` or `prior_deck`, `title`, `decision`.

`profile.json`: `slide_size`, `theme` (colors/fonts from OfficeCLI get `/`), `layouts[]` with placeholders.

`story.json`: `audience_in`, `audience_out`, `decision`, `slides[]` of `{action_title, intent, layout_hint, slots[], diagram}`.

`slide_plan.json`: resolved `layout_name` + slot fills. Render 不得改 action_title。

## Alternatives

1. **HTML-first 再轉 PPTX** — 好看但吃不了任意母版，否決。
2. **OfficeCLI 從空白 add slide** — 文件寫明新頁不會自動物化 layout placeholders；組新份必須 python-pptx `add_slide(layout)`。OfficeCLI 留給 mutate 與 mermaid。
3. **整頁生圖** — 流程圖不可編輯，否決。

## Security

來源與母版預設本機。不把使用者公司檔 commit 進 git。Eval fixtures 僅 MIT Inner Chapter + 自產空白母版 + 摘錄筆記（非全文轉載）。

## Observability

每次 run 寫 `runs/<id>/`：brief、profile、story、plan、pptx。Gold 結構閘門寫 `eval/gold/<case>/blind_review.json`。

## Rollout

v0：onboard + extract + compose + optimize + Inner Chapter `ab/` + `sourced/` gold，以及 light/dark 家族。弱母版不進 gold。再後：theme-aware diagrams、OfficeCLI mermaid/screenshot、draw.io 匯入。

## Key Decisions

1. **管線不是 mega-skill** — 一次生成是痛點根源。
2. **python-pptx 做 compose 與 mutate；OfficeCLI 做 theme 與 qa** — 新頁必須 `add_slide(layout)`。Mermaid／screenshot 後續。
3. **Story 凍結後才渲染** — ghost deck 可單獨審。
4. **Gold = 優化既有 deck** — 比「空白母版填同一 brief」更接近真實工作。
5. **弱母版必須降級而非發明 layout**。
6. **Gold B 禁止生圖。** 產品最終檔可生圖，但流程／架構／時序必須可編輯。Draft 不做多輪截圖 QA。

## PR Plan

| PR | Title | Files | Deps |
|----|-------|-------|------|
| 1 | Schemas, onboard, extract, fixtures | `work_ppt/onboard.py`, `extract.py`, `docs/fixtures` | — |
| 2 | Compose onto real layouts | `work_ppt/compose.py`, tests | 1 |
| 3 | Native diagrams | `work_ppt/diagrams.py` | 2 |
| 4 | Optimize path + gold baseline | `work_ppt/optimize.py`, `eval/gold` | 3 |
| 5 | Skill.md + CLI + iterate workflow | `skills/work-ppt`, `.grok/workflows` | 4 |

## Open Questions

- 盲測是否允許「深度持平、敘事勝出」？預設：**六維都必須勝出**（使用者原話）。
- 第二語言是否納入 v0 gold？預設否，屬 polish。

## References

- `.omc/specs/deep-interview-ppt-workflow.md`
- OfficeCLI 1.0.144
- Inner Chapter template (MIT, pptx-from-layouts)
- Raschka, 2026-05-16, LLM architecture notes in `docs/fixtures/source/`
