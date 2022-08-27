import argparse
import logging
import fetch
import requests
from database import BaseOps
import database.process as dbp


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="show debug messages", action="store_true")
    parser.add_argument("-vv", "--very-verbose", help="show A LOT more debug messages", action="store_true")
    # parser.add_argument("-d", "--domain", help="specify a domain to debug by using its test URL", type=str)
    parser.add_argument("url", help="full URL of the site you want to get info from. Example: https://www.foo.bar",
                        type=str)
    parser.add_argument("--no-db", help="skip database use to store current price and fetch lowest price", action="store_true")
    return parser.parse_args()


def set_logger(log_level):
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    logger.setLevel(log_level)


def expand_url(url):
    """
    Useful to get full URLs from shortened ones.
    """
    if "https://da.gd" in url:
        pos = url.rfind("/")
        url = url[pos + 1:]
        page = f"https://da.gd/coshorten/{url}"
        url = requests.get(page).content.decode("utf-8").strip()
    return url


class Options:
    """
    Enum with all possible CLI options
    """
    VERBOSE = V = "verbose"
    VERY_VERBOSE = VV = "very_verbose"
    NO_DB = "no_db"


def main():
    args = setup_parser()
    opts = args.__dict__
    if opts[Options.V] or opts[Options.VV]:
        set_logger(logging.DEBUG)
    else:
        set_logger(logging.INFO)

    if not opts[Options.NO_DB]:
        with BaseOps() as db:
            dbp.preprocess(db)
            url = expand_url(args.url)
            data = fetch.fetch_data(url=url, opts=opts)
            print(data)
            dbp.postprocess(db, data)
    else:
        url = expand_url(args.url)
        data = fetch.fetch_data(url=url, opts=opts)
        print(data)
    set_logger(logging.ERROR)  # Hides warnings after quitting chromedriver
    exit(0)


if __name__ == '__main__':
    main()
