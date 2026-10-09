from enum import StrEnum

from pydantic import BaseModel, ValidationError

from routing.classifier import classify
from routing.config import settings
from routing.handlers import handle, pick_model
from routing.models import RouteDecision

class Outcome( StrEnum ):
    HANDLED = "handle"
    HUMAN_REVIEWED = "human_reviewed"

class RouteResult( BaseModel ):
    ticket: str
    outcome: Outcome
    decision: RouteDecision | None = None
    model: str | None = None
    reply: str | None = None
    review_reason: str | None = None

def route( ticket: str ) -> RouteResult:
    try:
        decision = classify( ticket )
    except ValidationError as execption:
        return RouteResult(
            ticket = ticket,
            outcome = Outcome.HUMAN_REVIEWED,
            review_reason = f"Classifier output failed validation ({execption.error_count()} errors)"
        )

    if not is_confident(decision):
        return RouteResult(
            ticket = ticket,
            outcome = Outcome.HUMAN_REVIEWED,
            decision = decision,
            review_reason=(
                f"Low confidence: {decision.confidence:.2f} "
                f"< threshold {settings.confidence_threshold}"
            )
        )

    model = pick_model( decision.complexity )
    reply = handle( ticket, decision, model )

    return RouteResult(
        ticket = ticket,
        outcome = Outcome.HANDLED,
        decision = decision,
        model = model,
        reply = reply
    )

def is_confident( decision: RouteDecision ) -> bool:
    return decision.confidence >= settings.confidence_threshold