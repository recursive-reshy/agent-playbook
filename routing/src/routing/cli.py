import argparse
import sys

from routing.router import Outcome, RouteResult, route

def format_result( result: RouteResult ) -> str:
    lines: list[ str ] = []

    if result.decision:
        decision = result.decision
        lines.append( f"Route:      {decision.category} / {decision.complexity}  (confidence {decision.confidence:.2f})" )
        lines.append( f"Reasoning: {decision.reasoning}" )

    if result.outcome is Outcome.HUMAN_REVIEWED:
        lines.append( f"Outcome: human review ({result.review_reason})" )
    else:
        lines.append( f"Model: {result.model}" )
        lines.append( "" )
        lines.append( result.reply or "" )

    return "\n".join( lines )

def main() -> None:
    parser = argparse.ArgumentParser(
        prog = "routing",
        description = "Classify a support ticket and route it to the right handler."
    )

    parser.add_argument( "ticket", nargs="?", help="Ticket text. Read from stdin if omitted." )
    parser.add_argument( "--json", action="store_true", help="Print the full RouteResult as JSON." )
    args = parser.parse_args()

    ticket = ( args.ticket if args.ticket is not None else sys.stdin.read() ).strip()

    if not ticket:
        parser.error( "no ticket given: pass it as an argument or pipe it in" )

    result = route( ticket )
    print( result.model_dump_json( indent = 2 ) if args.json else format_result( result ) )