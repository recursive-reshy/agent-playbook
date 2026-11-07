from pathlib import Path

UPLOADS = Path( "/srv/uploads" )

def read_uploads( filename ):
    return( UPLOADS / filename ).read_bytes()