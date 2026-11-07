
# pickle is Python's built-in serialization module for turning objects into
# byte streams and back again; it is unsafe to deserialize untrusted data.
import pickle

# This loads a Python session from pickled bytes using unsafe deserialization.
def load_session( cookie_bytes ):
    return pickle.loads( cookie_bytes )