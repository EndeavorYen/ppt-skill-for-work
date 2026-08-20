# Blind review: `eval/gold/original.pptx` vs `eval/gold/optimized.pptx`

Reviewer stance: hostile. A dimension that is only equal is a lose. Beating a Thank-You dump is not enough if the payload exhibit corrupts the source.

Sources used: `eval/gold/original.extract.json`, `eval/gold/optimized.extract.json`, both `.pptx` text dumps, `docs/fixtures/source/raschka-2026-llm-architectures.md`, `skills/work-ppt/SKILL.md`.

---

## same_template

**yes**

Both decks only instantiate Inner Chapter named layouts. Original: `title-cover`, `content-centered-a`, `column-2-centered`, `title-centered`. Optimized: the same four plus `column-4-centered` (also Inner Chapter; original simply never used it). No foreign master names, no Title Slide / Title and Content fallback, no raster-only custom layout. Optimized overlay shapes are extra native geometry on top of those layouts, not a new slide master.

---

## Six dimensions

Score is **win/lose vs original**. Equal counts as lose.

### format — **win**

Original is the stock AI draft: English topic titles (`Agenda`, `Background`, `Gemma 4 Overview`, `Key Numbers`), bullet soup, closer `Thank You`. Optimized is a zh-Hant / English-terms readout: sentence titles, two-col evidence, four-col number cards, no Thank You.

### layout — **win**

Original parks 7/9 slides on `content-centered-a` / `title-centered` and has zero diagrams. Optimized actually uses the master: cover, title-body, two `title-centered` native-shape slides, four `column-2-centered` model slides, `column-4-centered` numbers. Extract shows native `Rounded Rectangle` shapes on slides 3 and 8; original extract has none.

### narrative — **win**

Original is a catalog (`Introduction / Gemma 4 / Laguna / ZAYA1 / DeepSeek / Conclusion`) with platitudes (`LLMs are getting better`). Optimized titles state a constraint → thesis → cost axes → four mechanisms → decision. That is a ghost deck. One title is a dud (slide 9: `可核對的數字都在這張表，沒寫進來源的數字不要編` is a pipeline slogan, not a takeaway), but the spine still exists and original has no spine.

### technical depth — **win**

Original’s Gemma slide is `Uses GQA` / `Saves memory` / `Code on GitHub` (E2B is MQA in the notes, not GQA). Optimized writes the notes’ actual machinery: E2B 35/15/20 + MQA 4:1, E4B 42/24/18, PLE 2.3B/5.1B and 4.5B/8B, Laguna 30×512 + 10 global with 6 vs 8 query/KV, CCA vs MLA (attention in latent, conv on Q/K not V), CSA m=4 / HCA m'=128 / 128-token near window, V4-Pro/Flash % vs V3.2, plus the author’s no-ablation caveat. Depth still has a hole — mHC is a title word with no n=4 / doubly-stochastic / +6.7% body — but that is still more than original’s `mHC residual streams` bullet.

### logic — **lose**

The argument spine is better than original, but the **only quantitative exhibit** is false in a way original was not. Notes: sharing **saves** ~2.7 GB (E2B, bf16/128K) and ~6 GB (E4B, 128K). Optimized slide 4 says `約省 2.7 GB` (correct). Slide 9 then labels the same figures `約 2.7 GB KV` / `約 6 GB KV` — stock size, not savings. Original’s `Some memory savings` was empty and not inverted. Compounding: slide 8 stacks `近窗` / `CSA` / `HCA` as three layers; the notes describe two compression schemes that **both** keep a 128-token uncompressed window, not a sandwich. Slide 3 draws those three cost axes as a left-to-right process (`KV 記憶體` → `Attention FLOPs` → `Residual 表達力`); they are parallel cuts, not a pipeline. Precise-and-wrong does not strictly beat vague-and-true on logic.

### story flow — **win**

Original: agenda → fog → four model dumps → fake “Key Numbers” → Thank You. Optimized: KV is the constraint → decoder is specialized not replaced → three costs → designs in rising aggressiveness (share KV → budget heads → latent attention → sequence compression) → V4 close-up → numbers → prototype sharing first. Slide 9’s meta title is a speed bump, not a collapse.

---

## Invented-numbers check

**No numeric literal in optimized is absent from the Raschka notes.** Date `2026-05-16`, layer splits, 128K, 2.7/6 GB, PLE 2.3B/5.1B/4.5B/8B, 40/30/512/10, KV=8, 6 vs 8 query/KV, 4:1 GQA, one routed expert, m=4, m'=128, near window 128, 1M, V4-Pro 27%/10%, V4-Flash 10%/7% all occur in `docs/fixtures/source/raschka-2026-llm-architectures.md`.

**Referent corruption (not a new literal, still a numbers defect):**

