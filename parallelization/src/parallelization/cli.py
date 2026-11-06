import argparse
import asyncio
import sys
from pathlib import Path

from parallelization.llm import LLM
from parallelization.models import ReviewReport
from parallelization.report import build_report, format_report
from parallelization.runner import run_all

def read_code( path: str | None ) -> tuple[ str, str ]:
    if path:
        return Path( path ).read_text( encoding = "utf-8" ), path
    return sys.stdin.read(), "stdin"

async def review( code: str, source: str, sequential: bool ) -> ReviewReport:
    llm = LLM()
    result = await run_all( llm, code, sequential = sequential )
    return build_report( 
        source, 
        result.reviews,
        result.vote,
        result.seconds,
        sequential
    )

def main() -> None:
    parser = argparse.ArgumentParser(
        prog = "parrallelization",
        description = "Review code with parallel LLM calls"
    )
    sub = parser.add_subparsers( dest = "command", required = True )

    review_cmd = sub.add_parser( "review", help = "Review a file, or code piped in on stdin." )
    review_cmd.add_argument( "file", nargs = "?", help = "Path to the code. Reads stdin if omitted." )
    review_cmd.add_argument( "--sequential", action = "store_true", help = "Run all calls one at a time." )
    review_cmd.add_argument( "--json", action = "store_true", help = "Print the full report as JSON." )

    args = parser.parse_args()

    if args.command == "review":
        code, source = read_code( args.file )
        if not code.strip():
            parser.error( "no code given: pass a file path or pipe code in" )

        report = asyncio.run( review( code, source, args.sequential ) )
        print(
            report.model_dump_json( indent = 2 ) if args.json else format_report( report )
        )