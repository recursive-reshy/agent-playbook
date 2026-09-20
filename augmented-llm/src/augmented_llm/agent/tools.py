import ast
import operator

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}

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