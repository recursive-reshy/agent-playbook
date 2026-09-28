import anthropic

from routing.client import client
from routing.config import settings
from routing.models import RouteDecision

ROUTE_TOOL = {
    "name": "route_ticket",
    "description": "Record the routing decision for a customer support ticket.",
    "input_schema": RouteDecision.model_json_schema()
}

SYSTEM_PROMPT = """
    You are the triage step of a customer support system.
    Read the ticket and decide which team should handle it. Do not answer the ticket.

    Categories:
    - billing: charges, invoices, refunds, payment methods, plan pricing.
    - technical: bugs, errors, features not working, integrations, performance.
    - account: logging in, passwords, profile and settings, access, closing an account.
    - general: anything else, such as product questions, feedback, or feature requests.

    If a ticket plausibly fits more than one category, pick the best fit and lower your confidence.
"""

def classify( ticket: str ) -> RouteDecision:
    response = client.messages.create(
        model = settings.classifier_model,
        max_tokens = 512,
        system = SYSTEM_PROMPT,
        tools = [ ROUTE_TOOL ],
        tool_choice = { 
            "type": "tool",
            "name": "route_ticket"
        },
        messages = [ 
            { "role": "user", "content": f"<ticket>\n{ticket}\n</ticket>" }
        ]
    )

    tool_use = next( block for block in response.content if block.type == "tool_use" )

    return RouteDecision.model_validate( tool_use.input ) 