
import data
import argparse
import logging
import fetch


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="show debug messages", action="store_true")
    parser.add_argument("-vv", "--veryverbose", help="show A LOT more debug messages", action="store_true")
    parser.add_argument("-d", "--domain", help="specify a domain to debug by using its test URL", type=str)
    parser.add_argument("url", help="Full URL of the site you want to get info from. Example: https://www.foo.bar",
                        type=str)
    return parser.parse_args()


def set_logger(log_level):
    logger = logging.getLogger()
    logger.setLevel(log_level)


class Options:
    """
    Enum with all possible CLI options
    """
    VERBOSE = V = "verbose"
    VERYVERBOSE = VV = "veryverbose"


if __name__ == '__main__':
    args = setup_parser()
    opts = args.__dict__
    if opts[Options.V] or opts[Options.VV]:
        set_logger(logging.DEBUG)
    else:
        set_logger(logging.INFO)
    attrs = fetch.fetch_data(args.url, opts)
    keys = [i.value for i in attrs.keys()]
    values = list(attrs.values())
    dat = {keys[i]: values[i] for i in attrs}
    # data = pd.DataFrame.from_dict(attrs)
    print("Producto: ", attrs[0])
    print("Marca: ", attrs[data.AttributeInfo.BRAND])
    print("Precio: ", attrs[data.AttributeInfo.PRICE])

