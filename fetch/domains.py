import json
import logging
import copy
import re
import fetch
from enum import Enum
from bs4 import BeautifulSoup, ResultSet


class AttributeInfo(Enum):
    """
    Enum that contains all supported extracted attributes.
    """
    PROD_NAME = "prod_name"
    BRAND = "brand"
    PRICE = "price"

    @staticmethod
    def find_text(elements, text):
        for elem in elements:
            if elem.find(string=text):
                return elem
        # logging.error("Cannot find text in elements")
        return elements

    @staticmethod
    def find_attribute(dictio: dict, source: BeautifulSoup | ResultSet, index=0):
        """
        Returns attribute text from source. index param should start in 0.

        :param dictio: dict
        :param source: BeautifulSoup | ResultSet
        :return:
        """
        # Aliases for convenience
        HC = HTMLComponent
        AI = AttributeInfo
        if dictio[HC.ELEMENT][0] == fetch.NULLVAL:
            return fetch.NOT_SUPPORTED
        if HC.TEXT in dictio.keys() and dictio[HC.TEXT][index] != fetch.NULLVAL:
            search = AI.find_text(source, dictio[HC.TEXT])  # is Tag
        else:
            search = source  # is ResultSet if index != 0

        # is first search and not text search
        if not isinstance(search, ResultSet):
            matches = search.find_all(dictio[HC.ELEMENT][index], attrs={dictio[HC.ATTRIBUTE][index]: dictio[HC.NAME][index]})
        else:
            matches = search

        # (is a previous search or (has multiple tags and is not a container)) and is not first search
        if (isinstance(search, ResultSet) or (len(matches) > 1 and HC.ISCONTAINER in dictio.keys() and dictio[HC.ISCONTAINER][index] is False)) and index != 0:
            matches = AI.iterate_tags(dictio, matches, index)

        if HC.GETFIRST in dictio.keys() and dictio[HC.GETFIRST][index] is True:
            while len(matches) > 1:
                matches.pop(-1)
        logging.debug("Match: " + str(matches))
        return AI.check_matches(dictio, source, matches, index)

    @staticmethod
    def iterate_tags(dictio, tags: ResultSet, index):
        HC = HTMLComponent
        matches = []
        for tag in tags:
            matches = tag.find_all(dictio[HC.ELEMENT][index], attrs={dictio[HC.ATTRIBUTE][index]: dictio[HC.NAME][index]})
            if len(matches) == 1:
                break
        return matches

    @staticmethod
    def check_matches(dictio, source, matches: ResultSet, index):
        HC = HTMLComponent
        # If there is more than 1 match or current tag is from a container
        if (len(matches) > 1 or (HC.ISCONTAINER in dictio.keys() and dictio[HC.ISCONTAINER][index] is True)) and index < fetch.LIST_MAX and dictio[HC.ELEMENT][index + 1] != fetch.NULLVAL:
            logging.debug("Trying to find attribute with successive elements")
            return AttributeInfo.find_attribute(dictio, matches, index + 1)
        # If there are no matches but there are more components to find
        elif len(matches) == 0 and index < fetch.LIST_MAX and dictio[HC.ELEMENT][index + 1] != fetch.NULLVAL:
            logging.debug("Current tag did not return matches. Trying another tag")
            return AttributeInfo.find_attribute(dictio, source, index + 1)
        # If there are no matches
        elif len(matches) == 0:
            logging.error("Could not find attribute")
            return None
        else:
            attr = matches[0].getText()
            return attr


class HTMLComponent(Enum):
    """
    Enum that contains all HTML elements needed to find attributes in page source.
    """
    # Used in bsoup.find[_all]("element", attrs={"attribute":"name"})
    ELEMENT = "element"
    ATTRIBUTE = "attribute"
    NAME = "name"
    # Used to find by text
    TEXT = "text"
    # Used to check if element is a container
    ISCONTAINER = "iscontainer"
    # Ignores multiple findings and uses the first one
    GETFIRST = "getfirst"


class TLDInfo(Enum):
    """
    Supported TLDs (top-level domains).
    """
    COM = "com"
    ES = "es"
    FR = "fr"
    CO_UK = "co.uk"
    DE = "de"
    IT = "it"
    NL = "nl"
    PL = "pl"
    PT = "pt"


