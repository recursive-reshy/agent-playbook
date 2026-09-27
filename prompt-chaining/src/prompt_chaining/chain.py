import logging

from prompt_chaining.gates import check_outline
from prompt_chaining.models import BlogPost, Outline
from prompt_chaining.steps import generate_outline, polish, write_draft

logger = logging.getLogger( __name__ )

class GateFailedError( Exception ):
    def __init__( self, issues: list[ str ] ):
        self.issues = issues
        super().__init__( "Outline failed the gate: " + "; ".join( issues ) )

def build_outline( topic: str, max_attempts: int = 3 ) -> Outline:
    feedback: list[ str ] | None = None

    for attempt in range( 1, max_attempts + 1 ):
        logger.info( "Step 1: generating outline (attempt %d)", attempt )
        outline = generate_outline( topic, feedback )

        result = check_outline( outline )

        if result.passed:
            logger.info( "Gate passed" )
            return outline

        logger.warning( "Gate failed: %s", "; ".join( result.issues ) )
        feedback = result.issues

    raise GateFailedError( result.issues )

def run_chain( topic: str ) -> BlogPost:
    outline = build_outline( topic )
    
    logger.info( "Step 2: writing draft" )
    draft = write_draft( topic = topic, outline = outline )

    logger.info( "Step 3: polishing" )
    final = polish( draft )

    return BlogPost( topic = topic, outline = outline, draft = draft, final = final )