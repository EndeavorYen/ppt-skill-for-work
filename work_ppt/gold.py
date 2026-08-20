from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

from work_ppt.compose import _delete_slides, _fill_placeholders, _layout_by_name, compose
from work_ppt.diagrams import add_csa_hca_fork, add_decoder_callouts, add_sibling_row
from work_ppt.onboard import onboard

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "docs/fixtures/templates/dense-consulting-inner-chapter.pptx"


def build_original(dest: Path) -> Path:
    """Typical AI-first-draft: topic titles, bullet soup, Thank You, no story."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    prs = Presentation(str(TEMPLATE))
    _delete_slides(prs)

    def add(layout_name, slots):
        slide = prs.slides.add_slide(_layout_by_name(prs, layout_name))
        _fill_placeholders(slide, slots)

    add("title-cover", ["LLM Architecture Update", "Gemma 4 / Laguna / ZAYA1 / DeepSeek V4", "Internal sharing"])
    add(
        "content-centered-a",
        [
            "Agenda",
            "Introduction\nGemma 4\nLaguna XS.2\nZAYA1-8B\nDeepSeek V4\nConclusion",
        ],
    )
    add(
        "content-centered-a",
        [
            "Background",
            "LLMs are getting better\nContext is longer\nThere are many new models in 2026\nArchitecture is important",
        ],
    )
    add(
        "column-2-centered",
        [
            "Gemma 4 Overview",
            "E2B and E4B for devices\n26B MoE\n31B dense\nUses GQA",
            "KV sharing across layers\nPLE embeddings\nSaves memory\nCode on GitHub",
        ],
    )
    add(
        "content-centered-a",
        [
            "Laguna XS.2",
            "Poolside coding model\n40 layers\nSliding window + global attention\nDifferent query heads per layer\nSimilar to OpenELM",
        ],
    )
    add(
        "content-centered-a",
        [
            "ZAYA1-8B",
            "Zyphra model on AMD GPUs\nCompressed Convolutional Attention\nRelated to MLA\nMoE with one expert\nPaper on arXiv",
        ],
    )
    add(
        "content-centered-a",
        [
            "DeepSeek V4",
            "Biggest release this year\nmHC residual streams\nCSA and HCA compression\nBetter than V3.2\nVery sparse MoE",
        ],
    )
    add(
        "content-centered-a",
        [
            "Key Numbers",
            "Some memory savings\nLong context is cheaper\nLots of complexity\nNeed to keep learning",
        ],
    )
    add("title-centered", ["Thank You", "Questions?"])
    prs.save(str(dest))
    return dest


OPTIMIZED_PLAN = {
    "title": "Long-context cost is now an architecture problem",
    "decision": "Prototype cross-layer KV sharing first; treat CSA/HCA as a later, higher-complexity bet.",
    "slides": [
        {
            "action_title": "推理與 agent 讓 KV cache，而不是參數量，成為約束",
            "layout_hint": "cover",
            "slots": [
                "推理與 agent 讓 KV cache，而不是參數量，成為約束",
                "Raschka 2026-05-16 筆記的工程 readout",
                "決策：先做哪一種長上下文省成本策略",
            ],
        },
        {
            "action_title": "解碼器 transformer 沒被取代，只是被改成更擅長長上下文",
            "layout_hint": "title-body",
            "slots": [
                "解碼器 transformer 沒被取代，只是被改成更擅長長上下文",
                "作者刻意不談資料配比、訓練課表、RL 與榜單\n本文只看 block / residual / KV / attention 的改動\n質性表現仍主要由資料與訓練配方驅動；架構改動買的是 runtime 成本",
            ],
        },
        {
            "action_title": "新架構在砍三種平行成本，不是一條流水線",
            "layout_hint": "section",
            "slots": ["新架構在砍三種平行成本，不是一條流水線"],
            "diagram": "sibling-costs",
        },
        {
            "action_title": "四種改動都掛在同一個 decoder block 上",
            "layout_hint": "section",
            "slots": ["四種改動都掛在同一個 decoder block 上"],
            "diagram": "decoder-callouts",
        },
        {
            "action_title": "Gemma 4 用跨層 KV 重用砍 cache，把多出來的容量放進 PLE",
            "layout_hint": "two-col",
            "slots": [
                "Gemma 4 用跨層 KV 重用砍 cache，把多出來的容量放進 PLE",
                "家族還有 26B MoE 與 31B dense；E2B/E4B 才做跨層 KV 分享\nE2B：35 層，前 15 算 KV，後 20 重用；MQA + 滑窗 4:1\nE4B：42 層，24 算 KV，後 18 重用\n128K bf16：E2B 約省 2.7 GB，E4B 約省 6 GB（未計滑窗）",
                "PLE：E2B 2.3B effective / 5.1B with embeddings\nE4B 4.5B / 8B\n額外容量在 lookup 表，不把整個 stack 做胖\n作者承認缺少對 2.3B / 5.1B 常規模型的公開對照",
            ],
        },
        {
            "action_title": "Laguna 把 query head 花在便宜的區域層，克扣昂貴的全域層",
            "layout_hint": "two-col",
            "slots": [
                "Laguna 把 query head 花在便宜的區域層，克扣昂貴的全域層",
                "40 層：30 滑窗（512）+ 10 全域\nKV head 固定 8\n全域層 6 query / KV；滑窗層 8 query / KV",
                "混滑窗+全域並非新發明（Gemma 4 也用）\n新的是 per-layer query-head 預算\n先例：Apple OpenELM 2024",
            ],
        },
        {
            "action_title": "ZAYA1 在壓縮潛空間裡做 attention，不是只壓縮 KV cache",
            "layout_hint": "two-col",
            "slots": [
                "ZAYA1 在壓縮潛空間裡做 attention，不是只壓縮 KV cache",
                "MLA：壓縮 KV 再投影回 head 空間才算 attention\nCCA：Q/K/V 都壓縮，attention 直接在潛空間算完再上投影\n省 cache 也省 prefill/training FLOPs",
                "壓縮後對 Q/K（不是 V）做卷積，補回區域上下文\n4:1 GQA；每 token 只啟動 1 個 routed expert\nCCA 論文自報優於 MLA——不是第三方 bake-off",
            ],
        },
        {
            "action_title": "DeepSeek V4 沿序列軸壓縮（CSA/HCA），並用 mHC 加寬 residual",
            "layout_hint": "two-col",
            "slots": [
                "DeepSeek V4 沿序列軸壓縮（CSA/HCA），並用 mHC 加寬 residual",
                "CSA：m=4 + 稀疏 top-k（DSA 風格）\nHCA：m'=128 再對短 cache 做 dense attention\n兩者都保留 128 token 未壓縮近窗",
                "mHC：n=4 平行 residual；Res mapping 投影到雙隨機矩陣\n27B 實作 n=4 訓練時間 +6.7%；原 HC FLOPs 13.36G→13.38G/token\n相對 V3.2、1M：V4-Pro 27% FLOPs / 10% KV；V4-Flash 10% / 7%\n作者：不能說 CSA/HCA 普遍優於 MLA；沒有獨立 ablation",
            ],
        },
        {
            "action_title": "CSA 保細節、HCA 保覆蓋，近窗被兩條路徑共用",
            "layout_hint": "section",
            "slots": ["CSA 保細節、HCA 保覆蓋，近窗被兩條路徑共用"],
            "diagram": "csa-hca-fork",
        },
        {
            "action_title": "跨層分享省的是數 GB；V4 在 1M 把 KV 壓到 V3.2 的 7–10%",
            "layout_hint": "four-col",
            "slots": [
                "跨層分享省的是數 GB；V4 在 1M 把 KV 壓到 V3.2 的 7–10%",
                "Gemma 4 E2B\n128K bf16\n跨層分享約省 2.7 GB\n（未計滑窗）",
                "Gemma 4 E4B\n128K\n跨層分享約省 6 GB\n（未計滑窗）",
                "V4-Pro @ 1M\n27% FLOPs\n10% KV vs V3.2",
                "V4-Flash @ 1M\n10% FLOPs\n7% KV vs V3.2",
            ],
        },
        {
            "action_title": "先做可逆的跨層 KV sharing，再考慮 CSA/HCA 等級的複雜度",
            "layout_hint": "title-body",
            "slots": [
                "先做可逆的跨層 KV sharing，再考慮 CSA/HCA 等級的複雜度",
                "來源沒有關閉的問題：品質對成本的 ablation 仍然薄\n跨層 KV sharing 有論文與 Gemma 4 產品化，改動面比 V4 小\nCCA/CSA/HCA 更激進，也更難在我們的 stack 落地\n決策：先 prototype 跨層 KV sharing；V4 級序列壓縮列為觀察項，不作為第一個施工項",
            ],
        },
    ],
}


def build_optimized(dest: Path, template: Path | None = None) -> Path:
    dest = Path(dest)
    template = Path(template) if template else TEMPLATE
    compose(template, OPTIMIZED_PLAN, dest)
    prs = Presentation(str(dest))
    for i, spec in enumerate(OPTIMIZED_PLAN["slides"]):
        kind = spec.get("diagram")
        if kind == "sibling-costs":
            add_sibling_row(
                prs.slides[i],
                ["KV 記憶體", "Attention FLOPs", "Residual 表達力"],
                top=Inches(3.2),
            )
        elif kind == "decoder-callouts":
            add_decoder_callouts(prs.slides[i])
        elif kind == "csa-hca-fork":
            add_csa_hca_fork(prs.slides[i])
    prs.save(str(dest))
    plan_path = dest.with_suffix(".plan.json")
    plan_path.write_text(json.dumps(OPTIMIZED_PLAN, indent=2, ensure_ascii=False), encoding="utf-8")
    return dest
