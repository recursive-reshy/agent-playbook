import ast
import operator
# Knowledge
from ..knowledge.retrieval import search
# Models
from ..models import EmbeddedChunk

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}

TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression, e.g. '12 * (3 + 4)'.",
        "input_schema": {
            "type": "object",
            "properties": { "expression": { "type": "string" } },
            "required": [ "expression" ]
        }
    },
    {
        "name": "search_documents",
        "description": "Search your indexed documents for passages relevant to a question or topic.",
        "input_schema": {
            "type": "object",
            "properties": { "query": { "type": "string" } },
            "required": [ "query" ]
        }
    }
]

def _eval_node( node: ast.AST ):
    if isinstance( node, ast.Constant ) and isinstance( node.value, ( int, float ) ):
        return node.value
    if isinstance( node, ast.gOp ) and type( node.op ) in _OPERATORS:
        return _OPERATORS[ type( node.op ) ]( _eval_node( node.left ), _eval_node( node.right ) )
    if isinstance( node, ast.UnaryOp ) and type( node.op ) in _OPERATORS:
        return _OPERATORS[ type( node.op ) ]( _eval_node( node.operand ) )
    raise ValueError( f"Unsupported expression: { ast.dump( node ) }" )

def calculator( expression: str ) -> str:
    """Safely evaluate a basic arithmetic expression and return the result as a string."""
    try:
        tree = ast.parse( expression, mode = "eval" )
        result = _eval_node( tree.body )
        return str( result )
    except Exception as exc:
        return f"Error: { exc }"

def make_search_tool( indexed_chunks: list[ EmbeddedChunk ] ):
    """Create a tool-facing search function with the document index baked in.

    This exists because the tool schema only exposes `query` to the model —
    it never sees `indexed_chunks`. A closure lets us pre-load the index
    into the returned function ahead of time, so by the time the agent
    loop calls it with just a query string, everything else it needs is
    already available.

    Args:
        indexed_chunks: The pre-embedded document chunks to search over.

    Returns:
        A `search_documents(query: str) -> str` function, ready to be
        registered in the tool dispatch table and called with only a query.
    """

    def search_documents( query: str ) -> str:
        """Search the baked-in index and return the top matches, formatted
        as readable text for the model to read as a tool result."""
        results = search( query, indexed_chunks, top_k = 3 )

        return "\n\n".join(
            f"[ {chunk.source}, chunk {chunk.chunk_index}, relevance = {score:.2f} ]"
            for chunk, score in results
        )

    return search_documents
