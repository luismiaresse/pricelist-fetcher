import warnings
from datetime import datetime
import time
import pytz
from database import BaseOps
from classes import Data


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
        # Insert price history into DB
        db.insert_product(data)
        (lowprc, interval) = db.get_lowest_price(data)
        # Show times according to local timezone
        localfmt = "%Y-%m-%d at %H:%M:%S"
        localtz = pytz.timezone(db.LOCAL_TIMEZONE)
        start = datetime.fromisoformat(interval.start.isoformat()).replace(tzinfo=pytz.utc).astimezone(
            localtz).strftime(localfmt)
        end = datetime.fromisoformat(interval.end.isoformat()).replace(tzinfo=pytz.utc).astimezone(localtz).strftime(
            localfmt)

        if data.prc.price == lowprc.price:
            print(
                f"This is the lowest recorded price for this item. It was first seen {f'since {start}' if start != end else 'now'}.")
        elif start != end:
            print(f"The lowest recorded price for this item was {lowprc.currency} {lowprc.price}"
                  f" from {start} to {end}.")
