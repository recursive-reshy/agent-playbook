from enum import StrEnum

from pydantic import BaseModel, Field

class Category( StrEnum ):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    GENERAL = "general"

class Complexity(StrEnum):
    SIMPLE = "simple"
    COMPLEX = "complex"

class RouteDecision( BaseModel ):
    reasoning: str = Field(
        description="One or two sentences explaining why this ticket fits the chosen category and complexity."
    )
    category: Category
    complexity: Complexity = Field(
        description="simple: a short, direct reply fully resolves it. "
        "complex: needs troubleshooting or investigation, asks several things at once, "
        "or describes a multi-step situation."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="How confident you are in the category, from 0.0 to 1.0.",
    )