# BetterProse

Better prose through transparent, evidence-backed assessment and revision.

BetterProse is an editing ruleset for the writing of Roderick Jones. It treats editing as evidence: every proposed change is logged in a ledger, cites a numbered rule, and answers one question — why is this better prose?

## Priority order

1. **Prose quality.** Clarity, concision, concreteness, rhythm, argumentative force.
2. **The author's voice.** Two registers, eight signature moves; where a generic rule and the voice conflict, the voice wins.
3. **AI-pattern awareness, as advisory evidence only.** Known AI tells are useful because most of them are weak writing anyway; the tell is a symptom, never the offence. Nothing here bans punctuation or rewrites good sentences to look less machine-made.

## The files

- **[PATTERNS.md](PATTERNS.md)** — the rules. Part I: sixteen prose-quality rules (BP-01 to BP-16) organised by what they protect: precision, economy, honesty, rhythm. Part II: eight voice rules (BPV-01 to BPV-08). Part III: the precedence rules where voice modifies quality.
- **[ASSESSMENT.md](ASSESSMENT.md)** — the protocol. One ledger row per edit; no edit without a pattern ID; no invented facts; coinages survive verbatim.
- **[SKILL.md](SKILL.md)** — the Claude skill wrapper: invocation modes and register selection.
- **[examples/](examples/)** — a worked example: weak paragraph, ledger, final rewrite.

## Acknowledgements

Part I adapts quality patterns first catalogued in [blader/humanizer](https://github.com/blader/humanizer) (MIT, © 2025 Siqi Chen), keeping only the patterns that are faults of prose in their own right and discarding its pure AI-detection heuristics. The plain-style rules restate the Orwell/Gowers tradition.

## Licence

MIT. See [LICENSE](LICENSE).