class DomainInfo(Enum):
    """
    Class with methods that return dictionaries with the corresponding HTML components of each attribute in a page.
    """
    # Supported domains
    ELCORTEINGLES = "elcorteingles"
    PCCOMPONENTES = "pccomponentes"
    AMAZON = "amazon"
    ZALANDO = "zalando"
    WORTEN = "worten"
    NIKE = "nike"
    ADIDAS = "adidas"
    CONVERSE = "converse"
    FOOTDISTRICT = "footdistrict"
    # Partially supported domains
    CARREFOUR = "carrefour"
    ALIEXPRESS = "aliexpress"

    def __init__(self, _):
        self.domain_info_dictio = None

    def set_domain_info(self, attr_dictio: dict):
        """
        Used to change elements to fetch based on a precondition
        """
        self.domain_info_dictio = attr_dictio

    def get_domain_info(self):
        """
        Returns the domain dictionary
        """
        if self.domain_info_dictio is not None:
            return self.domain_info_dictio
        with open(fetch.DOMAINS_PATH, 'r') as f:
            data: dict = json.load(f)[self.value][fetch.TLD.value]
            # Replace all str keys with enum keys
            htmlkeys = {i.value: i for i in HTMLComponent}
            attrkeys = {i.value: i for i in AttributeInfo}
            for attr in attrkeys.keys():
                if attr in data.keys():
                    for html in htmlkeys.keys():
                        if html in data[attr].keys():
                            data[attr][htmlkeys[html]] = data[attr].pop(html)
                    data[attrkeys[attr]] = data.pop(attr)
        return data
        # elements = [fetch.NULLVAL for _ in range(0, fetch.LIST_MAX)]
        # html_dictio = {i: copy.deepcopy(elements) for i in HC}
        # for i in range(0, fetch.LIST_MAX):
        #     html_dictio[HC.ISCONTAINER][i] = False
        #     html_dictio[HC.GETFIRST][i] = False
        # attr_dictio = {i: copy.deepcopy(html_dictio) for i in AI}
        # match self:
        #     case DI.ELCORTEINGLES:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'id'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'js-classes-detail-title'
        #         # BRAND
        #         attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'a'
        #         attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.BRAND][HC.NAME][0] = 'product_detail-brand'
        #         # PRICE
        #         # Price container
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'product_detail-buy-price-container'
        #         attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
        #         # Actual price
        #         attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'p'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][1] = 'price _big'
        #         # Discounted price
        #         attr_dictio[AI.PRICE][HC.ELEMENT][2] = 'p'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][2] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][2] = 'price _big _sale'
        #     case DI.AMAZON:     # TODO Check books/other products
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'span'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'id'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'productTitle'
        #         # BRAND
        #         attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'a'
        #         attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'id'
        #         attr_dictio[AI.BRAND][HC.NAME][0] = 'bylineInfo'
        #         # PRICE
        #         # Price container
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'span'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = re.compile('(.*apexPriceToPay.*|.*priceToPay.*)')
        #         attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
        #         # Price (new)
        #         attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][1] = 'a-offscreen'
        #         attr_dictio[AI.PRICE][HC.GETFIRST][1] = True
        #     case DI.PCCOMPONENTES:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'h4'
        #         # BRAND
        #         # Product data container
        #         attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.BRAND][HC.NAME][0] = 'ficha-producto__datos-de-compra white-card-movil'
        #         attr_dictio[AI.BRAND][HC.ISCONTAINER][0] = True
        #         # Brand row
        #         attr_dictio[AI.BRAND][HC.ELEMENT][1] = 'div'
        #         attr_dictio[AI.BRAND][HC.ATTRIBUTE][1] = 'class'
        #         attr_dictio[AI.BRAND][HC.NAME][1] = 'col-xs-12 col-sm-9'
        #         # PRICE
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'id'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'precio-main'
        #     case DI.ZALANDO:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'span'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'EKabf7 R_QwOV'
        #         # BRAND
        #         attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'h3'
        #         attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.BRAND][HC.NAME][0] = 'SZKKsK mt1kvu FxZV-M pVrzNP _5Yd-hZ'
        #         # PRICE
        #         # Price container
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'Bqz_1C'
        #     case DI.WORTEN:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'w-product__name iss-classes-name'
        #         # BRAND
        #         # Info container
        #         attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'li'
        #         attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.BRAND][HC.NAME][0] = 'clearfix'
        #         attr_dictio[AI.BRAND][HC.ISCONTAINER][0] = True
        #         # Text search inside info container
        #         attr_dictio[AI.BRAND][HC.TEXT][1] = 'Marca'
        #         # Brand
        #         attr_dictio[AI.BRAND][HC.ELEMENT][1] = 'span'
        #         attr_dictio[AI.BRAND][HC.ATTRIBUTE][1] = 'class'
        #         attr_dictio[AI.BRAND][HC.NAME][1] = 'details-value'
        #         # PRICE
        #         # Price (Worten)
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'span'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'w-product__price__current iss-classes-current-price'
        #         # Price (first marketplace seller)
        #         attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][1] = 'classes-offers__price-title'
        #     case DI.CARREFOUR:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'classes-header__name'
        #         # BRAND NOT SUPPORTED (is inside classes name)
        #         # PRICE
        #         # Seller container
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'buybox'
        #         attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
        #         # Current price
        #         attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][1] = 'buybox__price'
        #         # Discounted price
        #         attr_dictio[AI.PRICE][HC.ELEMENT][2] = 'span'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][2] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][2] = 'buybox__price--current'
        #     case DI.ALIEXPRESS:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'classes-title-text'
        #         # BRAND NOT SUPPORTED (is inside classes name)
        #         # PRICE
        #         # Price container
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'uniform-banner'
        #         attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
        #         # Price
        #         attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][1] = 'uniform-banner-box-price'
        #     case DI.NIKE:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'data-test'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'classes-title'
        #         attr_dictio[AI.PROD_NAME][HC.GETFIRST][0] = True
        #         # BRAND NOT SUPPORTED (is always Nike)
        #         # PRICE
        #         # Price container
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'classes-price__wrapper css-13hq5b3'
        #         attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
        #         # Discounted price
        #         attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'data-test'
        #         attr_dictio[AI.PRICE][HC.NAME][1] = 'classes-price-reduced'
        #         # Current price
        #         attr_dictio[AI.PRICE][HC.ELEMENT][2] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][2] = 'data-test'
        #         attr_dictio[AI.PRICE][HC.NAME][2] = 'classes-price'
        #
        #     case DI.ADIDAS:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'data-testid'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'classes-title'
        #         # BRAND NOT SUPPORTED (is always Adidas)
        #         # PRICE
        #         # Price container
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'classes-description___2cJO2'
        #         attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
        #         # Discounted price
        #         attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][1] = 'gl-price-item gl-price-item--sale notranslate'
        #         # Current price
        #         attr_dictio[AI.PRICE][HC.ELEMENT][2] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][2] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][2] = 'gl-price-item notranslate'
        #     case DI.CONVERSE:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'itemprop'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'name'
        #         # BRAND NOT SUPPORTED (is always Converse)
        #         # PRICE
        #         # Price container
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'itemprop'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'offers'
        #         attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
        #         # Price (current or discounted)
        #         attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'itemprop'
        #         attr_dictio[AI.PRICE][HC.NAME][1] = 'price'
        #     case DI.FOOTDISTRICT:
        #         # PRODUCT NAME
        #         attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'span'
        #         attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'data-ui-id'
        #         attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'page-title-wrapper'
        #         # BRAND
        #         attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.BRAND][HC.NAME][0] = 'amshopby-option-link'
        #         # PRICE
        #         # Price container
        #         attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][0] = 'classes-info-price'
        #         attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
        #         # Price (current or discounted)
        #         attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
        #         attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
        #         attr_dictio[AI.PRICE][HC.NAME][1] = 'price'
        #     case _:     # Covered by detect_domain(), should never enter here
        #         logging.fatal("Domain doesn't match checks")
        #         exit(1)



class DomainSupported:
    """
    Used to mark domain support.
    """
    DI = DomainInfo
    # Add domains to mark them
    PARTIALLY_SUPPORTED = [DI.CARREFOUR,            # Domains that can fetch some attributes
                           DI.ALIEXPRESS]
    NOT_SUPPORTED = []                              # Domains that cannot/should not be fetched
