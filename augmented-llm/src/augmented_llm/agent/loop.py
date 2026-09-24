# Anthropic
from anthropic import Anthropic
# Settings
from ..config import settings
# Tools
from .tools import TOOLS

_client = Anthropic( api_key = settings.ANTHROPIC_API_KEY )

def run_turn( messages: list, tool_implementation: dict ) -> str:
    """Send the conversation to Claude, resolving any tool calls it makes,
    looping until it produces a final text answer.

    `messages` is mutated in place — every user message, tool call, and
    tool result stays in the list, which is what makes memory work across
    multiple calls to this function.
    """
    while True:
        response = _client.messages.create(
            model = settings.ANTHROPIC_MODEL,
            max_tokens = 1024,
            tools = TOOLS,
            messages = messages
        )

        messages.append( { "role": "assistant", "content": response.content } )

        if response.stop_reason != "tool_use":
            return "".join(
                block.text for block in response.content if block.type == "text"
            )

        tool_result = []

        for block in response.content:
            if block.type != "tool_use":
                continue

            print( f"  [tool call] { block.name }( { block.input } )" )
            implementation = tool_implementation[ block.name ]
            result = implementation( **block.input)

            tool_result.append( { 
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            } )

        messages.append( { "role": "user", "content": tool_result } )