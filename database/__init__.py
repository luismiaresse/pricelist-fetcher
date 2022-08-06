import os.path as path
import logging
import warnings
import database.dbsecrets as creds

import psycopg          # PostgreSQL driver
import classes
import pandas as pd

TIMEZONE = 'utc'
DBSECRETS_PATH = "database/dbsecrets.py"     # To check if exists


# TODO Check if product already exists in database and now() - last_update < interval
#  to avoid fetching the same page too many times
def preprocess(data: classes.Data):
    pass


def postprocess(data: classes.Data):
    if path.exists(DBSECRETS_PATH):
        dbcreds = creds.DBCreds()
        if dbcreds.URL is not None:
            insert_product(data)
            (lowprc, interval) = get_lowest_price(data)
            print(f"The lowest recorded price for this item was {lowprc.currency} {lowprc.price}"
                  f" from {interval.start.date} at {interval.start.time} to {interval.end.date} at {interval.end.time}.")
        else:
            logging.info("""No database credentials found. Skipping lowest recorded price...
            If you want to use this feature, please add your database to database/dbsecrets.py,
            or use release binary.""")


# TODO Prevent too many requests by updating date/time by an interval
#  If price is unchanged and now() - last_update < interval, do not update date/time
#  Otherwise, update date/time. Also store first update (to make graphs)
def insert_product(data: classes.Data):
    with psycopg.connect(creds.DBCreds().URL, options=f"-c search_path={creds.DBCreds().SCHEMA}") as con:
        # Open a cursor to perform database operations
        with con.cursor() as cur:
            con.autocommit = False

            # Set timezone
            con.execute(f"SET TIME ZONE '{TIMEZONE}'")

            # Escape quotes in strings
            data.prod.name = data.prod.name.replace("'", "''")
            data.prod.brand = data.prod.brand.replace("'", "''")

            # Get latest price
            query = f"""
                SELECT "prod_name", "price", "end_date", "end_time" 
                FROM "product_history"
                WHERE "prod_name" = '{data.prod.name}' AND "dom_name" = '{data.dom.name}' AND "dom_tld" = '{data.dom.tld}'
                 AND "currency" = '{data.prc.currency}'
                ORDER BY "end_date" DESC, "end_time" DESC
                """

            warnings.simplefilter("ignore")
            dictio = pd.read_sql_query(query, con)      # TODO Use SQLAlchemy 2.0 to avoid warning (not possible at the moment)

            # If latest price is unchanged update end date/time and return
            if not dictio.empty and dictio["price"][0] == data.prc.price:
                timestamp = classes.Timestamp(dictio["end_date"][0], dictio["end_time"][0])
                try:
                    cur.execute(f"""
                        UPDATE "product_history" SET "end_date" = CURRENT_DATE, "end_time" = CURRENT_TIME
                        WHERE "prod_name" = '{data.prod.name}' AND "dom_name" = '{data.dom.name}' AND "dom_tld" = '{data.dom.tld}'
                         AND "currency" = '{data.prc.currency}' AND "price" = '{data.prc.price}' AND "end_date" = '{timestamp.date}'
                         AND "end_time" = '{timestamp.time}'
                        """)
                except Exception as e:
                    logging.debug(f"Could not update end date/time in DB: {e}")
                logging.debug("Price is unchanged")
                return
            elif dictio.empty:
                # Insert if new domain
                try:
                    cur.execute("SAVEPOINT sp1")
                    cur.execute(f"""
                        INSERT INTO domains VALUES ('{data.dom.name}', '{data.dom.tld}')
                        """)
                except Exception as e:
                    logging.debug(f"Could not insert domain {data.dom.name} into DB: {e}")
                    con.execute("ROLLBACK TO SAVEPOINT sp1")

                # Insert if new product
                try:
                    cur.execute("SAVEPOINT sp2")
                    cur.execute(f"""
                        INSERT INTO products VALUES ('{data.prod.name}', '{data.prod.brand}', '{data.prod.category}')
                        """)
                except Exception as e:
                    logging.debug(f"Could not insert product {data.prod.name} into DB: {e}")
                    con.execute("ROLLBACK TO SAVEPOINT sp2")

                # Insert into history. Date/Time for start and end is the same the first time a new price or product is detected
                # Any subsequent checks with same price will update end date/time only
                try:
                    cur.execute(f"""
                        INSERT INTO product_history VALUES ('{data.prod.name}', '{data.prc.price}', '{data.prc.currency}',
                        '{data.dom.name}', '{data.dom.tld}', CURRENT_DATE, CURRENT_TIME, CURRENT_DATE, CURRENT_TIME, '{data.prc.shipping}')
                        """)
                except Exception as e:
                    logging.error(f"Could not insert history into DB: {e}")
                    con.cancel()
                    return
            else:
                try:
                    cur.execute(f"""
                        INSERT INTO product_history VALUES ('{data.prod.name}', '{data.prc.price}', '{data.prc.currency}',
                        '{data.dom.name}', '{data.dom.tld}', CURRENT_DATE, CURRENT_TIME, CURRENT_DATE, CURRENT_TIME, '{data.prc.shipping}')
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
            con.execute(f"SET TIME ZONE '{TIMEZONE}'")

            # Get lowest price of classes
            query = f"""
                SELECT "start_date", "start_time", "end_date", "end_time", "price", "currency"
                FROM "product_history"
                WHERE "prod_name" = '{data.prod.name}' AND "dom_name" = '{data.dom.name}' AND "dom_tld" = '{data.dom.tld}'
                 AND "currency" = '{data.prc.currency}'
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

