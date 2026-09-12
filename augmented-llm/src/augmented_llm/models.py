from pydantic import BaseModel

class DocumentChunk( BaseModel ):
    source: str
    chunk_index: int
    text: str

class EmbeddedChunk( DocumentChunk ):
    embedding: list[ float ]