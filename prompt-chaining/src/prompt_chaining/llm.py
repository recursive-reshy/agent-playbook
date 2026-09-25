from typing import TypeVar
# Antropic
import anthropic
# Pydantic
from pydantic import BaseModel
# Config
from prompt_chaining.config import settings

client = anthropic.Anthropic( api_key = settings.anthropic_api_key )

T = TypeVar( "T", bound = BaseModel )

def complete_text( prompt: str, system: str ) -> str:
    response = client.messages.create(
        model = settings.model,
        max_tokens = settings.max_tokens,
        system = system,
        messages = [ { "role": "user", "content": prompt } ]
    )

    return "".join(
        block.text for block in response.content if block.type == "text"
    )

def complete_structured( prompt: str, system: str, output_model: type[ T ] ) -> T:
    tool = {
        "name": "submit_out",
        "description": "Submit your answer in the required format.",
        "input_schema": output_model.model_json_schema()
    }

    response = client.messages.create(
        model = settings.model,
        max_tokens = settings.max_tokens,
        system = system,
        tools = [ tool ],
        tool_choice = { "type": "tool", "name": "submit_output" },
        messages = [ { "role": "user", "content": prompt } ]
    )

    for block in response.content:
        if block.type == "tool_user":
            return output_model.model_validate( block.input )
    raise ValueError( "Model did not return structured output" )