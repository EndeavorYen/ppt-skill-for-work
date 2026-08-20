# Source notes: Recent Developments in LLM Architectures

> Eval source for the work-PPT pipeline. Facts below are extracted from a public article. Do not invent numbers.

## Citation

- Author: Sebastian Raschka, PhD
- Title: Recent Developments in LLM Architectures: KV Sharing, mHC, and Compressed Attention
- Subtitle: From Gemma 4 to DeepSeek V4, How New Open-Weight LLMs Are Reducing Long-Context Costs
- Date: 2026-05-16
- URL: https://magazine.sebastianraschka.com/p/recent-developments-in-llm-architectures
- Related: LLM Architecture Gallery https://sebastianraschka.com/llm-architecture-gallery/

## Why this source

Deep technical article with architecture, process, numbers, and trade-offs. Suitable for a mixed-room engineering readout: one story (long-context cost is the constraint), multiple native diagrams (block architecture, KV-sharing vs GQA, CSA vs HCA), no need to invent conclusions.

## Thesis (from the article)

Newer open-weight architectures are not replacing the decoder-only transformer. They add targeted tricks so long-context inference is cheaper. KV-cache size, memory traffic, and attention cost are the main constraints because reasoning models and agents keep more tokens around.

Qualitative modeling quality is still driven mainly by data and training recipes; the architecture tweaks buy runtime cost.

## Scope the author set

Covered: changes inside the transformer block, residual stream, KV cache, or attention.

Skipped: dataset mixtures, training schedules, post-training, RL recipes, benchmark tables, product comparisons.

## Four designs

### 1. Gemma 4 — cross-layer KV sharing + per-layer embeddings

- Families: E2B / E4B (embedded), 26B MoE (local), 31B dense (quality / post-train).
- E2B/E4B add **cross-layer KV sharing** (later layers reuse K/V from earlier layers of the same attention type). Not invented here; see Brandon et al., “Reducing Transformer Key-Value Cache Size with Cross-Layer Attention”, NeurIPS 2024.
- E2B: 35 layers; first 15 compute KV; last 20 reuse. E2B uses MQA + sliding-window in a 4:1 pattern.
- E4B: 42 layers; 24 compute KV; last 18 share.
- Memory: sharing ~half the KVs. E2B saves ~2.7 GB at bfloat16 / 128K context. E4B saves ~6 GB at 128K. Sliding-window savings not included in that figure.
- Downside: approximation / reduced capacity. Cross-layer attention paper claims impact can be small on the small models tested.
- **PLE (per-layer embeddings):** “E” = effective. E2B = 2.3B effective / 5.1B with embeddings. E4B = 4.5B effective / 8B with embeddings. Extra capacity lives in lookup-style embedding tables, not a fatter transformer stack.
- PLE path: token IDs → per-layer embedding lookup; normal embeddings → linear projection; add/scale/reshape into one slice per layer; gated by hidden state after FFN; projected back and residual-added.
- Author caveat: no public comparison of E2B vs a regular 2.3B vs a regular 5.1B. PLE is not inherently limited to small models, but larger models already have capacity and use MoE instead.
- From-scratch code: https://github.com/rasbt/LLMs-from-scratch/tree/main/ch05/17_gemma4

### 2. Laguna XS.2 (Poolside) — layer-wise attention budgeting

- 40 layers: 30 sliding-window (window 512) + 10 global/full.
- Mixed window+global is common (also Gemma 4). New piece: **per-layer query-head counts** (`num_attention_heads_per_layer` in Hugging Face config).
- KV heads fixed at 8. Full-attention layers: 6 query heads per KV head. Sliding-window layers: 8 query heads per KV head.
- Point: spend attention capacity where it is useful; full-attention layers are expensive so they get fewer query heads.
- Precedent: Apple OpenELM (2024) varied capacity by layer. Also per-head attention-output gating (similar to Qwen3-Next; omitted in depth).

### 3. ZAYA1-8B (Zyphra) — Compressed Convolutional Attention

