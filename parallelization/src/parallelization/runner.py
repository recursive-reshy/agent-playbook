import asyncio
import time

from parallelization.llm import LLM
from parallelization.models import Aspect, SectionReview, RunResult
from parallelization.reviewers import review_aspect
from parallelization.voting import run_vote

async def timed_review( llm: LLM, aspect: Aspect, code: str ) -> SectionReview:
    start = time.perf_counter()
    try:
        output = await review_aspect( llm, aspect, code )
    except Exception as execption:
        return SectionReview(
            aspect = aspect,
            seconds = time.perf_counter() - start,
            error = f"{type( execption ).__name__}: {execption}"
        )

    return SectionReview(
        aspect = aspect,
        seconds = time.perf_counter() - start,
        output = output
    )

async def run_reviews(
    llm: LLM,
    code: str,
    *, # * here means that all subsequent arguments need to be named. i.e run_reviews( sequential = True )
    sequential: bool = False
) -> list[ SectionReview ]:
    if sequential:
        return  [ await timed_review( llm, aspect, code ) for aspect in Aspect ]

    # gather excepts an argument for each aspect
    # * spreads these arguments
    # i.e asyncio.gather( timed_review( ..., SECURITY, ... ), timed_review( ..., PERFORMANCE, ... ), timed_review( ..., READABILITY, ... ) )
    reviews = reviews = await asyncio.gather( *( timed_review( llm, aspect, code ) for aspect in Aspect ) )

    return list( reviews )

async def run_all(
    llm: LLM,
    code: str,
    *,
    sequential: bool = False
) -> RunResult:
    start = time.perf_counter()

    if sequential:
        reviews = await run_reviews( llm, code, sequential = True )
        vote = await run_vote( llm, code, sequential = True )
    else:
        reviews, vote = await asyncio.gather(
            run_reviews( llm, code ),
            run_vote( llm, code )
        )

    return RunResult( 
        reviews = reviews,
        vote = vote,
        seconds = time.perf_counter() - start
    )