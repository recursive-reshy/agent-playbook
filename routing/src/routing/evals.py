from pathlib import Path
from pydantic import BaseModel, ValidationError

from routing.classifier import classify
from routing.models import Category, Complexity
from routing.router import is_confident

class LabelledTicket( BaseModel ):
    ticket: str
    category: Category
    complexity: Complexity
    ambiguous: bool = False

def load_cases( path: Path ) -> int:
    cases = load_cases( path )
    category_hits = complexity_hits = 0
    caught_ambiguous = unneeded_reviews = 0
    misroutes: list[ str ] = []

    for case in cases:
        try:
            decision = classify( case.ticket )
        except ValidationError:
            decision = None

        reviewed = decision is None or not is_confident( decision )
        cat_ok = decision is not None and decision.category == case.category
        cx_ok = decision is not None and decision.complexity == case.complexity
        category_hits += cat_ok
        complexity_hits += cx_ok

        if case.ambiguous:
            caught_ambiguous += reviewed
        elif reviewed:
            unneeded_reviews += 1
        elif not cat_ok:
            got = decision.category if decision else "invalid"
            misroutes.append( f"expected {case.category}, got {got}: {case.ticket}" )            

        got_label = (
            f"{decision.category}/{decision.complexity} @ {decision.confidence:.2f}"
            if decision
            else "invalid output"
        )

        print(
            f"{'✓' if cat_ok else '✗'} cat  {'✓' if cx_ok else '✗'} cx  "
            f"{'R' if reviewed else ' '}  {got_label:<28} {case.ticket[:60]}"
        )

        total = len( cases )
        ambiguous_total = sum( case.ambiguous for case in cases )
        clear_total = total - ambiguous_total

        print()
        print(f"Category accuracy:     {category_hits}/{total}")
        print(f"Complexity accuracy:   {complexity_hits}/{total}")
        print(f"Ambiguous -> review:   {caught_ambiguous}/{ambiguous_total}")
        print(f"Clear -> review:       {unneeded_reviews}/{clear_total}  (needless human work)")
        print(f"Confident misroutes:   {len(misroutes)}")

        for misroute in misroutes:
            print( f"f -{misroute}" )

        return 1 if misroutes else 0