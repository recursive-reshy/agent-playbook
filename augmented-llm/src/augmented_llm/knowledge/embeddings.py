# Embedding library
import voyageai
# Config
from ..config import settings
# Models
from ..models import DocumentChunk, EmbeddedChunk

_client = voyageai.Client( api_key = settings.VOYAGE_API_KEY )

def embed_chunks( chunks: list[ DocumentChunk ] ) -> list[ EmbeddedChunk ]:
    texts = [ chunk.text for chunk in chunks ]

    result = _client.embed(
        texts,
        model = settings.VOYAGE_MODEL,
        input_type = "document"
    )

    return [
        EmbeddedChunk(
            source = chunk.source,
            chunk_index = chunk.chunk_index,
            text = chunk.text,
            embedding = vector
        )
        for chunk, vector in zip( chunks, result.embeddings )
    ]

def embed_query( query: str ) -> list[ float ]:
    """Embed a single query string for comparison against indexed document chunks."""
    result = _client.embed(
        [ query ],
        model = settings.VOYAGE_MODEL,
        input_type = "query"
    )

    return result.embeddings[ 0 ]