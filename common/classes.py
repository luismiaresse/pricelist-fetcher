from dataclasses import dataclass
from common.definitions import NULLVAL_NUM, NOT_SUPPORTED
from common.domains import DomainInfo, TLDInfo
from price_parser import Price


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
        {f'- Brand:        {self.brand}' if self.brand not in NOT_SUPPORTED else ''}
        {f'- Category:     {self.category}' if self.category not in NOT_SUPPORTED else ''}
        {f'- Color:        {self.color}' if self.color not in NOT_SUPPORTED else ''}
        {f'- Size:         {self.size}' if self.size not in NOT_SUPPORTED else ''}
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
    def __init__(self, price: Price = None, shipping: Price = None, pricetag: str = None, shippingtag: str = None):
        if shippingtag not in NOT_SUPPORTED:
            self.shipping = Price.fromstring(shippingtag)
        elif shipping not in NOT_SUPPORTED:
            self.shipping = shipping
        else:
            self.shipping = Price(amount=NULLVAL_NUM, amount_text=None, currency=None)

        if pricetag not in NOT_SUPPORTED:
            self.price = Price.fromstring(pricetag)
        elif price not in NOT_SUPPORTED:
            self.price = price
        else:
            raise ValueError("No valid price or pricetag was entered")

    def __str__(self):
        string = f"""Pricing:
        - Price:        {self.price.currency} {self.price.amount_float}
        {f"- Shipping:     {self.shipping.currency} {self.shipping.amount_float}" if self.shipping.amount_float not in NOT_SUPPORTED else ''}
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
