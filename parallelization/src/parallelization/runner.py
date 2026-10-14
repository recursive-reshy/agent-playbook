import asyncio
import time

from parallelization.llm import LLM
from parallelization.models import Aspect, SectionReview
from parallelization.reviewers import review_aspect

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
    *,
    sequential: bool = False
) -> tuple[ list[ SectionReview ], float ]:
    start = time.perf_counter()

    if sequential:
        reviews = [
            await timed_review( llm, aspect, code ) for aspect in Aspect
        ]
    else:
        # gather excepts an argument for each aspect
        # * spreads these arguments
        # i.e asyncio.gather( timed_review( ..., SECURITY, ... ), timed_review( ..., PERFORMANCE, ... ), timed_review( ..., READABILITY, ... ) )
        reviews = await asyncio.gather(
            *( timed_review( llm, aspect, code ) for aspect in Aspect )
        )

    return list( reviews ), time.perf_counter() - start