from pathlib import Path
# Knowledge
from .knowledge.extraction import extract_text
from .knowledge.chunking import chunk_text
from .knowledge.embeddings import embed_chunks
# Agents
from .agent.tools import calculator, make_search_tool
from .agent.loop import run_turn

def build_index( pdf_path: Path ):
    text = extract_text( pdf_path )
    chunks = chunk_text( text, source = pdf_path.name )
    return embed_chunks( chunks )

def main():
    indexed_chunks = build_index( Path( "data/prompt engineering.pdf" ) )

    tools_implementation = {
        "calculator": calculator,
        "search_documents": make_search_tool( indexed_chunks )
    }

    messages = []

    test_queries = [
        "What is few-shot prompting? Search the documents to answer.", # retrieval only
        "What's 234 * 18?", # calculator only
        "Search the document for a specific number it mentions, then multiply that number by 3.", # both together
        "Going back to my first question — can you give one more example of when you'd use that technique?", # memory
    ]

    for query in test_queries:
        print( f"\nUser: { query }" )

        messages.append( { "role": "user", "content": query } )
        answer = run_turn( messages, tools_implementation )

        print( f"Claude: { answer }" )

if __name__ == "__main__":
    main()