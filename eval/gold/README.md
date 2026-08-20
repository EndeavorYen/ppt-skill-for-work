# Gold test

Same Inner Chapter master. `original.pptx` is a typical AI first draft (topic titles, bullets, Thank You). `optimized.pptx` is rebuilt from that deck’s facts with a frozen ghost deck and native shapes.

```bash
python -m work_ppt gold-baseline -o eval/gold/original.pptx
python -m work_ppt gold-optimize -o eval/gold/optimized.pptx
```

Blind bar: template family must match, and optimized must win format, layout, narrative, technical depth, logic, and story flow.

Open both files in PowerPoint. Read titles of `optimized.pptx` in order — they should tell the argument without the body text.
