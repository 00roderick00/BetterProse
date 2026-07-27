# BetterProse MCP server

The BetterProse MCP server supports two assessment modes and a host-assisted
voice-revision workflow:

1. **Host-assisted (default):** the AI already hosting the conversation applies
   the rubric. BetterProse verifies its evidence and calculates the report. No
   separate model API key is required.
2. **Independent engine (optional):** BetterProse calls its configured OpenAI
   provider or uses its low-confidence deterministic local diagnostic.
3. **Named voice revision:** the host AI applies a versioned BetterProse voice
   profile and BetterProse audits the candidate. This also needs no separate
   model API key.

It uses the official stable Python MCP SDK and local stdio transport by default.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Install `".[openai]"` only if you want the optional independent OpenAI-backed
engine.

## Configure an MCP client

### Run the draft branch directly from GitHub

If `uv`/`uvx` is installed on the same computer as the AI application, copy
`configs/mcp-uvx.json.example` into its MCP configuration:

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

The branch suffix makes this work while pull request #1 remains a draft. After
the pull request is merged, remove `@agent/prosebench-mvp` to follow the
repository's default branch. For reproducible use, replace the branch with a
release tag or commit SHA.

The first launch downloads BetterProse and its dependencies into uv's managed
tool cache. The AI application then starts the local stdio server when needed.

### Run a cloned copy

Copy `configs/mcp.json.example` into the MCP configuration surface used by your
AI application, then replace the command with the absolute path to
`betterprose-mcp` in the virtual environment:

```json
{
  "mcpServers": {
    "betterprose": {
      "command": "/Users/you/projects/BetterProse/.venv/bin/betterprose-mcp",
      "args": []
    }
  }
}
```

The default workflow needs no API key. The server inherits environment
variables from the AI application, so configure `OPENAI_API_KEY` there only
when you want the optional independent engine. Do not place a secret directly
in a repository configuration file.

After connecting the server, ask:

> Assess this with BetterProse: [paste prose]

The server instructions tell the host AI to complete the two-tool workflow and
present only the validated final report.

For a personal voice revision, ask:

> Revise this in my BetterProse voice: [paste prose]

The server tells the host AI to call `prepare_voice_revision`, apply the
returned profile selectively, and pass its complete candidate to
`finalize_voice_revision`.

## Tools

### `prepare_assessment`

Inputs:

- `text`: pasted prose, unchanged;
- `profile`: `academic_argument`, `professional_prose`, or
  `narrative_nonfiction`;
- `audience`: optional intended reader;
- `purpose`: optional intended effect.

Output contains:

- an unpredictable, temporary `assessment_id`;
- the selected versioned rubric with all twelve criteria and rating anchors;
- the document split into numbered paragraphs and sentences;
- safety and evidence instructions;
- the name of the required next tool.

The prose remains in process memory for 30 minutes by default or until a
successful finalization. It is never written to disk.

### `finalize_assessment`

Inputs:

- `assessment_id`: returned by `prepare_assessment`;
- `assessment`: the host model's complete structured `AssessmentDraft`;
- `host_model`: the host model name, when known.

Before returning a report, BetterProse:

- requires every criterion exactly once and in canonical order;
- requires evidence for every criterion;
- confirms each quotation appears at its claimed paragraph or sentence;
- rejects reversed, unknown, or mixed evidence ranges;
- limits evidence quotations to 500 characters;
- calculates criterion points and the total from versioned weights.

Invalid submissions are rejected without consuming the temporary assessment,
so a host can correct and retry. Successful submissions are removed from
memory.

### `assess_prose` (optional independent engine)

Inputs add `provider`: `auto`, `local`, or `openai`.

Output is the complete structured `AssessmentReport`, including criterion
evidence, locally calculated points, confidence, integrity notes, and warnings.

### `list_betterprose_profiles`

Returns every installed rubric profile with its version, description, and
criterion weights.

### `prepare_voice_revision`

Inputs:

- `text`: pasted prose, unchanged;
- `voice`: currently `roderick_b_jones`;
- `register`: `auto`, `historian_essay`, or `futurist_column`;
- `focus`: optional revision priorities;
- `audience` and `purpose`: optional rhetorical context;
- `fact_lock`: `strict` or `advisory`.

The output includes the full versioned profile, the unchanged source,
register-specific guidance, non-invention rules, and a temporary
`revision_id`. The host AI must treat the source as untrusted prose and call
`finalize_voice_revision`.

### `finalize_voice_revision`

Inputs:

- `revision_id`: returned by `prepare_voice_revision`;
- `revision`: the complete revised text, change summary, and unresolved issues;
- `host_model`: the host model name, when known.

The returned `VoiceRevisionReport` records the profile version, register,
provider, model, focus, candidate, unified diff, fact-lock audit, and warnings.
In strict mode, changed locked items mark the candidate as blocked pending
human review.

### `list_betterprose_voices`

Returns installed voice profiles, versions, descriptions, and registers.

## Prompts

MCP clients that expose server prompt templates receive:

- `assess_with_betterprose`, which prepares, evaluates, finalizes, and presents
  a validated assessment;
- `revise_in_roderick_voice`, which prepares, rewrites, finalizes, and presents
  an audited personal-voice candidate.

## Provider selection

Provider selection applies only to optional `assess_prose`.
`provider="auto"` selects:

1. OpenAI when `OPENAI_API_KEY` exists;
2. otherwise the low-confidence local provider.

Every assessment report records the selected provider and model. A request for
`provider="openai"` fails clearly when credentials or the optional dependency
are unavailable.

## Limits and security

- Pasted prose is limited to 100,000 characters by default. Change this with
  `BETTERPROSE_MAX_CHARS`.
- Prepared host sessions expire after 1,800 seconds by default. Change this
  with `BETTERPROSE_HOST_SESSION_TTL_SECONDS`.
- At most 32 unfinished host sessions are held by default. Change this with
  `BETTERPROSE_MAX_PREPARED_ASSESSMENTS`.
- Stdio is local and is the recommended transport for personal use.
- The optional `streamable-http` transport binds to `127.0.0.1` by default.
- Do not expose the HTTP server publicly without authentication, transport
  security, request limits, and an explicit threat review.
- Host-assisted mode exposes the prose to the AI hosting the conversation but
  does not make another model-provider call.
- Voice revision profiles describe rhetorical and stylistic choices. They do
  not authorise the host to invent biographical experience or factual support.
- Independent OpenAI mode sends the prose to the configured API provider.
  Local diagnostic mode keeps assessment inside the server process.
- The server never writes the pasted prose to disk.
- The host is told to treat prose as untrusted data, and BetterProse rejects
  fabricated evidence quotations. These controls reduce prompt-injection risk
  but cannot control every host application's behavior.

## Optional local HTTP transport

For clients that require a URL:

```bash
BETTERPROSE_MCP_TRANSPORT=streamable-http betterprose-mcp
```

The default endpoint is `http://127.0.0.1:8000/mcp`. Configure the host and port
with `BETTERPROSE_MCP_HOST` and `BETTERPROSE_MCP_PORT`.

## Verification

The test suite connects an in-memory MCP client to the real server, lists its
tools and prompts, and completes host-assisted and independent assessments. It
also launches the packaged stdio entry point in a subprocess. Tests use no
configured AI client, network access, or paid API calls.
