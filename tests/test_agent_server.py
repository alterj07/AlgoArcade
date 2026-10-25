import asyncio
import sys
from dataclasses import asdict
from typing import Any, get_args

from mcp import Client, StdioServerParameters

from algoarcade.agent.server import ButtonName
from algoarcade.backends.base import Button
from algoarcade.backends.fake import FakeBackend
from algoarcade.games.fake import FakeReader

PARAMS = StdioServerParameters(command=sys.executable, args=["-m", "algoarcade.agent.server"])
# Two steps right lands on the chest, A opens it. One press call is one decision.
TO_THE_CHEST = ["RIGHT", "RIGHT", "A"]


async def tools_press_and_read() -> tuple[list[str], dict[str, Any] | None, dict[str, Any] | None]:
    async with Client(PARAMS, raise_exceptions=True) as client:
        listing = await client.list_tools()
        pressed = await client.call_tool("press", {"buttons": TO_THE_CHEST})
        read_back = await client.call_tool("get_state")
    names = [tool.name for tool in listing.tools]
    return names, pressed.structured_content, read_back.structured_content


async def fresh_state() -> dict[str, Any] | None:
    async with Client(PARAMS, raise_exceptions=True) as client:
        return (await client.call_tool("get_state")).structured_content


def test_two_tools_and_press_matches_a_direct_backend_run() -> None:
    names, pressed, read_back = asyncio.run(tools_press_and_read())
    backend = FakeBackend()
    backend.press([Button[name] for name in TO_THE_CHEST])
    assert sorted(names) == ["get_state", "press"]
    assert pressed == read_back == asdict(FakeReader().read(backend))


def test_get_state_matches_a_fresh_read() -> None:
    assert asyncio.run(fresh_state()) == asdict(FakeReader().read(FakeBackend()))


def test_button_names_are_the_backend_enum() -> None:
    assert set(get_args(ButtonName)) == {button.name for button in Button}
