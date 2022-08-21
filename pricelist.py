import argparse
import logging
import fetch
import database as db


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="show debug messages", action="store_true")
    parser.add_argument("-vv", "--very-verbose", help="show A LOT more debug messages", action="store_true")
    # parser.add_argument("-d", "--domain", help="specify a domain to debug by using its test URL", type=str)
    parser.add_argument("url", help="full URL of the site you want to get info from. Example: https://www.foo.bar",
                        type=str)
    parser.add_argument("--no-db", help="skip database use to store and fetch prices", action="store_true")
    return parser.parse_args()


def set_logger(log_level):
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
    logger.setLevel(log_level)


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
    if not opts[Options.NO_DB]:
        db.preprocess()
    if opts[Options.V] or opts[Options.VV]:
        set_logger(logging.DEBUG)
    else:
        set_logger(logging.INFO)
    data = fetch.fetch_data(url=args.url, opts=opts)
    print(data)
    if not opts[Options.NO_DB]:
        db.postprocess(data)
    set_logger(logging.ERROR)  # Hides warnings after quitting chromedriver
    exit(0)


if __name__ == '__main__':
    main()
