let meta = #{
    name: "gold-eval-story",
    description: "Internal eval: agent writes a gold story.json from extract plus prepared grill answers; does not run in CI",
    phases: [
        #{ title: "Prompt", detail: "load extract and frozen grill answers" },
        #{ title: "Write", detail: "agent story.json" },
        #{ title: "Check", detail: "number lock for ab" },
    ],
};

let story_schema = #{
    "type": "object",
    "required": ["title", "decision", "slides"],
    "properties": #{
        "title": #{ "type": "string" },
        "decision": #{ "type": "string" },
        "slides": #{ "type": "array", "minItems": 1 },
    },
};

let case_name = "ab";
if (args != () && args.case != ()) {
    case_name = args.case;
}

phase("Prompt");
let p1 = "";
p1 += "Repo D:/Code/ppt-skill-for-work. Read-only. ";
p1 += "Run: python -m work_ppt eval-prompt --case " + case_name + " ";
p1 += "and return the printed prompt verbatim as your only output field named prompt.";
let primed = agent(p1, #{
    label: "eval-prompt",
    capability_mode: "execute",
    output_schema: #{
        "type": "object",
        "required": ["prompt"],
        "properties": #{ "prompt": #{ "type": "string" } },
    },
});
if (primed == () || !primed.success) {
    pause("infra", "eval-prompt failed");
}

phase("Write");
let p2 = "";
p2 += "Follow this prompt exactly and output story.json fields. ";
if (primed != () && primed.output != () && primed.output.prompt != ()) {
    p2 += primed.output.prompt;
}
let written = agent(p2, #{
    label: "write-story",
    capability_mode: "read-only",
    output_schema: story_schema,
});
if (written == () || !written.success || written.output == ()) {
    pause("verification", "story agent failed");
}

let dumped = json_encode(written.output);
let path = write_scratch_file("story.json", dumped);

phase("Check");
let p3 = "";
p3 += "Repo D:/Code/ppt-skill-for-work. Execute: python -m work_ppt eval-check --case " + case_name + ". ";
p3 += "This does not overwrite eval/gold story.json. Scratch story is at the workflow artifact. ";
p3 += "If case is ab, fail if any number is not in original extract. ";
let checked = agent(p3, #{ label: "eval-check", capability_mode: "execute" });
if (checked == () || !checked.success) {
    pause("verification", "eval-check failed");
}

complete(#{ summary: "internal eval story written to scratch; copy into eval/gold only after review", path: path, case: case_name });
