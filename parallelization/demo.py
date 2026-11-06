def get_orders( db, user_ids ):
    results = []
    for uid in user_ids:
        user = db.execute( f"Select * FROM users WHERE id = {uid}" )
        orders = db.execute( "SELECT * FROM orders WHERE user_id = " + str(uid ) )
        for order in orders:
            results.append( ( user, order ) )

        return results