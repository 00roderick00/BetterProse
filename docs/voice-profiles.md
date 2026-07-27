# BetterProse voice profiles

BetterProse voice profiles make a writer's recurring rhetorical choices
available as explicit, versioned revision constraints. They are not style
scores, authorship detectors, or permission to add biographical material.

The first installed profile is `roderick_b_jones` version 2. It was supplied by
Roderick B Jones and describes a British-American analytical voice calibrated
against his 1994 Cambridge MPhil, the *Current Preoccupations* corpus
(2009–2019), and recent essays. Those works are named as provenance; their text
is not bundled with BetterProse.

## What the profile captures

The profile separates the voice's stable features from two context-dependent
registers.

### Historian's essay

This register is intended for long-form, academic, and reflective prose. It
favours balanced sentences that carry argument through subordinate clauses,
paragraphs that function as units of argument, and the elimination of
alternatives before the positive case is constructed. It avoids bullets and
does not add section headers to pieces under 1,500 words.

### Futurist column

This register is intended for writing about security, technology, markets, and
forward risk. It allows shorter paragraphs, one pulled-out thesis line, a
compact rhetorical-question pivot, and an operational or practitioner frame.

With `register=auto`, the host model selects between these registers using the
piece's genre, audience, and purpose. A caller can instead choose
`historian_essay` or `futurist_column` explicitly.

Both registers share the profile's central analytical movement:

> incident → system → trajectory → response

Other recurring techniques include a historically grounded analogy, calibrated
confidence, at most one coined concept, one vivid image, one aphoristic line,
and a forward-leaning close. These are options governed by the needs of the
piece, not boxes that every revision must tick. BetterProse specifically tells
the revising model not to force them.

## Safety boundary

A voice profile can influence cadence, structure, diction, stance, spelling,
and patterns of development. It cannot supply facts.

BetterProse therefore requires a voice revision to:

- preserve names, dates, numbers, quotations, citations, first-person claims,
  and degrees of certainty;
- avoid invented biography, expertise, memories, incidents, observations,
  sources, and historical analogies;
- flag missing information rather than manufacture it;
- create a separate candidate rather than overwrite the source;
- return a diff and fact-lock audit;
- identify the exact voice version and register used.

The fact lock detects changed numbers, URLs, quotations, and citation-like
tokens. It cannot prove that every implication or unsupported claim is
unchanged, so the candidate still requires the writer's review.

## Use from the command line

List installed profiles:

```bash
betterprose voices
```

Create a voice-matched candidate:

```bash
betterprose revise draft.md \
  --provider openai \
  --voice roderick_b_jones \
  --register auto \
  --focus voice,structure,clarity \
  --fact-lock strict
```

For an academic or reflective essay, select the register directly:

```bash
betterprose revise draft.md \
  --provider openai \
  --voice roderick_b_jones \
  --register historian_essay
```

The local provider accepts and records the profile but deliberately does not
claim to reproduce it. It performs safe mechanical cleanup and adds an
unresolved-issue warning. Substantive voice revision requires the optional
model-backed provider or the host-assisted MCP workflow.

## Use from an MCP-connected AI

Once BetterProse is connected, paste a draft and say:

> Revise this in my BetterProse voice.

The default no-extra-key workflow is:

1. The AI calls `prepare_voice_revision` with the source unchanged.
2. BetterProse returns the versioned profile, selected register, source,
   rhetorical context, and preservation constraints.
3. The AI creates a complete candidate while treating the source as untrusted
   prose rather than instructions.
4. The AI calls `finalize_voice_revision`.
5. BetterProse audits locked items and returns the candidate, diff, change
   summary, unresolved issues, and warnings.

This uses the model already hosting the conversation. It does not require a
separate model API key. The result records `provider="host-assisted"` and the
host model name when the client supplies it.

Useful requests include:

> Revise this in my BetterProse voice using the historian's essay register.

> Integrate this passage into the article in my Roderick B Jones voice. Keep
> the existing facts and use American spelling for a US professional audience.

> Rework this as a futurist column in my BetterProse voice. Do not add a
> historical analogy unless the supplied evidence supports one.

## Relationship to assessment

BetterProse's twelve-part quality rubric includes voice, ethos, and originality
of perception, but it does not reward resemblance to Roderick B Jones or any
other named writer. A piece can match the profile and still be weak; a strong
piece can depart from it.

The voice profile is therefore recorded only as revision provenance. It does
not alter assessment weights, add points, or prove who wrote the result.

## Versioning and authorship

The source of truth is
`src/betterprose/voices/roderick_b_jones.yaml`. Revisions to the profile should
increment its version and explain any material change to registers, principles,
or safeguards. This keeps old revision reports interpretable.

Using a personal voice profile also creates an authorship responsibility. The
writer should review and approve the candidate, verify its claims, and disclose
material AI assistance when the publication, institution, or assignment
requires it.
