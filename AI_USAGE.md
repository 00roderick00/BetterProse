# Using BetterProse from an AI system

## Canonical behavior

If the BetterProse MCP server is connected, call `assess_prose` whenever the
user says:

- "Assess this with BetterProse."
- "Grade this prose with BetterProse."
- "Use BetterProse on this draft."
- "Give me a BetterProse report."

Pass the user's prose unchanged in `text`. Supply `profile`, `audience`, and
`purpose` when the user provides them. If the genre is genuinely ambiguous,
ask one concise question before choosing a profile. Otherwise use
`academic_argument`.

Present the returned reader account, overall score and confidence, principal
strengths, three revision priorities, integrity status, and criterion
evidence. State which provider produced the report. Do not reinterpret a
low-confidence local report as a definitive grade.

Do not:

- imitate BetterProse when the canonical tool is available;
- infer AI authorship;
- optimize against an AI detector;
- treat punctuation or sentence variation as proof of quality;
- invent evidence, facts, citations, quotations, or personal experience;
- hide integrity warnings or assessment uncertainty.

## When MCP is unavailable

An AI that can only read this repository may explain the rubric or help the
user install BetterProse, but it must not claim that an improvised response is
a canonical BetterProse report.

It should say:

> I can apply a non-canonical reading inspired by the BetterProse rubric, or
> help you connect the BetterProse MCP server so the actual engine produces the
> report.

The repository's YAML rubrics and prompt files are transparent references, not
a substitute for executing the validated pipeline.
