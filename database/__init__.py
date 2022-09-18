import warnings
from datetime import datetime
import time

from price_parser import Price
import pytz
import logging
import pandas as pd
import psycopg  # PostgreSQL driver
import database.dbsecrets as creds
from common.classes import Data, Interval, Timestamp, Pricing, Product


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
            If you want to use these features, please add your database following database/dbsecrets.py instructions,
            or use release binary; otherwise consider using --no-db option.""")
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

        dictio = pd.read_sql_query(query, self.con)

        # If no PID is found
        if dictio.empty:
            logging.debug("Product not found in database. Inserting as new product")
            insert = f"""
                INSERT INTO "products" ("prod_name", "dom_name", "dom_tld", "short_url", "brand", "category", "color", "size")
                VALUES ('{data.prod.name}', '{data.dom.name.name}', '{data.dom.tld.name}', '{data.dom.short_url}', '{data.prod.brand}',
                 '{data.prod.category}', '{data.prod.color}', '{data.prod.size}')
                RETURNING "pid"
                """
            self.cur.execute(insert)
            pid = self.cur.fetchone()[0]
            self.con.commit()
            return pid
        return dictio["pid"][0]

    def insert_history(self, data: Data):
        # Get latest price
        query = f"""
            SELECT "price", "end_date", "end_time" 
            FROM "histories"
            WHERE "pid" = {data.prod.pid} AND "currency" = '{data.prc.price.currency}'
            ORDER BY "end_date" DESC, "end_time" DESC
            """

        dictio = pd.read_sql_query(query, self.con)

        if not dictio.empty and dictio["price"][0] == data.prc.price.amount_float:
            # If latest price is unchanged update end date/time
            logging.debug("Updating end date/time")
            timestamp = Timestamp(dictio["end_date"][0], dictio["end_time"][0])
            try:
                self.cur.execute(f"""
                    UPDATE "histories" SET "end_date" = CURRENT_DATE, "end_time" = CURRENT_TIME
                    WHERE "pid" = '{data.prod.pid}' 
                     AND "currency" = '{data.prc.price.currency}' AND "price" = '{str(data.prc.price.amount_float)}' AND "end_date" = '{timestamp.date}'
                     AND "end_time" = '{timestamp.time}';
                    """)
            except Exception as e:
                logging.debug(f"Could not update end date/time in DB: {e}")
                self.con.rollback()
                return
        else:
            # Insert into history. Date/Time for start and end is the same the first time a new price is detected
            # Any subsequent checks with same price will update end date/time only
            logging.debug("Inserting new price")
            try:
                self.cur.execute(f"""
                    INSERT INTO "histories" ("pid", "price", "start_date", "start_time", "end_date", "end_time", "currency", "shipping")
                     VALUES ('{data.prod.pid}', '{data.prc.price.amount_float}', CURRENT_DATE, CURRENT_TIME, CURRENT_DATE, CURRENT_TIME,
                      '{data.prc.price.currency}', '{data.prc.shipping.amount_float}')
                    """)
            except Exception as e:
                logging.error(f"Could not insert history into DB: {e}")
                self.con.rollback()
                return
        self.con.commit()
        logging.debug("History successfully updated")

    def get_lowest_price(self, data: Data):
        # Get lowest price of product
        query = f"""
            SELECT "start_date", "start_time", "end_date", "end_time", "price", "currency"
            FROM "histories"
            WHERE "pid" = '{data.prod.pid}' AND "currency" = '{data.prc.price.currency}'
            ORDER BY "price"
            """

        dictio = pd.read_sql_query(query, self.con)

        # If no price history
        if dictio.empty:
            logging.error("No price history for this product")
            exit(1)
        price = Price(amount=dictio["price"][0], currency=dictio["currency"][0], amount_text=None)
        pricing = Pricing(price=price)
        startstamp = Timestamp(dictio["start_date"][0], dictio["start_time"][0])
        endstamp = Timestamp(dictio["end_date"][0], dictio["end_time"][0])
        interval = Interval(startstamp, endstamp)
        return pricing, interval

    def get_product_by_pid(self, pid: int):
        # Get product by PID
        query = f"""
            SELECT "pid", "prod_name", "brand", "category", "color", "size"
            FROM "products"
            WHERE "pid" = '{pid}'
            """

        dictio = pd.read_sql_query(query, self.con)

        # If no product is found
        if dictio.empty:
            return None
        return Product(pid=dictio["pid"][0], name=dictio["prod_name"][0], brand=dictio["brand"][0],
                       category=dictio["category"][0], color=dictio["color"][0], size=dictio["size"][0])

    # TODO Update newly supported and some existing data
    def update_product(self, data: Data):
        dbprod = self.get_product_by_pid(data.prod.pid)
        if dbprod == data.prod:
            logging.debug("Product == DB Product")
            return
        elif dbprod is None:
            logging.debug("Product not found in database")
            return
        else:
            # Update product optional fields
            query = f"""
                    UPDATE "products" SET "brand" = '{data.prod.brand}', "category" = '{data.prod.category}'
                    WHERE "pid" = '{data.prod.pid}'
                    """
            try:
                self.cur.execute(query)
                self.con.commit()
            except Exception as e:
                logging.error(f"Could not update product in DB: {e}")
                self.con.rollback()
                return


# TODO Check if product already exists by URL in database and now() - last_update < interval
# to avoid fetching the same page too many times
def preprocess(db: BaseOps):
    if db.url is not None:
        db.LOCAL_TIMEZONE = time.tzname[0]
    warnings.simplefilter("ignore")   # TODO Use SQLAlchemy 2.0 in pandas to avoid warning (not possible at the moment)


def postprocess(db: BaseOps, data: Data):
    if db.url is not None:
        # Escape quotes in strings
        data.prod.name = data.prod.name.replace("'", "''")
        data.prod.brand = data.prod.brand.replace("'", "''")
        # Get PID from DB
        data.prod.pid = db.get_prod_pid(data)
        # Update if optional fields are different
        db.update_product(data)
        # Insert price history into DB
        db.insert_history(data)
        (lowprc, interval) = db.get_lowest_price(data)
        # Show times according to local timezone
        localfmt = "%Y-%m-%d at %H:%M:%S"
        localtz = pytz.timezone(db.LOCAL_TIMEZONE)
        start = datetime.fromisoformat(interval.start.isoformat()).replace(tzinfo=pytz.utc).astimezone(
            localtz).strftime(localfmt)
        end = datetime.fromisoformat(interval.end.isoformat()).replace(tzinfo=pytz.utc).astimezone(localtz).strftime(
            localfmt)

        if data.prc.price.amount_float == lowprc.price.amount_float:
            print(
                f"This is the lowest recorded price for this item. It was first seen {f'since {start}' if start != end else 'now'}.")
        elif start != end:
            print(f"The lowest recorded price for this item was {lowprc.price.currency} {lowprc.price.amount}"
                  f" from {start} to {end}.")
        else:
            print(f"The lowest recorded price for this item was {lowprc.price.currency} {lowprc.price.amount}"
                  f" in {start}.")
