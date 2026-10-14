from parallelization.models import (
    Aspect,
    ReportFinding,
    ReviewReport,
    SectionReview,
    VoteResult
)

def merge_findings( reviews: list[ SectionReview ] ) -> list[ ReportFinding ]:
    merged: list[ ReportFinding ] = []

    for review in reviews:
        if review.output is None:
            continue

        for finding in review.output.findings:
            merged.append(
                ReportFinding( aspect = review.aspect, **finding.model_dump() )
            )

    # Same aspect + same line = same problem reported twice; keep the most severe.
    best: dict[ tuple[ Aspect, int | None ], ReportFinding ] = {}

    for finding in merged:
        key = ( finding.aspect, finding.line )

        if finding.line is None or key not in best or finding.severity.rank < best[ key ].severity.rank:
            best[ key if finding.line is not None else ( finding.aspect, id( finding ) ) ] = finding

    return sorted(
        best.values(),
        key = lambda finding: ( finding.severity.rank, finding.line or 0 )
    )

def build_report(
    source: str,
    reviews: list[ SectionReview ],
    vote: VoteResult,
    seconds: float,
    sequential: bool
) -> ReviewReport:
    return ReviewReport(
        source = source,
        mode = "sequential" if sequential else "parallel",
        seconds = seconds,
        findings = merge_findings( reviews ),
        sections = reviews,
        vote = vote,
    )

def format_report( report: ReviewReport ) -> str:
    lines = [ f"Review of {report.source} ({report.mode}, {report.seconds:.1f}s)", "" ]

    verdict = "FLAGGED" if report.vote.flagged else "cleared"

    lines.append(
        f"Security vote: {verdict} "
        f"{report.vote.vulnerable_votes}/{len(report.vote.votes)} vulnerable, "
        f"threshold {report.vote.threshold}"
    )

    lines.append( "" )

    for finding in report.findings:
        where = f"line {finding.line}" if finding.line else "general"
        lines.append( f"[{finding.severity.upper():<8}] {finding.aspect:<11} {where}: {finding.title}" )
        lines.append( f"    {finding.explanation}" )
        lines.append( f"    Fix: {finding.suggestion}" )

    failed = [ section for section in report.sections if section.error ]
    for section in failed:
        lines.append( f"\n! {section.aspect} reviewer failed: {section.error}" )

    return "\n".join( lines )