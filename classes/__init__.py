import fetch


class Product:
    def __init__(self, pid: str = None, name: str = None, brand: str = None, category: str = None, color: str = None, size: str = None):
        self.pid = pid
        self.name = name
        self.brand = brand
        self.category = category
        self.color = color
        self.size = size

    def __str__(self):
        return f"""
        Product:
        - Name:         {self.name}
        - Brand:        {self.brand}
        - Category:     {self.category}
        - Color:        {self.color}
        - Size:         {self.size}
        """


class Domain:
    def __init__(self, name: str = None, tld: str = None, short_url: str = None):
        self.name = name
        self.tld = tld
        self.short_url = short_url

    def __str__(self):
        return f"""
        Domain:
        - Name:         {self.name}
        - TLD:          {self.tld}
        - Short URL:    {self.short_url}
        """


class Pricing:
    def __init__(self, price: str | float = None, currency: str = None, pricetag: str = None, shipping: str = None):
        if shipping is not None:
            self.shipping = float(shipping)
        else:
            self.shipping = fetch.NULLVAL_NUM
        if price is not None and currency is not None:
            self.price = float(price)
            self.currency = currency
        if pricetag is not None:
            pos = (0, -1)
            pos = [i for i in pos if not pricetag[i].isnumeric()]
            self.currency = pricetag[pos[0]]
            localprice = pricetag.replace(self.currency, "").strip()

            if localprice.find(",") < localprice.find("."):  # 1,234.56
                price = localprice.replace(",", "")
            elif localprice.find(",") > localprice.find("."):  # 1.234,56
                price = localprice.replace(".", "").replace(",", ".")
            else:
                price = localprice

            self.price = float(price)

    def __str__(self):
        return f"""
        Pricing:
        - Price:        {self.currency} {(self.price-self.shipping if self.shipping is float else self.price)}
        - Shipping:     {(f"{self.currency} {self.shipping}" if self.shipping != fetch.NULLVAL_NUM else fetch.NOT_SUPPORTED)}
        """


class Data:
    """
    Groups other data objects into a single object
    """
    def __init__(self, prod: Product, dom: Domain, prc: Pricing):
        self.prod = prod
        self.dom = dom
        self.prc = prc

    def __str__(self):
        return f"""
        Fetched data:
        {self.prod} {self.dom} {self.prc}
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


class Interval:
    def __init__(self, start: Timestamp, end: Timestamp):
        self.start = start
        self.end = end
