from __future__ import annotations

import os
from typing import Literal, cast

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from betterprose.mcp_tools import (
    ProfileCatalog,
    ProfileName,
    ProviderName,
    assess_pasted_prose,
    list_profiles,
)
from betterprose.models import AssessmentReport

Transport = Literal["stdio", "streamable-http"]


def _port() -> int:
    raw = os.getenv("BETTERPROSE_MCP_PORT", "8000")
    try:
        port = int(raw)
    except ValueError as exc:
        raise RuntimeError("BETTERPROSE_MCP_PORT must be an integer.") from exc
    if not 1 <= port <= 65535:
        raise RuntimeError("BETTERPROSE_MCP_PORT must be between 1 and 65535.")
    return port


SERVER_INSTRUCTIONS = """
BetterProse is the canonical prose assessment engine.

When a user asks to "assess this with BetterProse", "grade this with
BetterProse", "use BetterProse on this draft", or asks for a BetterProse
report, call assess_prose. Pass the user's prose unchanged. Do not imitate the
rubric in the host model when the tool is available.

Present the returned reader account, score and confidence, strengths, revision
priorities, integrity status, and passage-level criterion evidence. State the
provider. Do not infer AI authorship or hide uncertainty.
""".strip()

mcp = FastMCP(
    "BetterProse",
    instructions=SERVER_INSTRUCTIONS,
    json_response=True,
    host=os.getenv("BETTERPROSE_MCP_HOST", "127.0.0.1"),
    port=_port(),
)


@mcp.tool()
def assess_prose(
    text: str,
    profile: ProfileName = "academic_argument",
    audience: str | None = None,
    purpose: str | None = None,
    provider: ProviderName = "auto",
) -> AssessmentReport:
    """Assess pasted prose with the canonical BetterProse rubric pipeline.

    Call this tool whenever the user says "assess this with BetterProse" or
    requests a BetterProse grade, critique, or report. Return the tool's
    evidence and uncertainty; do not substitute the host model's own rubric.
    """
    try:
        return assess_pasted_prose(
            text,
            profile=profile,
            audience=audience,
            purpose=purpose,
            provider=provider,
        )
    except (ValueError, RuntimeError) as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool()
def list_betterprose_profiles() -> ProfileCatalog:
    """List BetterProse genre profiles, versions, criteria, and weights."""
    return list_profiles()


@mcp.prompt()
def assess_with_betterprose(
    prose: str,
    profile: ProfileName = "academic_argument",
    audience: str = "",
    purpose: str = "",
) -> str:
    """Create a host prompt that requires the canonical BetterProse tool."""
    return (
        "Call the BetterProse assess_prose tool with the following values. "
        "Present its returned evidence and uncertainty without replacing its "
        "assessment with your own.\n\n"
        f"profile: {profile}\n"
        f"audience: {audience or 'not supplied'}\n"
        f"purpose: {purpose or 'not supplied'}\n\n"
        f"prose:\n{prose}"
    )


def main() -> None:
    """Run the BetterProse MCP server."""
    transport = os.getenv("BETTERPROSE_MCP_TRANSPORT", "stdio")
    if transport not in {"stdio", "streamable-http"}:
        raise SystemExit("BETTERPROSE_MCP_TRANSPORT must be 'stdio' or 'streamable-http'.")
    mcp.run(transport=cast(Transport, transport))


if __name__ == "__main__":
    main()
