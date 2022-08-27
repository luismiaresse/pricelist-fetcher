
import logging
import warnings
import pandas as pd
import psycopg  # PostgreSQL driver
import database.dbsecrets as creds
from classes import Data, Interval, Timestamp, Pricing


class BaseOps:
    """
    Contains basic database operations
    """
    DB_TIMEZONE = 'utc'
    LOCAL_TIMEZONE = None  # To convert UTC to local time

    def __init__(self):
        """
        Initialize database connection and cursor.
        """
        self.url = creds.DBCreds().URL

        if self.url is None:
            logging.info("""No database credentials found. Database features such as lowest price or prefetching will not be available.
            If you want to use these features, please add your database to database/dbsecrets.py, or use release binary;
            otherwise consider using --no-db option.""")
            return

        self.con = psycopg.connect(self.url)
        self.con.autocommit = False
        self.cur = self.con.cursor()
        # Set timezone
        self.cur.execute(f"SET TIME ZONE '{self.DB_TIMEZONE}'")
        logging.info("Database successfully connected")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.url is not None:
            self.cur.close()
            self.con.close()

    def get_prod_pid(self, data: Data):
        # Get PID of product
        query = f"""
            SELECT "pid"
            FROM "products"
            WHERE "short_url" = '{data.dom.short_url}' OR "prod_name" = '{data.prod.name}' AND "dom_name" = '{data.dom.name.name}' AND "dom_tld" = '{data.dom.tld.name}'
            AND "color" = '{data.prod.color}' AND "size" = '{data.prod.size}'
            """

        warnings.simplefilter("ignore")
        dictio = pd.read_sql_query(query, self.con)      # TODO Use SQLAlchemy 2.0 to avoid warning (not possible at the moment)

        # If no PID is found
        if dictio.empty:
            logging.debug("Product not found in database")
            insert = f"""
                INSERT INTO "products" ("prod_name", "dom_name", "dom_tld", "short_url", "brand", "category", "color")
                VALUES ('{data.prod.name}', '{data.dom.name.name}', '{data.dom.tld.name}', '{data.dom.short_url}', '{data.prod.brand}',
                 '{data.prod.category}', '{data.prod.color}')
                RETURNING "pid"
                """
            self.cur.execute(insert)
            pid = self.cur.fetchone()[0]
            self.con.commit()
            return pid
        return dictio["pid"][0]

    def insert_product(self, data: Data):
        # Get latest price
        query = f"""
            SELECT "price", "end_date", "end_time" 
            FROM "histories"
            WHERE "pid" = {data.prod.pid} AND "currency" = '{data.prc.currency}'
            ORDER BY "end_date" DESC, "end_time" DESC
            """

        warnings.simplefilter("ignore")
        dictio = pd.read_sql_query(query, self.con)      # TODO Use SQLAlchemy 2.0 to avoid warning (not possible at the moment)

        # If latest price is unchanged update end date/time and return
        if not dictio.empty and dictio["price"][0] == data.prc.price:
            timestamp = Timestamp(dictio["end_date"][0], dictio["end_time"][0])
            try:
                self.cur.execute(f"""
                    UPDATE "histories" SET "end_date" = CURRENT_DATE, "end_time" = CURRENT_TIME
                    WHERE "pid" = '{data.prod.pid}' 
                     AND "currency" = '{data.prc.currency}' AND "price" = '{data.prc.price}' AND "end_date" = '{timestamp.date}'
                     AND "end_time" = '{timestamp.time}'
                    """)
            except Exception as e:
                logging.debug(f"Could not update end date/time in DB: {e}")
            logging.debug("Price is unchanged")
            return
        else:
            # Insert into history. Date/Time for start and end is the same the first time a new price is detected
            # Any subsequent checks with same price will update end date/time only
            try:
                self.cur.execute(f"""
                    INSERT INTO histories ("pid", "price", "start_date", "start_time", "end_date", "end_time", "currency", "shipping")
                     VALUES ('{data.prod.pid}', '{data.prc.price}', CURRENT_DATE, CURRENT_TIME, CURRENT_DATE, CURRENT_TIME,
                      '{data.prc.currency}', '{data.prc.shipping}')
                    """)
            except Exception as e:
                logging.error(f"Could not insert history into DB: {e}")
                self.con.cancel()
                return
        self.con.commit()
        logging.debug("Succesfully updated DB with latest price")

    def get_lowest_price(self, data: Data):
        # Get lowest price of product
        query = f"""
            SELECT "start_date", "start_time", "end_date", "end_time", "price", "currency"
            FROM "histories"
            WHERE "pid" = '{data.prod.pid}' AND "currency" = '{data.prc.currency}'
            ORDER BY "price"
            """

        warnings.simplefilter("ignore")
        dictio = pd.read_sql_query(query, self.con)      # TODO Use SQLAlchemy 2.0 to avoid warning (not possible at the moment)

        # If no price history
        if dictio.empty:
            logging.error("No price history for this product")
            exit(1)

        pricing = Pricing(price=dictio["price"][0], currency=dictio["currency"][0])
        startstamp = Timestamp(dictio["start_date"][0], dictio["start_time"][0])
        endstamp = Timestamp(dictio["end_date"][0], dictio["end_time"][0])
        interval = Interval(startstamp, endstamp)
        return pricing, interval

    # TODO Update newly supported and some existing data
    def update_product(self, data: Data):
        pass
