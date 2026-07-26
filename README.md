# BetterProse

BetterProse is a local-first, rubric-driven prose assessment and revision
toolkit. It evaluates writing against transparent criteria, cites textual
evidence for its judgments, proposes controlled revisions, and produces
auditable reports.

BetterProse does **not** detect AI authorship. It does not treat punctuation,
sentence-length variation, unusual vocabulary, or other surface features as
proof of authorship or writing quality.

## Research foundations

BetterProse is grounded in rhetoric and composition theory, writing instruction
at Stanford, Princeton, Harvard, Oxford, and Cambridge, professional writing-
assessment guidance, meta-analyses of rubrics and feedback, and current research
on automated essay scoring and AI-detector bias.

Its twelve criteria are a transparent synthesis, not a hidden model preference.
The system separates prose quality, source integrity, authorial process, and
AI-use compliance; requires exact textual evidence; calculates scores from
versioned rubric weights; and treats AI as a formative second reader rather than
an autonomous high-stakes grader.

Read the full 3,300-word [research foundations and design
rationale](docs/research-foundations.md), including criterion provenance,
research-to-product traceability, limitations, selected academic sources, and
the empirical validation program.

BetterProse is **research-grounded and software-validated**, but it does not
claim psychometric validation for admissions, employment, publication, or
autonomous grading.

## What the MVP includes

- `betterprose assess`: score prose with a 12-part, genre-sensitive rubric.
- `betterprose coach`: produce three prioritized revision goals without
  changing the source.
- `betterprose revise`: create a separate candidate revision and fact-lock
  audit; the original is never overwritten.
- `betterprose compare`: compare drafts with an auditable unified diff.
- `betterprose profiles`: inspect the installed rubric profiles.
- `betterprose-mcp`: expose BetterProse as structured tools to MCP-compatible
  AI assistants.
- Markdown, HTML, and JSON assessment reports.
- Academic argument, professional prose, and narrative nonfiction profiles.
- An offline provider for private, deterministic diagnostics.
- An optional OpenAI provider using the Responses API and Structured Outputs.

## Install

BetterProse requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,openai]"
```

The offline provider needs no account or API key:

```bash
betterprose assess examples/sample_essay.md --provider local
```

For model-assisted assessment, set an API key in your environment:

```bash
export OPENAI_API_KEY="your-key"
betterprose assess examples/sample_essay.md --provider openai
```

The default model may be changed with `BETTERPROSE_MODEL`. Every report records
the provider and model that produced it.

## Use BetterProse from an AI assistant

BetterProse includes a local Model Context Protocol (MCP) server. Once it is
connected to an MCP-compatible AI, you can paste prose into that AI and say:

> Assess this with BetterProse.

By default, the AI calls `prepare_assessment`, evaluates the returned rubric
with the model already hosting the conversation, and submits its findings to
`finalize_assessment`. BetterProse validates the quoted evidence and calculates
the score. This host-assisted workflow needs no separate model API key.

Choose either installation method below. To use a local clone:

```bash
git clone https://github.com/00roderick00/BetterProse.git
cd BetterProse
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Alternatively, let an MCP-compatible AI install and run the current draft
branch directly from GitHub with `uvx`:

```json
{
  "mcpServers": {
    "betterprose": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/00roderick00/BetterProse.git@agent/prosebench-mvp",
        "betterprose-mcp"
      ]
    }
  }
}
```

That configuration needs `uv`/`uvx` installed on the same computer as the AI
application. While pull request #1 is a draft, the Git URL explicitly selects
its branch. After that pull request is merged, remove
`@agent/prosebench-mvp` to install from the repository's default branch.

For a previously cloned copy, add this local stdio server instead:

```json
{
  "mcpServers": {
    "betterprose": {
      "command": "/absolute/path/to/BetterProse/.venv/bin/betterprose-mcp",
      "args": []
    }
  }
}
```

Replace the command with the real absolute path on your computer. Restart or
refresh the AI application after changing its MCP configuration.

The server publishes:

