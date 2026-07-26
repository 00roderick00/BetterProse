# BetterProse MCP server

The BetterProse MCP server lets an AI client call the same validated assessment
pipeline used by the CLI. It uses the official stable Python MCP SDK and local
stdio transport by default.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[openai]"
```

The OpenAI extra is optional. Without `OPENAI_API_KEY`, the server can still use
the deterministic local provider.

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

The server inherits environment variables from the AI application. Configure
`OPENAI_API_KEY` in that application's environment when you want substantive
model-assisted assessment. Do not place a secret directly in a repository
configuration file.

After connecting the server, ask:

> Assess this with BetterProse: [paste prose]

The server instructions and `assess_prose` tool description tell the host AI to
use the canonical tool for that request.

## Tools

### `assess_prose`

Inputs:

- `text`: pasted prose, unchanged;
- `profile`: `academic_argument`, `professional_prose`, or
  `narrative_nonfiction`;
- `audience`: optional intended reader;
- `purpose`: optional intended effect;
- `provider`: `auto`, `local`, or `openai`.

Output is the complete structured `AssessmentReport`, including criterion
evidence, locally calculated points, confidence, integrity notes, and warnings.

### `list_betterprose_profiles`

Returns every installed rubric profile with its version, description, and
criterion weights.

## Prompts

`assess_with_betterprose` is available to MCP clients that expose server prompt
templates. The prompt tells the host to call the tool and present its returned
evidence without substituting the host model's own grading.

## Provider selection

`provider="auto"` selects:

1. OpenAI when `OPENAI_API_KEY` exists;
2. otherwise the low-confidence local provider.

Every assessment report records the selected provider and model. A request for
`provider="openai"` fails clearly when credentials or the optional dependency
are unavailable.

## Limits and security

- Pasted prose is limited to 100,000 characters by default. Change this with
  `BETTERPROSE_MAX_CHARS`.
- Stdio is local and is the recommended transport for personal use.
- The optional `streamable-http` transport binds to `127.0.0.1` by default.
- Do not expose the HTTP server publicly without authentication, transport
  security, request limits, and an explicit threat review.
- Model-assisted calls may send the pasted prose to the configured model
  provider. Offline mode keeps assessment local.
- The server never writes the pasted prose to disk.

## Optional local HTTP transport

For clients that require a URL:

```bash
BETTERPROSE_MCP_TRANSPORT=streamable-http betterprose-mcp
```

The default endpoint is `http://127.0.0.1:8000/mcp`. Configure the host and port
with `BETTERPROSE_MCP_HOST` and `BETTERPROSE_MCP_PORT`.

## Verification

The test suite connects an in-memory MCP client to the real server, lists its
tools and prompts, and calls `assess_prose`. It also launches the packaged
stdio entry point in a subprocess. Tests use no configured AI client, network
access, or paid API calls.