- Trained on AMD GPUs.
- Config lists 80 alternating entries (CCA/GQA attention vs MoE FFN) = 40 attention+MoE pairs.
- Uses CCA + 4:1 GQA. Extreme MoE: one routed expert per token.
- **CCA vs MLA:** MLA stores compact KV then up-projects into head space for attention. CCA compresses Q, K, and V and **runs attention in the compressed latent space**, then up-projects the attention vector. Saves KV cache **and** attention FLOPs in prefill/training.
- Convolutional mixing on compressed Q and K (not V) restores local context after narrowing. Sequence mixing + channel mixing.
- Paper: “Compressed Convolutional Attention: Efficient Attention in a Compressed Latent Space”, arXiv:2510.04476 (Oct 2025). ZAYA1-8B tech report: arXiv:2605.05365.
- CCA paper reports CCA outperforming MLA under comparable compression (author’s paper, not an independent third-party bake-off).

### 4. DeepSeek V4 — mHC + CSA/HCA

- V4-Pro is the most parameter-sparse MoE in the author’s active-parameter-share chart. Active share is only one lens (ignores KV, attention pattern, context, routing, hardware, data).
- **mHC (Manifold-Constrained Hyper-Connections):** arXiv:2512.24880 (31 Dec 2025), previously tested at 27B; now in the flagship.
  - Hyper-connections (Zhu et al. 2024) replace one residual stream with n parallel streams (DeepSeek V4: n=4) plus Pre/Post/Res mappings. Attention/MoE still run at normal hidden size.
  - Original HC 7B OLMo MoE: 13.36G → 13.38G FLOPs/token (essentially unchanged). Metrics reached baseline with ~half the training tokens.
  - Practical cost may be memory traffic more than FLOPs.
  - mHC projects Res Mapping onto doubly stochastic matrices (non-negative, rows and columns sum to 1). Pre/Post mappings non-negative and bounded. 27B optimized impl: +6.7% training time for n=4.
- **CSA / HCA compress along the sequence axis**, unlike MLA’s per-token latent KV.
  - CSA: milder compression m=4 + sparse top-k (DSA-style). Keeps more detail.
  - HCA: heavy compression m'=128 then dense attention over the short cache.
  - Both keep a 128-token sliding-window of uncompressed recent KV.
  - At 1M context, V4-Pro uses 27% of V3.2’s single-token inference FLOPs and 10% of V3.2’s KV cache. V4-Flash: 10% FLOPs, 7% KV vs V3.2.
  - Author: not “universally better than MLA”. No ablation isolating CSA/HCA. Reported quality is the full V4 recipe (data, Muon, mHC, precision, systems).

## Author’s takeaway

Transformer block is still the recipe, more specialized for long context. Tweaks 10× implementation complexity vs a 50–100 line GPT-2 block, in exchange for lower runtime cost. First-time readers will drown in V4 source; learn GPT-2 then add one component at a time.

## Suggested eval brief (work-report wrapping)

Use these notes as `sources`. Do not add benchmarks the article did not publish.

```yaml
title: "Long-context cost is now an architecture problem, not just a hardware one"
audience: mixed-room
language: zh-Hant-en-terms   # first draft; en is polish-only
path: compose
decision: "Which KV/attention strategy should we prototype first for 128K+ agent workloads — cross-layer KV sharing, layer-wise head budgeting, CCA, or wait for CSA/HCA-class sequence compression?"
```

Ghost-deck spine (action titles; story layer may rewrite, must stay source-faithful):

1. Reasoning and agents made KV-cache size, not parameter count, the binding constraint.
2. The decoder-only transformer is not being replaced; it is being specialized for long context.
3. Gemma 4 reuses KV across layers and parks extra capacity in per-layer embeddings.
4. Laguna spends query heads on cheap local layers and starves expensive global layers.
5. ZAYA1 runs attention inside a compressed latent, unlike MLA’s cache-only compression.
6. DeepSeek V4 shortens the sequence itself (CSA/HCA) and widens the residual (mHC).
7. We should prototype the cheapest reversible bet first — cross-layer KV sharing — before committing to CSA/HCA complexity.
8. Open question the article does not close: quality vs cost ablations are still thin.

Required native diagrams (must not be rasters):

- Architecture: decoder block with optional KV-share / PLE / CCA / mHC callouts
- Process: “which cost is being cut” decision (cache memory vs attention FLOPs vs residual expressivity)
- Sequence: token → compressed KV blocks → CSA sparse select vs HCA dense over m'=128
- Table: E2B 2.7 GB / E4B 6 GB / V4-Pro 27% FLOPs 10% KV / V4-Flash 10% FLOPs 7% KV
