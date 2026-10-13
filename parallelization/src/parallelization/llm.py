import asyncio
from typing import TypeVar

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from parallelization.config import Settings, get_settings

T = TypeVar( "T", bound = BaseModel )

TOOL_NAME = "submit_output"

class LLM:
    def __init__( self, settings: Settings | None = None ) -> None:
        self.settings = settings or get_settings()
        self.client = AsyncAnthropic(
            api_key = self.settings.anthropic_api_key.get_secret_value(),
            max_retries = self.settings.max_retries
        )
        # Caps in-flight API calls at max_concurrency; extra calls wait their turn.
        self.semaphore =asyncio.Semaphore( self.settings.max_concurrency )

    async def structured(
        self,
        *,
        model: str,
        system: str,
        user: str,
        schema: type[ T ]
    ) -> T:
        tool = {
            "name": TOOL_NAME,
            "description": "Submit your answer in the required structure",
            "input_schema": schema.model_json_schema()
        }

        async with self.semaphore:
            response = await self.client.messages.create(
                model = model,
                max_tokens = self.settings.max_tokens,
                system = system,
                messages = [ { "role": "user", "content": user } ],
                tools = [ tool ],
                tool_choice = { "type": "tool", "name": TOOL_NAME }
            )

        if response.stop_reason == "max_tokens":
            raise RuntimeError(
                f"{schema.__name__}: response hit max_tokens, so the output is truncated"
            )

        for block in response.content:
            if block.type == "tool_use":
                return schema.model_validate( block.input )

        raise RuntimeError( f"{schema.__name__}: no tool_use block in response" )