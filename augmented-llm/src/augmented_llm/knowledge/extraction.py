# General imports
from pathlib import Path
# PDF reader library
from pypdf import PdfReader

def extract_text( pdf_path: Path ) -> str:
    """
    Return the raw extracted text of a single PDF, with pages joined
    by a blank line so page boundaries read like paragraph breaks.
    """
    reader = PdfReader( pdf_path )
    pages = [ page.extract_text() for page in reader.pages ]

    """
    Joining pages with "\n\n" is a deliberate choice tied to the chunking.
    it makes page boundaries look like paragraph breaks to whatever splits on blank lines next, 
    which is a reasonable proxy since a new page is at least often a topic shift
    """
    return "\n\n".join( pages )