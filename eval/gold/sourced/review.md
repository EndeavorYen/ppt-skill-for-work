# Inner Chapter sourced — six dimensions

A: `eval/gold/original.pptx`  
B: `eval/gold/sourced/optimized.pptx`  
Extra source: `docs/fixtures/source/raschka-2026-llm-architectures.md`  
This is not an A/B of equal facts. Depth may (and must) exceed A.

| Dimension | Verdict | Evidence |
|---|---|---|
| format | **win** | Same as A/B: takeaway titles, no Thank You, zh-Hant/en-terms readout vs topic bullets. |
| layout | **win** | Cover, title-body, two native-shape section slides (sibling costs, decoder callouts), four two-col model slides, CSA/HCA fork, four-col number cards. Inner Chapter layouts only. |
| narrative | **win** | Constraint (KV cache) → decoder still the recipe → three parallel costs → four mechanisms on one block → four models → fork close-up → sourced numbers → prototype KV sharing first. |
| depth | **win** | 2.7 GB / 6 GB, E2B 35/15/20, PLE 2.3B/5.1B, Laguna 30×512+10 global, CSA m=4 / HCA m'=128, V4-Pro 27%/10% vs V3.2. A had “Saves memory” and “Better than V3.2”. |
| logic | **win** | Sibling costs are not a pipeline (no arrows). CSA/HCA share the near window. Decision matches evidence: KV sharing is smaller surface than V4 sequence compression; notes lack isolating ablations. |
| story | **win** | Ghost deck titles carry the argument without body text. Closer is a decision, not Thank You. |

**pass:** yes (six wins). Same visual system. Do not treat this pair as the no-source A/B.