| Slide | Deck text | Notes |
|---|---|---|
| 4 | `E2B 約省 2.7 GB，E4B 約 6 GB（未計滑窗）` | Matches “saves ~2.7 GB … ~6 GB. Sliding-window savings not included.” |
| 9 | `約 2.7 GB KV` / `約 6 GB KV` | Same digits, wrong noun. Notes never state remaining KV size. |

Omitted source numbers (not invented): Gemma 26B MoE / 31B dense; mHC n=4, 13.36G→13.38G FLOPs/token, +6.7% train time at 27B; ZAYA1 80/40 block count. Original had 26B/31B; optimized dropped them.

Original’s `Uses GQA` on Gemma 4 is the only clear technical falsehood in that deck (notes: E2B uses **MQA**). Optimized fixes that.

---

## Other must-haves

| Gate | Result | Evidence |
|---|---|---|
| Action titles form a ghost deck | **mostly; slide 9 fails** | Titles 1–8+10 read as an argument. Title 9 is an authoring rule. |
| Native `Rounded Rectangle`, not a flowchart image | **yes** | Optimized slides 3 and 8: `Rounded Rectangle 2/3/4`. No picture/flowchart block in either extract. |
| Must not end on Thank You | **yes** | Original slide 9 title = `Thank You`. Optimized slide 10 title = `先做可逆的跨層 KV sharing，再考慮 CSA/HCA 等級的複雜度`. |

Ghost deck (optimized titles in order):

1. 推理與 agent 讓 KV cache，而不是參數量，成為約束
2. 解碼器 transformer 沒被取代，只是被改成更擅長長上下文
3. 新架構在砍三種成本：KV 記憶體、Attention FLOPs、Residual 表達力
4. Gemma 4 用跨層 KV 重用砍 cache，把多出來的容量放進 PLE
5. Laguna 把 query head 花在便宜的區域層，克扣昂貴的全域層
6. ZAYA1 在壓縮潛空間裡做 attention，不是只壓縮 KV cache
7. DeepSeek V4 沿序列軸壓縮（CSA/HCA），並用 mHC 加寬 residual
8. CSA 保細節、HCA 保覆蓋，近窗負責最新 token
9. ~~可核對的數字都在這張表，沒寫進來源的數字不要編~~ ← not a takeaway
10. 先做可逆的跨層 KV sharing，再考慮 CSA/HCA 等級的複雜度

Suggested native diagrams from the notes vs what shipped:

| Required | Shipped |
|---|---|
| Decoder block with KV-share / PLE / CCA / mHC callouts | **missing** |
| Process: which cost is cut (cache vs FLOPs vs residual) | Slide 3 boxes, but drawn as a sequence |
| Sequence: token → compressed KV → CSA vs HCA m'=128 | Slide 8 stack, not a sequence and not a fork |
| Table: E2B 2.7 GB / E4B 6 GB / V4-Pro 27% 10% / V4-Flash 10% 7% | Slide 9, with the 2.7/6 GB referent bug |

---

## Verdict

**FAIL**

Format, layout, narrative, technical depth, and story flow strictly beat original. Logic does not: the numbers table inverts the only memory figures in the source, and the CSA/HCA “architecture” is a stack the notes do not describe. Six-dimension gate requires a win on every axis. Slide 9 also breaks the ghost deck.

---

## Fix list

1. **Slide 9, both Gemma cards:** restore the verb from the notes and from slide 4. Write `跨層分享約省 2.7 GB` / `約省 6 GB` (128K; E2B bf16; 未計滑窗). Never label them `GB KV` as if they were cache size.
2. **Slide 9 title:** replace `可核對的數字都在這張表，沒寫進來源的數字不要編` with a takeaway, e.g. `跨層分享省的是數 GB；V4 在 1M 把 KV 壓到 V3.2 的 7–10%`.
3. **Slide 8 diagram:** do not stack 近窗 / CSA / HCA as three layers. Native shapes: one near-window (128 token uncompressed) feeding **parallel** CSA (m=4 + sparse top-k) and HCA (m'=128 dense) branches. That is what the notes say (`Both keep a 128-token sliding-window`).
4. **Slide 3 diagram:** three cost axes are siblings, not a pipeline. Drop the left-to-right arrows, or label them as alternative cuts, not `KV → FLOPs → Residual`.
5. **Slide 7 body:** mHC is in the title and then disappears. Put source facts in a column: n=4 residual streams; Res mapping projected onto doubly stochastic matrices; 27B +6.7% train time for n=4; original HC FLOPs 13.36G→13.38G. Do not invent a quality delta.
6. **Missing architecture slide:** add a native-shape decoder block with KV-share / PLE / CCA / mHC callouts (required by the notes’ eval brief; process-3 + the CSA stack do not substitute).
7. **Gemma family context:** original carried `26B MoE` / `31B dense` from the notes; optimized dropped them. One line under slide 4 is enough so optimize does not silently lose extractable facts.
8. Re-extract after the edits and re-run this review. Do not PASS while slide 9 still says `2.7 GB KV`.
