import sys
from collections.abc import AsyncGenerator

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.memory import create_connected_server_and_client_session

from betterprose.mcp_server import mcp


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
        "list_betterprose_profiles",
    }
    assess = next(tool for tool in tools.tools if tool.name == "assess_prose")
    assert "assess this with BetterProse" in (assess.description or "")


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
            assert "assess_prose" in {tool.name for tool in tools.tools}
            result = await session.call_tool(
                "assess_prose",
                {
                    "text": "The recommendation matters because readers need clear evidence.",
                    "provider": "local",
                },
            )
            assert not result.isError
            assert result.structuredContent is not None
            assert result.structuredContent["provider"] == "local"
