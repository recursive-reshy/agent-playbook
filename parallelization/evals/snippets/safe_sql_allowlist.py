SORT_TABLE = { "name", "created_at", "email" }

def list_users( db, sort_by ):
    if sort_by not in SORT_TABLE:
        raise ValueError( "bad sort column" )
    return db.execute( f"SELECT * FROM users ORDER_BY {sort_by}" )