# Regex module
import re
# Models
from ..models import DocumentChunk

# _ denotes that it is a private variable, not to be used outside of this module
_WHITESPACE_RE = re.compile( r"\s+" )
_SENTENCE_SPLIT_RE = re.compile( r"(?<=[.!?])\s+" )

def _make_chunk(
    sentences: list[ str ],
    source: str,
    chunk_index: int,
) -> DocumentChunk:
    """
    Create a DocumentChunk object from a list of sentences, the source, and the chunk index.
    """
    return DocumentChunk(
        source = source,
        chunk_index = chunk_index,
        text = " ".join( sentences ),
    )

def chunk_text( 
        text: str,
        source: str,
        target_size: int = 700,
    ) -> list[ DocumentChunk ]:
    """
    Split raw text into DocumentChunk objects.

    The text is first collapsed to one continuous string (since PDF
    extraction often leaves word-wrap newlines with no real paragraph
    structure), split into sentences, then sentences are greedily packed
    into chunks up to `target_size` characters — so each chunk stays
    sentence-complete instead of being sliced mid-sentence.
    """
    normalized = _WHITESPACE_RE.sub( " ", text ).strip()
    sentences = _SENTENCE_SPLIT_RE.split( normalized )

    chunks: list[ DocumentChunk ] = []
    # Aggregate sentences into chunks until the target size is reached
    current_sentences: list[ str ] = []
    current_length: int = 0

    for sentence in sentences:
        # Strip whitespace and skip empty sentences
        sentence = sentence.strip()
        if not sentence:
            continue

        # Create chunks once current_length exceeds target_size
        if current_length + len( sentence ) > target_size and current_sentences:
            chunks.append( _make_chunk( current_sentences, source, len( chunks ) ) )
            current_sentences = []
            current_length = 0

        current_sentences.append( sentence )
        current_length += len( sentence ) + 1 # +1 reserves space for the space character that'll glue sentences together later

    if current_sentences:
        chunks.append( _make_chunk( current_sentences, source, len( chunks ) ) )

    return chunks