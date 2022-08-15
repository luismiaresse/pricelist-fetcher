import os.path as path
import logging
import warnings
import database.dbsecrets as creds

import psycopg          # PostgreSQL driver
import classes
import pandas as pd

TIMEZONE = 'utc'
DBSECRETS_PATH = "database/dbsecrets.py"     # To check if exists


# TODO Check if product already exists by URL in database and now() - last_update < interval
#  to avoid fetching the same page too many times
def preprocess(data: classes.Data):
    pass


def postprocess(data: classes.Data):
    if path.exists(DBSECRETS_PATH):
        dbcreds = creds.DBCreds()
        if dbcreds.URL is not None:
            data.prod.pid = get_prod_pid(data)
            insert_product(data)
            (lowprc, interval) = get_lowest_price(data)
            print(f"The lowest recorded price for this item was {lowprc.currency} {lowprc.price}"
                  f" from {interval.start.date} at {interval.start.time} to {interval.end.date} at {interval.end.time}.")
        else:
            logging.info("""No database credentials found. Skipping lowest recorded price...
            If you want to use this feature, please add your database to database/dbsecrets.py,
            or use release binary.""")


def get_prod_pid(data: classes.Data):
    with psycopg.connect(creds.DBCreds().URL) as con:
        # Open a cursor to perform database operations
        with con.cursor() as cur:
            con.autocommit = False

            # Set timezone
            cur.execute(f"SET TIME ZONE '{TIMEZONE}'")

            # Get PID of product
            query = f"""
                SELECT "pid"
                FROM "products"
                WHERE "short_url" = '{data.dom.short_url}' OR "prod_name" = '{data.prod.name}' AND "dom_name" = '{data.dom.name}' AND "dom_tld" = '{data.dom.tld}'
                AND "color" = '{data.prod.color}' AND "size" = '{data.prod.size}'
                """

            warnings.simplefilter("ignore")
            dictio = pd.read_sql_query(query, con)      # TODO Use SQLAlchemy 2.0 to avoid warning (not possible at the moment)

            # If no PID is found
            if dictio.empty:
                logging.debug("Product not found in database")
                insert = f"""
                    INSERT INTO "products" ("prod_name", "dom_name", "dom_tld", "short_url", "brand", "category", "color")
                    VALUES ('{data.prod.name}', '{data.dom.name}', '{data.dom.tld}', '{data.dom.short_url}', '{data.prod.brand}',
                     '{data.prod.category}', '{data.prod.color}')
                    RETURNING "pid"
                    """
                cur.execute(insert)
                pid = cur.fetchone()[0]
                con.commit()
                return pid
            return dictio["pid"][0]


# TODO Prevent too many requests by updating date/time by an interval
#  If price is unchanged and now() - last_update < interval, do not update date/time
#  Otherwise, update date/time. Also store first update (to make graphs)
def insert_product(data: classes.Data):
    with psycopg.connect(creds.DBCreds().URL, options=f"-c search_path={creds.DBCreds().SCHEMA}") as con:
        # Open a cursor to perform database operations
        with con.cursor() as cur:
            con.autocommit = False

            # Set timezone
            cur.execute(f"SET TIME ZONE '{TIMEZONE}'")

            # Escape quotes in strings
            data.prod.name = data.prod.name.replace("'", "''")
            data.prod.brand = data.prod.brand.replace("'", "''")

            # Get latest price
            query = f"""
                SELECT "price", "end_date", "end_time" 
                FROM "histories"
                WHERE "pid" = {data.prod.pid} AND "currency" = '{data.prc.currency}'
                ORDER BY "end_date" DESC, "end_time" DESC
                """

            warnings.simplefilter("ignore")
            dictio = pd.read_sql_query(query, con)      # TODO Use SQLAlchemy 2.0 to avoid warning (not possible at the moment)

            # If latest price is unchanged update end date/time and return
            if not dictio.empty and dictio["price"][0] == data.prc.price:
                timestamp = classes.Timestamp(dictio["end_date"][0], dictio["end_time"][0])
                try:
                    cur.execute(f"""
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
                    cur.execute(f"""
                        INSERT INTO histories ("pid", "price", "start_date", "start_time", "end_date", "end_time", "currency", "shipping")
                         VALUES ('{data.prod.pid}', '{data.prc.price}', CURRENT_DATE, CURRENT_TIME, CURRENT_DATE, CURRENT_TIME,
                          '{data.prc.currency}', '{data.prc.shipping}')
                        """)
                except Exception as e:
                    logging.error(f"Could not insert history into DB: {e}")
                    con.cancel()
                    return
            con.commit()
            logging.debug("Succesfully updated DB with latest price")


def get_lowest_price(data: classes.Data):
    with psycopg.connect(creds.DBCreds().URL) as con:
        # Open a cursor to perform database operations
        with con.cursor() as cur:
            # Set timezone
            cur.execute(f"SET TIME ZONE '{TIMEZONE}'")

            # Get lowest price of product
            query = f"""
                SELECT "start_date", "start_time", "end_date", "end_time", "price", "currency"
                FROM "histories"
                WHERE "pid" = '{data.prod.pid}' AND "currency" = '{data.prc.currency}'
                ORDER BY "price"
                """

            warnings.simplefilter("ignore")
            dictio = pd.read_sql_query(query, con)      # TODO Use SQLAlchemy 2.0 to avoid warning (not possible at the moment)

            # If no price history return
            if dictio.empty:
                logging.debug("No price history for this product")
                return

            pricing = classes.Pricing(price=dictio["price"][0], currency=dictio["currency"][0])
            startstamp = classes.Timestamp(dictio["start_date"][0], dictio["start_time"][0])
            endstamp = classes.Timestamp(dictio["end_date"][0], dictio["end_time"][0])
            interval = classes.Interval(startstamp, endstamp)
            return pricing, interval
