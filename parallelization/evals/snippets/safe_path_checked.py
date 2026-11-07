from pathlib import Path

UPLOADS = Path( "/srv/uploads" ).resolve()

def read_upload( filename ):
    target = ( UPLOADS/ filename ).resolve()

    if not target.is_relative_to( UPLOADS ):
        raise PermissionError( "outside uploads directory" )
    
    return target.read_bytes()