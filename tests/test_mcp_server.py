import sys
from collections.abc import AsyncGenerator

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.memory import create_connected_server_and_client_session

from betterprose.mcp_server import mcp
from betterprose.rubric import CORE_CRITERION_IDS


def _host_draft_payload(quotation: str) -> dict[str, object]:
    return {
        "reader_account": "The recommendation is clear but needs fuller development.",
        "principal_strengths": ["The opening gives the reader a specific recommendation."],
        "priority_revisions": ["Develop the recommendation with another concrete detail."],
        "integrity_status": "review_needed",
        "integrity_notes": ["No sources were supplied for factual verification."],
        "findings": [
            {
                "criterion_id": criterion_id,
                "rating": 3.0,
                "confidence": "medium",
                "rationale": "The exact quotation supports this criterion-level judgment.",
                "supporting_evidence": [
                    {
                        "location": "P1",
                        "quotation": quotation,
                        "explanation": "This passage supplies relevant textual evidence.",
                    }
                ],
                "limiting_evidence": [],
                "revision_action": "Develop the relevant feature with one concrete detail.",
            }
            for criterion_id in CORE_CRITERION_IDS
        ],
    }


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client_session() -> AsyncGenerator[ClientSession]:
    async with create_connected_server_and_client_session(
        mcp._mcp_server,
        raise_exceptions=True,
    ) as session:
        yield session


@pytest.mark.anyio
async def test_server_publishes_canonical_tools(client_session: ClientSession) -> None:
    tools = await client_session.list_tools()
    assert {tool.name for tool in tools.tools} == {
        "assess_prose",
        "finalize_assessment",
        "list_betterprose_profiles",
        "prepare_assessment",
    }
    prepare = next(tool for tool in tools.tools if tool.name == "prepare_assessment")
    assert "assess this with BetterProse" in (prepare.description or "")


@pytest.mark.anyio
async def test_server_calls_assessment_pipeline(
    client_session: ClientSession,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = await client_session.call_tool(
        "assess_prose",
        {
            "text": "A proposal should be adopted because it reduces delay.",
            "profile": "academic_argument",
            "provider": "local",
        },
    )
    assert not result.isError
    assert result.structuredContent is not None
    assert result.structuredContent["profile_name"] == "academic_argument"
    assert result.structuredContent["provider"] == "local"
    assert len(result.structuredContent["scores"]) == 12


@pytest.mark.anyio
async def test_server_completes_host_assisted_workflow(
    client_session: ClientSession,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    prose = "A proposal should be adopted because it gives readers clear evidence."
    prepared = await client_session.call_tool(
        "prepare_assessment",
        {
            "text": prose,
            "profile": "academic_argument",
            "audience": "general readers",
        },
    )
    assert not prepared.isError
    assert prepared.structuredContent is not None
    assert len(prepared.structuredContent["criteria"]) == 12

    finalized = await client_session.call_tool(
        "finalize_assessment",
        {
            "assessment_id": prepared.structuredContent["assessment_id"],
            "assessment": _host_draft_payload("gives readers clear evidence"),
            "host_model": "test-host",
        },
    )
    assert not finalized.isError
    assert finalized.structuredContent is not None
    assert finalized.structuredContent["provider"] == "host-assisted"
    assert finalized.structuredContent["model"] == "test-host"
    assert finalized.structuredContent["overall_score"] == 75.0


@pytest.mark.anyio
async def test_server_rejects_fabricated_host_evidence(
    client_session: ClientSession,
) -> None:
    prepared = await client_session.call_tool(
        "prepare_assessment",
        {"text": "The real sentence provides a modest claim."},
    )
    assert prepared.structuredContent is not None
    finalized = await client_session.call_tool(
        "finalize_assessment",
        {
            "assessment_id": prepared.structuredContent["assessment_id"],
            "assessment": _host_draft_payload("A fabricated sentence."),
        },
    )
    assert finalized.isError


@pytest.mark.anyio
async def test_server_publishes_assessment_prompt(client_session: ClientSession) -> None:
    prompts = await client_session.list_prompts()
    assert [prompt.name for prompt in prompts.prompts] == ["assess_with_betterprose"]


@pytest.mark.anyio
async def test_console_entrypoint_works_over_stdio() -> None:
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "betterprose.mcp_server"],
    )
    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert "prepare_assessment" in {tool.name for tool in tools.tools}
            result = await session.call_tool(
                "prepare_assessment",
                {
                    "text": "The recommendation matters because readers need clear evidence.",
                },
            )
            assert not result.isError
            assert result.structuredContent is not None
            assert result.structuredContent["next_tool"] == "finalize_assessment"
