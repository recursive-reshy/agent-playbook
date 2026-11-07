import asyncio
import time
from pathlib import Path

from pydantic import BaseModel

from parallelization.llm import LLM
from parallelization.models import VoteResult
from parallelization.voting import run_vote

SNIPPETS_DIR = Path( __file__ ).resolve().parents[2] / "evals" / "snippets"

class Case( BaseModel ):
    name: str
    code: str
    vulnerable: bool

class CaseResult( BaseModel ):
    case: Case
    vote: VoteResult

    @property
    def correct( self ) -> bool:
        return self.vote.flagged == self.case.vulnerable

def load_cases( directory: Path = SNIPPETS_DIR ) -> list[ Case ]:
    cases = []

    for path in sorted( directory.glob( "*.py" ) ):
        if path.name.startswith( "vuln_" ):
            vulnerable = True
        elif path.name.startswith( "safe_" ):
            vulnerable = False
        else:
            raise ValueError( f"{path.name}: file name must start with either vuln_ or safe_" )

        cases.append(
            Case(
                name = path.stem,
                code = path.read_text( encoding = "utf-8" ),
                vulnerable = vulnerable
            )
        )

    if not cases:
        raise ValueError( f"no snippets found in {directory}" )

    return cases

async def evaluate_cases( llm: LLM, cases: list[ Case ] ) -> list[ CaseResult ]:
    votes = await asyncio.gather( *( run_vote( llm, case.code ) for case in cases ) )
    return [ CaseResult( case = case, vote = vote ) for case, vote in zip( cases, votes ) ]

def format_eval( results: list[ CaseResult ], seconds: float ) -> str:
    lines = [ f"{'case':<28} {'truth':<11} {'votes':<7} result" ]

    for result in results:
        truth = "vulnerable" if result.case.vulnerable else "safe"
        votes = f"{result.vote.vulnerable_votes}/{len(result.vote.votes)}"
        verdict = "ok" if result.correct else "WRONG"
        lines.append( f"{ result.case.name:<28} {truth:<11} {votes:<7} {verdict}" )

    vulnerable = [ result for result in results if result.case.vulnerable ]
    safe = [ result for result in results if not result.case.vulnerable ]
    caught = sum( result.vote.flagged for result in vulnerable )
    false_alarms = sum( result.vote.flagged for result in safe )
    failed = sum( result.vote.failed for result in results )

    lines += [
        "",
        f"caught        {caught}/{len(vulnerable)} vulnerable",
        f"false alarms  {false_alarms}/{len(safe)} safe",
        f"failed votes  {failed}",
        f"threshold     {results[0].vote.threshold}",
        f"time          {seconds:.1f}s",
    ]
    return "\n".join( lines )

async def evaluate() -> str:
    cases = load_cases()
    llm = LLM()
    start = time.perf_counter()
    results = await evaluate_cases( llm, cases )

    return format_eval( results, time.perf_counter() - start )