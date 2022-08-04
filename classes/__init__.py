

class Product:
    def __init__(self, name: str, brand: str = None, category: str = None):
        self.name = name
        self.brand = brand
        self.category = category

    def __str__(self):
        return f"""
        Product:
        - Name:         {self.name}
        - Brand:        {self.brand}
        - Category:     {self.category}
        """


class Domain:
    def __init__(self, name: str, tld: str):
        self.name = name
        self.tld = tld

    def __str__(self):
        return f"""
        Domain:
        - Name:         {self.name}
        - TLD:          {self.tld}
        """


class Pricing:
    def __init__(self, pricetag: str, shipping: float = 0.00):
        self.shipping = shipping
        pos = (0, -1)
        pos = [i for i in pos if not pricetag[i].isnumeric()]
        self.currency = pricetag[pos[0]]
        localprice = pricetag.replace(self.currency, "").strip()

        if localprice.find(",") < localprice.find("."):  # 1,234.56
            price = float(localprice.replace(",", ""))
        elif localprice.find(",") > localprice.find("."):  # 1.234,56
            price = float(localprice.replace(".", "").replace(",", "."))
        else:
            price = float(localprice)

        self.price = price

    def __str__(self):
        return f"""
        Pricing:
        - Price:        {self.currency} {self.price-self.shipping}
        - Shipping:     {self.currency} {self.shipping}
        
        """

