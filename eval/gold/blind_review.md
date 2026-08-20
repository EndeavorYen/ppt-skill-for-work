# Blind review: `eval/gold/original.pptx` vs `eval/gold/optimized.pptx`

Re-review after the logic fix. Stance still hostile: equal = lose. PASS only if every gate below holds.

Sources: `eval/gold/original.extract.json`, `eval/gold/optimized.extract.json`, `eval/gold/optimized.plan.json`, both `.pptx` text dumps, `work_ppt/diagrams.py`, `work_ppt/gold.py`, `docs/fixtures/source/raschka-2026-llm-architectures.md`.

---

## same_template

**yes**

Both decks only instantiate Inner Chapter layouts. Original: `title-cover`, `content-centered-a`, `column-2-centered`, `title-centered`. Optimized: the same four plus `column-4-centered`. Diagrams are extra `Rounded Rectangle` geometry on those layouts, not a new master.

---

## Six dimensions

Score is **win/lose vs original**. Equal counts as lose.

### format — **win**

Original is the AI draft: English topic titles (`Agenda`, `Background`, `Gemma 4 Overview`, `Key Numbers`) and a `Thank You` closer. Optimized is a zh-Hant / English-terms readout with sentence titles, two-col evidence, four-col number cards, and native shapes.

### layout — **win**

Original parks 7/9 slides on `content-centered-a` / `title-centered` with zero diagrams. Optimized uses the master: cover, two title-body slides, three `title-centered` native-shape slides (sibling costs, decoder callouts, CSA/HCA fork), four `column-2-centered` model slides, `column-4-centered` numbers. Extract lists `Rounded Rectangle` on slides 3, 4, and 9; original extract has none.

### narrative — **win**

Original is a catalog (`Introduction / Gemma 4 / Laguna / ZAYA1 / DeepSeek / Conclusion`) plus platitudes. Optimized titles are all takeaways and read as a ghost deck: constraint → thesis → parallel costs → one decoder block → four mechanisms → fork close-up → sourced numbers → prototype sharing first.

### technical depth — **win**

Original: `Uses GQA` (E2B is MQA), `Saves memory`, `Better than V3.2`, `mHC residual streams` with no mechanics. Optimized carries the notes’ machinery: 26B MoE / 31B dense family context, E2B 35/15/20 + MQA 4:1, E4B 42/24/18, PLE 2.3B/5.1B and 4.5B/8B, Laguna 30×512 + 10 global with 6 vs 8 query/KV, CCA vs MLA (latent attention, conv on Q/K not V), CSA m=4 / HCA m'=128 / shared 128-token window, mHC n=4 + doubly-stochastic Res + 27B +6.7% + 13.36G→13.38G/token, V4-Pro/Flash % vs V3.2, and the no-ablation caveat.

### logic — **win**

The six defects that failed the last pass are gone. Slide 10 (was 9) says `跨層分享約省 2.7 GB` / `約省 6 GB`, not `GB KV` stock. Slide 5 also uses `約省` for both E2B and E4B. `add_sibling_row(..., connect=False)` draws the three costs with no arrows; the title names them `平行成本，不是一條流水線`. `add_csa_hca_fork` places a shared 近窗 box above two side-by-side branches with arrows into CSA and HCA; labels say `兩條路徑都保留` / `近窗被兩條路徑共用`. V4 body now states mHC instead of title-only. Decoder callouts exist (KV-share / PLE / CCA / mHC). Original’s `Some memory savings` and `Better than V3.2` are no longer the more honest exhibit.

### story flow — **win**

Original: agenda → fog → four dumps → empty “Key Numbers” → Thank You. Optimized: KV is the constraint → decoder specialized not replaced → three sibling costs → map onto one block → Gemma → Laguna → ZAYA1 → V4 → CSA/HCA fork → numbers → reversible prototype. No slogan slide, no Thank You.

---

## Prior FAIL items (re-checked)

| # | Prior defect | Now |
|---|---|---|
| 1 | Slide 9 labeled 2.7/6 GB as KV stock | **fixed.** Slide 10: `跨層分享約省 2.7 GB` / `跨層分享約省 6 GB`. No `2.7 GB KV` / `6 GB KV` string in the extract. |
| 2 | CSA/HCA drawn as a stack | **fixed.** Slide 9 title + labels describe a shared window and two paths; `add_csa_hca_fork` is a top box at (3.4", 2.15") and two branches at y=4.15" (x=0.7" and x=7.1") with arrows down from the window. |
| 3 | Three costs drawn as a pipeline | **fixed.** Title `不是一條流水線`; `add_sibling_row` sets `connect=False` (no arrows). |
| 4 | Numbers-slide title was a slogan | **fixed.** Title is a takeaway: `跨層分享省的是數 GB；V4 在 1M 把 KV 壓到 V3.2 的 7–10%`. |
| 5 | mHC facts missing from V4 body | **fixed.** Slide 8: n=4, 雙隨機矩陣, 27B +6.7%, 13.36G→13.38G/token. |
| 6 | Decoder callout slide missing | **fixed.** Slide 4: core `Decoder block / Attention + FFN` plus KV-share, PLE, CCA, mHC rounded rects. |

