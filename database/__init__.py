import logging
import os.path as path
import psycopg          # PostgreSQL driver
import classes
import pandas as pd

DBSECRETS_PATH = "database/dbsecrets.py"
ALT_DBSECRETS_PATH = "database/dbsecrets-dummy.py"

if path.exists(DBSECRETS_PATH):
    import database.dbsecrets


def insert_product(prod: classes.Product, dom: classes.Domain, pricing: classes.Pricing):
    with psycopg.connect(dbsecrets.DBCreds.URL) as con:
        # Open a cursor to perform database operations
        with con.cursor() as cur:
            con.autocommit = False
            # Get latest price of classes
            query = f"""
                    SELECT "prod_name", "price", "day", "hour"
                    FROM "product_history"
                    WHERE "prod_name" = '{prod.name}' AND "dom_name" = '{dom.name}' AND "currency" = '{pricing.currency}'
                    ORDER BY "day" DESC, "hour" DESC
                    """
            dictio = pd.read_sql_query(query, con)      # TODO Use SQLAlchemy 2.0 to avoid warning (not possible at the moment)

            # If latest price is unchanged return
            if not dictio.empty and dictio["price"][0] == pricing.price:
                logging.debug("Price is unchanged. No changes to DB")
                return
            elif dictio.empty:
                # Insert if new domain
                try:
                    cur.execute("SAVEPOINT sp1")
                    cur.execute(f"""
                            INSERT INTO public.domains VALUES ('{dom.name}', '{dom.tld}')
                            """)
                except Exception as e:
                    logging.debug(f"Could not insert domain {dom.name} into DB: {e}")
                    con.execute("ROLLBACK TO SAVEPOINT sp1")

                # Insert if new product
                try:
                    cur.execute("SAVEPOINT sp2")
                    cur.execute(f"""
                            INSERT INTO public.products VALUES ('{prod.name}', '{prod.brand}')
                            """)
                except Exception as e:
                    logging.debug(f"Could not insert product {prod.name} into DB: {e}")
                    con.execute("ROLLBACK TO SAVEPOINT sp2")

                # Insert into history
                try:
                    cur.execute("SAVEPOINT sp3")
                    cur.execute(f"""
                            INSERT INTO public.product_history VALUES ('{prod.name}', '{pricing.price}', '{pricing.currency}',
                            '{dom.name}', '{dom.tld}', CURRENT_DATE, CURRENT_TIME, '{pricing.shipping}')
                            """)
                except Exception as e:
                    logging.error(f"Could not insert history into DB: {e}")
                    con.cancel()
                    return

            con.commit()
            logging.debug("Succesfully updated DB with latest price")


def get_lowest_price(prod: classes.Product, dom: classes.Domain, pricing: classes.Pricing):
    with psycopg.connect(dbsecrets.DBCreds.URL) as con:
        # Open a cursor to perform database operations
        with con.cursor() as cur:
            # Get lowest price of classes
            query = f"""
                    SELECT "prod_name", "day", "hour", "price"
                    FROM "product_history"
                    WHERE "prod_name" = '{prod.name}' AND "dom_name" = '{dom.name}' AND "currency" = '{pricing.currency}'
                    ORDER BY "price" ASC
                    """
            dictio = pd.read_sql_query(query, con)      # TODO Use SQLAlchemy 2.0 to avoid warning (not possible at the moment)

            # If no price history return
            if dictio.empty:
                logging.debug("No price history for this classes")
                return


