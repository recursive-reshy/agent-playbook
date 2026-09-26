from pydantic import BaseModel
from prompt_chaining.models import Outline

MIN_SECTIONS = 3
MAX_SECTIONS = 6
MIN_POINTS = 2
MAX_POINTS = 4

class GateResult( BaseModel ):
    passed: bool
    issues: list[ str ]

def check_outline( outline: Outline ) -> GateResult:
    issues: list[ str ] = []

    if not outline.title.strip():
        issues.append( "Title is empty." )

    count = len( outline.sections )
    if not MIN_SECTIONS <= count <= MAX_SECTIONS:
        issues.append(
            f"Outline has {count} sections; expected {MIN_SECTIONS}-{MAX_SECTIONS}."
        )

    headings = [ s.heading.strip().lower() for s in outline.sections ]
    if len( headings ) != len( set( headings ) ):
        issues.append( "Outline has duplicate section headings." )

    for section in outline.sections:
        points = [ p for p in section.key_points if p.strip() ]
        if not MIN_POINTS <= len( points ) <= MAX_POINTS:
            issues.append(
                f"Section '{section.heading}' has {len(points)} key points; "
                f"expected {MIN_POINTS}-{MAX_POINTS}."
            )

    return GateResult( passed = not issues, issues = issues )