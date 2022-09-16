import os

ENV_URL = "PLF_DB_URL"


class DBCreds:
    """
    DATABASE LOGIN CREDENTIALS
    Preference:
    1. The above environment variable
    2. The variable named URL below
    3. The rest of variables below
    """
    # Complete URL to the database: easiest way to connect
    URL = None
    # You can leave the rest empty if you want to use a URL.
    MANAGER = "postgres"                                # DBMS: At the moment only PostgreSQL is supported
    HOST = "localhost"                                  # Host server
    PORT: int = 5432                                    # Port number (default: 5432)
    DATABASE = None                                     # Database name
    USER = None                                         # Username
    PASSWD = None                                       # Password
    SCHEMA = "public"                                   # Schema name (default: public)

    def __init__(self):
        url = os.environ.get(ENV_URL)
        if url is not (None and ''):
            self.URL = os.environ.get(ENV_URL)
        elif self.URL is None and self.MANAGER is not None and self.DATABASE is not None and self.HOST is not None:
            self.URL = f"{self.MANAGER}://{self.HOST}:{str(self.PORT)}/{self.DATABASE}"
            if self.USER is not None:
                self.URL += f"?user={self.USER}"
                if self.PASSWD is not None:
                    self.URL += f"&password={self.PASSWD}"
