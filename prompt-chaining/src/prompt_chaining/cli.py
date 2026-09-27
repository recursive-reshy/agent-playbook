import argparse
import logging
import sys
from pathlib import Path

from prompt_chaining.chain import GateFailedError, run_chain

def main() -> None:
    parser = argparse.ArgumentParser(
        description = "Generate a blog post using a prompt chain."
    )

    parser.add_argument( "topic", help = "What the blog post should be about" )
    parser.add_argument( "-o", "--output", type = Path, help = "Save the post to a file" )
    args = parser.parse_args()

    logging.basicConfig( level = logging.INFO, format = "%(message)s" )

    try:
        post = run_chain( args.topic )
    except GateFailedError as error:
        logging.error( error )
        sys.exit( 1 )

    if args.output:
        args.output.write_text( post.final, encoding = "utf-8" )
        logging.info( "Saved to %s", args.output )
    else:
        print( post.final )