- `prepare_assessment`: return the rubric and numbered prose for the current
  host AI to evaluate without a separate model call.
- `finalize_assessment`: validate exact quoted evidence, enforce criterion
  coverage, calculate weighted scores, and return the canonical report.
- `assess_prose`: optionally run the independent OpenAI-backed engine or the
  low-confidence local diagnostic.
- `list_betterprose_profiles`: the installed genre profiles and weights.
- `assess_with_betterprose`: a reusable MCP prompt for clients that expose
  server prompts.

The default two-tool workflow uses the AI already open in the conversation and
records `provider="host-assisted"`. Results may differ among host models, so
the report also records the host model when the client supplies its name.

The optional `assess_prose` tool retains an independent-engine mode. Its
`provider="auto"` uses OpenAI when `OPENAI_API_KEY` is available to the server
process and otherwise uses the low-confidence offline provider.

See [docs/mcp.md](docs/mcp.md) for configuration, security boundaries, and
testing. [AI_USAGE.md](AI_USAGE.md) provides portable instructions for AI
systems that can read a repository but cannot connect to MCP.

An AI system must support tools or MCP to run the canonical engine. Merely
pointing an AI at the GitHub page does not install or execute BetterProse.

## Assess

```bash
betterprose assess draft.md \
  --profile academic_argument \
  --audience "educated nonspecialist" \
  --purpose "persuade readers that the policy should change"
```

The command writes:

```text
reports/draft/
├── assessment.json
├── assessment.md
└── assessment.html
```

The application—not the model—calculates weighted totals from the versioned
rubric.

## Coach

```bash
betterprose coach draft.md --profile academic_argument
```

Coaching starts with global issues such as purpose, reasoning, support, and
structure. It limits the plan to three consequential priorities.

## Revise under fact lock

```bash
betterprose revise draft.md \
  --provider openai \
  --focus development,macrostructure,diction \
  --fact-lock strict
```

Revision always creates a separate candidate. The audit compares numbers,
URLs, quotations, citation-like tokens, and named references before and after.
Strict mode marks a candidate as blocked when a locked item changes; it never
silently overwrites the source.

The offline provider performs conservative mechanical cleanup only. It will
not pretend that local statistics can perform developmental editing.

## Compare drafts

```bash
betterprose compare draft-v1.md draft-v2.md
```

The comparison report contains document statistics, a unified diff, and a
claim-surface warning when locked items have changed.

Add rubric-aware score deltas when you want to compare substantive movement:

```bash
betterprose compare draft-v1.md draft-v2.md \
  --assess \
  --profile academic_argument \
  --provider local
```

The report lists before-and-after ratings for every criterion. Treat local
provider deltas as low-confidence diagnostics, not proof that a revision is
better.

## Rubric

All profiles share twelve criterion IDs:

1. rhetorical fit
2. motive, problem, or stakes
3. controlling idea, claim, or tension
4. development, reasoning, or narrative movement
5. support, evidence, and concrete particulars
6. complexity, qualification, and counterpressure
7. macrostructure and sequence
8. paragraph and section cohesion
9. sentence clarity, emphasis, and rhythm
10. diction, precision, and economy
11. voice, ethos, and originality of perception
12. conventions, accessibility, and presentation

Each profile changes the weights while preserving the construct. YAML files
are validated to total 100 points and reports record the profile version.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
python -m betterprose --help
pytest tests/test_mcp_server.py
```

See [docs/methodology.md](docs/methodology.md) for the assessment model and
[docs/limitations.md](docs/limitations.md) before using results in a
consequential setting.

## Project principles

1. Finished-prose quality, factual integrity, authorial process, and AI-use
   compliance are separate judgments.
2. Every model-assisted score requires passage-level evidence.
3. Numerical totals come from visible, versioned rubric weights.
4. Revision must preserve claims and expose possible meaning changes.
5. Automated reports are formative second-reader feedback, not autonomous
   high-stakes grades.
6. The project will not add AI detectors, “human scores,” punctuation bans,
   fabricated specificity, or detector-evasion features.

## License

MIT

