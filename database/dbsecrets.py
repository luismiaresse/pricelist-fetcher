
class DBCreds:
    """
    DATABASE LOGIN CREDENTIALS
    """
    # Complete URL to the database: easiest way to connect
    URL = None
    # You can leave the rest empty if you want to use a URL.
    MANAGER = None      # Database manager: At the moment only PostgreSQL is supported
    HOST = None         # Host server
    PORT: int = 5432    # Port number
    DATABASE = None     # Database name
    USER = None         # Username
    PASSWORD = None     # Password
    SCHEMA = None       # Schema name
