def total( xs ):
    t = 0
    for i in range( len( xs ) ):
        for j in range( 1 ):
            t = t + xs[ i ]
    
    return t