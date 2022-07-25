
from product_fetch import *


class Options:
    """
    Enum with all possible CLI options
    """
    VERBOSE = "verbose"
    VERYVERBOSE = "veryverbose"


if __name__ == '__main__':
    args = setup_parser()
    opts = args.__dict__
    if opts[Options.VERBOSE] or opts[Options.VERYVERBOSE]:
        set_logger(logging.DEBUG)
    else:
        set_logger(logging.INFO)
    attrs = fetch_data(args.url, opts)
    print("Producto: ", attrs[AI.PROD_NAME])
    print("Marca: ", attrs[AI.BRAND])
    print("Precio: ", attrs[AI.PRICE])