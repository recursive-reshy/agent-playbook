from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, computed_field, model_validator

class Aspect( StrEnum ):
    SECURITY = "security"
    PERFORMANCE = "performance"
    ReLIABILITY = "reliability"

class Severity( StrEnum ):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def rank( self ) -> int:
        return list( Severity ).index( self )

class Finding( BaseModel ):
    severity: Severity = Field( descriptio = "How serious the issue is." )
    line: int | None = Field(
        default = None,
        ge = 1,
        description = "The line number the issue is on, or null if it applies to the whole snippet."
    )
    title: str = Field( description = "A short name for the issue, under 10 words." )
    explanation: str = Field( description = "What the problem is and why it matters." )
    suggestion: str = Field( description = "A concrete fix" )

class SectionFindings( BaseModel ):
    summary: str = Field( description = "One or two sentences on the code from this reviewer's angle." )
    findings: list[ Finding ] = Field(
        default_factory = list,
        description = "Issues found. An empty list if there are none."
    )

class SecurityVote( BaseModel ):
    reasoning: str = Field(
        description = "Trace how the code handles untrusted input before deciding."
    )
    vulnerable: bool = Field(
        description = "True only if the code contains an exploitable security vulnerability."
    )
    confidence: float = Field(
        ge = 0,
        le = 1,
        description = "How sure you are, from 0 to 1."
    )

class SectionReview( BaseModel ):
    aspect: Aspect
    seconds: float
    output: SectionFindings | None = None
    error: str | None = None

    @model_validator( mode = "after" )
    def exactly_one_result( self ) -> "SectionReview":
        if ( self.output is None ) == ( self.error is None ):
            raise ValueError( "SectionReview needs exactly one of output or error" )
        return self


class VoteResult( BaseModel ):
    votes: list[ SecurityVote ]
    failed: int = 0
    threshold: int

    @computed_field
    @property
    def vulnerable_votes( self ) -> int:
        return sum( vote.vulnerable for vote in self.votes )

    @computed_field
    @property
    def flagged( self ) -> bool:
        return self.vulnerable_votes >= self.threshold


class ReportFinding( Finding ):
    aspect: Aspect


class ReviewReport( BaseModel ):
    source: str
    mode: Literal[ "parallel", "sequential" ]
    seconds: float
    findings: list[ ReportFinding ]
    sections: list[ SectionReview ]
    vote: VoteResult