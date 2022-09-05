from dataclasses import dataclass
from common.definitions import NULLVAL_NUM, NOT_SUPPORTED
from common.domains import DomainInfo, TLDInfo


@dataclass
class Product:
    name: str
    pid: int = None
    brand: str = None
    category: str = None
    color: str = None
    size: str = None

    def __str__(self):
        string = f"""Product:
        - Name:         {self.name}
        {f'- Brand:        {self.brand}' if self.brand is not (None or NOT_SUPPORTED) else ''}
        {f'- Category:     {self.category}' if self.category is not (None or NOT_SUPPORTED) else ''}
        {f'- Color:        {self.color}' if self.color is not (None or NOT_SUPPORTED) else ''}
        {f'- Size:         {self.size}' if self.size is not (None or NOT_SUPPORTED) else ''}
        """
        return _remove_newlines(string)


@dataclass
class Domain:
    name: DomainInfo
    tld: TLDInfo
    short_url: str = None

    def __str__(self):
        string = f"""Domain:
        - Name:         {self.name.name}
        - TLD:          {self.tld.name}
        - Short URL:    {self.short_url}
        """
        return _remove_newlines(string)


@dataclass(init=False)
class Pricing:
    def __init__(self, price: str | float = None, currency: str = None, pricetag: str = None, shipping: str = None):
        if shipping is not (None and NOT_SUPPORTED):
            self.shipping = float(shipping)
        else:
            self.shipping = NULLVAL_NUM
        if pricetag is not None:
            (self.price, self.currency) = self.fromtag(pricetag)
        elif price is not None and currency is not None:
            self.price = float(price)
            self.currency = currency

    @staticmethod
    def fromtag(pricetag):
        pos = (0, -1)
        pos = [i for i in pos if not pricetag[i].isnumeric()]
        currency = pricetag[pos[0]]
        localprice = pricetag.replace(currency, "").strip()
        price = Pricing.convert_float(localprice)
        return price, currency

    @staticmethod
    def convert_float(localprice):
        """
        Converts numbers from localised format to standard float, i.e. 1.234,56 to 1234.56
        """
        if localprice.find(",") != -1 and localprice.find(".") != -1:   # 1.234,56 or 1,234.56
            if localprice.find(",") > localprice.find("."):             # 1.234,56
                price = localprice.replace(".", "").replace(",", ".")
            else:                                                       # 1,234.56
                price = localprice.replace(",", "")
        elif localprice.find(".") != -1:                                # 1234.56 or 1.234
            # TODO This could cause trouble for currencies than may have more than 2 decimal digits
            if (len(localprice) - 1) - localprice.find(".") > 2:        # 1.234
                price = localprice.replace(".", "")
            else:                                                       # 1234.56
                price = localprice
        elif localprice.find(",") != -1:                                # 1,234 or 1234,56
            # TODO This could cause trouble for currencies than may have more than 2 decimal digits
            if (len(localprice) - 1) - localprice.find(",") > 2:        # 1,234
                price = localprice.replace(",", "")
            else:                                                       # 1234,56
                price = localprice.replace(",", ".")
        else:
            price = localprice
        return float(price)

    def __str__(self):
        string = f"""Pricing:
        - Price:        {self.currency} {(self.price-self.shipping if self.shipping is float else self.price)}
        {f"- Shipping:     {self.currency} {self.shipping}" if self.shipping != NULLVAL_NUM else ''}
        """
        return _remove_newlines(string)


@dataclass
class Data:
    """
    Groups other data objects into a single object
    """
    prod: Product = None
    dom: Domain = None
    prc: Pricing = None

    def __str__(self):
        return f"""
Fetched data:
    {self.prod}
    {self.dom}
    {self.prc}
        """


class Timestamp:
    """
    Contains date (YYYY-MM-DD) and time (hh:mm:ss) which should be in the specified timezone in database
    """
    def __init__(self, date: str, time: str):
        self.date = str(date)
        time = str(time)
        if time.find("."):
            self.time = time.split(".")[0]
        else:
            self.time = time

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.date == other.date and self.time == other.time
        else:
            return False

    def isoformat(self):
        return f"{self.date} {self.time}"


class Interval:
    def __init__(self, start: Timestamp, end: Timestamp):
        self.start = start
        self.end = end

    def equal(self):
        return self.start == self.end


def _remove_newlines(string: str):
    return "\n".join([s for s in string.splitlines() if s.strip()])
