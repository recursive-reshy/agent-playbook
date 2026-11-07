import subprocess

ALLOWED = { "status", "log", "diff" }

def git( subcommand ):
    if subcommand not in ALLOWED:
        raise ValueError( "unsupported subcommand" )

    return subprocess.run( [ "git", subcommand ], capture_output = True, text = True )