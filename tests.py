from fetch.product import fetch_data, testURLs
from data import AttributeInfo as AI

class TestClass:
    # Test if any attribute is missing
    def test_domains(self):
        for dom, url in testURLs.items():
            attrs = fetch_data(url)
            print("\nDominio: ", dom.name)
            print("Producto: ", attrs[AI.PROD_NAME])
            print("Marca: ", attrs[AI.BRAND])
            print("Precio: ", attrs[AI.PRICE])
            for attr in attrs.values():
                if attr is None:
                    raise AssertionError(str(dom.name) + " (" + str(dom.value) + ") failed: attribute is None")
