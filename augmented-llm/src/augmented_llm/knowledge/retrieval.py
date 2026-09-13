# Numpy
import numpy as np
# Models
from ..models import EmbeddedChunk
#Embedding
from .embeddings import embed_query

# Compute the cosine similarity between two vectors, measuring how aligned
# They are in embedding space regardless of their magnitude.
def cosine_similarity( a: list[ float ], b: list[ float ] ) -> float:
    """
    Return the cosine similarity between two vectors.
    """
    a_arr = np.array( a )
    b_arr = np.array( b )

    return float( np.dot( a_arr, b_arr ) / ( np.linalg.norm( a_arr ) ) * ( np.linalg.norm( b_arr ) ) )

def search(
    query: str, 
    indexed_chunks: list[ EmbeddedChunk ], 
    top_k: int = 3
) -> list[ tuple[ EmbeddedChunk, float ] ]:
    """
    Embed the query, score it against every indexed chunk, and return
    the top_k (chunk, similarity_score) pairs, best match first.
    """
    query_vector = embed_query( query )

    # Score every indexed chunk against the query embedding and keep the best matches.
    scored = [
        ( chunk, cosine_similarity( query_vector, chunk.embedding ) )
        for chunk in indexed_chunks
    ]
    scored.sort( key = lambda pair: pair[ 1 ], reverse = True )

    return scored[ :top_k ]