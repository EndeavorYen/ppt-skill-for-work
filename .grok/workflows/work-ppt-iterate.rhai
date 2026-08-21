let meta = #{
    name: "work-ppt-iterate",
    description: "Build, gold-test, review, and improve the work PPT pipeline until the optimized deck beats the original",
    phases: [
        #{ title: "Build", detail: "tests and gold decks" },
        #{ title: "Review", detail: "blind compare original vs optimized" },
        #{ title: "Fix", detail: "close gaps then re-verify" },
    ],
};

let review_schema = #{
    "type": "object",
    "required": ["same_template", "wins", "gaps", "pass"],
    "properties": #{
        "same_template": #{ "type": "boolean" },
        "wins": #{
            "type": "object",
            "required": ["format", "layout", "narrative", "depth", "logic", "story"],
            "properties": #{
                "format": #{ "type": "boolean" },
                "layout": #{ "type": "boolean" },
                "narrative": #{ "type": "boolean" },
                "depth": #{ "type": "boolean" },
                "logic": #{ "type": "boolean" },
                "story": #{ "type": "boolean" },
            },
        },
        "gaps": #{ "type": "array", "maxItems": 8, "items": #{ "type": "string" } },
        "pass": #{ "type": "boolean" },
    },
};

phase("Build");
let build_prompt = "";
build_prompt += "Repo D:/Code/ppt-skill-for-work. Use execute tools. ";
build_prompt += "Run: python -m pytest tests/ -q ; python -m work_ppt gold-baseline -o eval/gold/original.pptx ; ";
build_prompt += "python -m work_ppt gold-optimize -o eval/gold/optimized.pptx. ";
build_prompt += "Fix failures. Do not invent slide numbers. Read work_ppt/ and tests/ first.";
let built = agent(build_prompt, #{ label: "build-gold", capability_mode: "all" });
if (built == () || !built.success) {
    pause("infra", "Build agent failed. Resume after the environment can run pytest.");
}

phase("Review");
let review_prompt = "";
review_prompt += "Blind-compare D:/Code/ppt-skill-for-work/eval/gold/original.pptx against BOTH eval/gold/ab/optimized.pptx and eval/gold/sourced/optimized.pptx. ";
review_prompt += "ab/ must not introduce numbers absent from original.extract.json. sourced/ may use Raschka notes and must be deeper. ";
review_prompt += "Read extract json under eval/gold/ and each case directory. ";
review_prompt += "same_template=true only if optimized uses Inner Chapter layouts (title-cover, column-2-centered, title-centered) like original. ";
review_prompt += "For each of format, layout, narrative, depth, logic, story: true only if optimized is strictly better. ";
review_prompt += "pass=true only if same_template and all six wins are true. List gaps otherwise. ";
review_prompt += "Fail closed: missing evidence means pass=false.";
let reviewed = agent(review_prompt, #{
    label: "blind-review",
    capability_mode: "read-only",
    output_schema: review_schema,
});

if (reviewed == () || !reviewed.success || reviewed.output == ()) {
    pause("verification", "Blind review did not return a schema-valid verdict.");
}

if (reviewed.output.pass == true) {
    let ok = write_scratch_file("verdict.md", "Gold test passed. Optimized beats original on all six dimensions.");
    complete(#{ summary: "gold pass", path: ok, pass: true });
}

phase("Fix");
let gaps = reviewed.output.gaps;
let gap_text = json_encode(gaps);
let fix_prompt = "";
fix_prompt += "Gold test FAILED. Gaps JSON: ";
fix_prompt += gap_text;
fix_prompt += " Repo D:/Code/ppt-skill-for-work. Read eval/gold extracts and work_ppt/gold.py. ";
fix_prompt += "Fix story, layouts, or native diagrams. Re-run gold-optimize and pytest. Do not change the Inner Chapter template. Do not invent numbers.";
let fixed = agent(fix_prompt, #{ label: "fix-gold", capability_mode: "all" });
if (fixed == () || !fixed.success) {
    pause("verification", "Fix agent failed; resume to retry.");
}

let rereview_prompt = "";
rereview_prompt += "Re-review D:/Code/ppt-skill-for-work/eval/gold original vs optimized after a fix. ";
rereview_prompt += "Read extract json files. pass=true only if same Inner Chapter master and optimized strictly wins format, layout, narrative, depth, logic, story. Fail closed.";
let rereviewed = agent(rereview_prompt, #{
    label: "blind-rereview",
    capability_mode: "read-only",
    output_schema: review_schema,
});

if (rereviewed != () && rereviewed.success && rereviewed.output != () && rereviewed.output.pass == true) {
    let ok2 = write_scratch_file("verdict.md", "Gold test passed after one fix round.");
    complete(#{ summary: "gold pass after fix", path: ok2, pass: true });
}

pause("verification", "Gold test still failing after one fix round. Resume to run another fix cycle, or inspect eval/gold.");