---

## Invented-numbers check

**No numeric literal in optimized is absent from the Raschka notes.**

| Number | Where in deck | Notes |
|---|---|---|
| 2026-05-16 | cover | article date |
| 26B MoE, 31B dense | slide 5 | Gemma family |
| 35 / 15 / 20; 42 / 24 / 18 | slide 5 | E2B / E4B layer split |
| 4:1 MQA 滑窗 | slide 5 | E2B pattern |
| 128K, bf16, 約省 2.7 GB, 約省 6 GB, 未計滑窗 | slides 5, 10 | savings, not remaining cache |
| 2.3B / 5.1B, 4.5B / 8B | slide 5 | PLE effective vs with embeddings |
| 40 / 30 / 512 / 10, KV=8, 6 vs 8 query/KV | slide 6 | Laguna |
| OpenELM 2024 | slide 6 | precedent year |
| 4:1 GQA, 1 routed expert | slide 7 | ZAYA1 |
| m=4, m'=128, 128-token near window | slides 8–9 | CSA / HCA |
| n=4, 27B, +6.7%, 13.36G→13.38G/token | slide 8 | mHC / original HC |
| 1M, V4-Pro 27% FLOPs / 10% KV, V4-Flash 10% / 7% | slides 8, 10 | vs V3.2 |
| 7–10% | slide 10 title | range over the two sourced KV figures (Flash 7%, Pro 10%), unpacked on the cards |

Not invented, still omitted (harmless): ZAYA1 80/40 block count; Brandon et al. 2024; original HC “~half the training tokens”; “sharing ~half the KVs”.

Original falsehood still present in the baseline: Gemma 4 `Uses GQA`. Optimized correctly says E2B uses MQA.

---

## Other must-haves

| Gate | Result | Evidence |
|---|---|---|
| Same Inner Chapter master | **yes** | Named layouts only from that master. |
| Ghost deck titles are all takeaways | **yes** | Eleven sentence titles; none are `Agenda` / `Background` / `Key Numbers` / `Thank You` / authoring slogans. |
| CSA/HCA is a fork, not a stack | **yes** | Shared 近窗 → CSA and HCA branches (`add_csa_hca_fork`). |
| Numbers say 省, not stock KV | **yes** | `約省 2.7 GB` / `約省 6 GB` on slides 5 and 10. |
| Native `Rounded Rectangle`, not a flowchart image | **yes** | Slides 3, 4, 9. No picture block in either extract. |
| No Thank You closer | **yes** | Original slide 9 = `Thank You`. Optimized slide 11 = the prototype decision. |

Ghost deck (optimized titles in order):

1. 推理與 agent 讓 KV cache，而不是參數量，成為約束
2. 解碼器 transformer 沒被取代，只是被改成更擅長長上下文
3. 新架構在砍三種平行成本，不是一條流水線
4. 四種改動都掛在同一個 decoder block 上
5. Gemma 4 用跨層 KV 重用砍 cache，把多出來的容量放進 PLE
6. Laguna 把 query head 花在便宜的區域層，克扣昂貴的全域層
7. ZAYA1 在壓縮潛空間裡做 attention，不是只壓縮 KV cache
8. DeepSeek V4 沿序列軸壓縮（CSA/HCA），並用 mHC 加寬 residual
9. CSA 保細節、HCA 保覆蓋，近窗被兩條路徑共用
10. 跨層分享省的是數 GB；V4 在 1M 把 KV 壓到 V3.2 的 7–10%
11. 先做可逆的跨層 KV sharing，再考慮 CSA/HCA 等級的複雜度

---

## Non-blocking nits (do not fail)

- Slide 10 title compresses Pro 10% KV and Flash 7% KV into `7–10%`. Endpoints are in the notes and on the cards; it is not a third measurement.
- Decoder callouts match the notes’ required set (KV-share / PLE / CCA / mHC). Laguna head-budgeting and CSA/HCA live on later slides, not on that block.
- `原 HC FLOPs 13.36G→13.38G/token` omits the 7B OLMo MoE qualifier. The digits are sourced; do not read them as mHC-at-V4.

---

## Verdict

**PASS**

Same Inner Chapter master. Optimized strictly wins format, layout, narrative, technical depth, logic, and story flow. No Thank You. No stock-size `2.7 GB KV` / `6 GB KV`. CSA/HCA is a fork from a shared 128-token window. Ghost-deck titles are takeaways. Numbers in the deck are in the Raschka notes.
