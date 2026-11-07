def find_user( db, name ):
    return db.execute( f"SELECT * FROM users WHERE name = '{name}'" )