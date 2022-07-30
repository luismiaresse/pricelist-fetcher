import logging
import copy
import re   # regex
from enum import Enum
from data import HTMLComponent as HC, AttributeInfo as AI, NULLVAL, LIST_MAX


class DomainInfo(Enum):
    """
    Class with methods that return dictionaries with the corresponding HTML components of each attribute in a page.
    """
    # Supported domains
    ELCORTEINGLES = "www.elcorteingles.es"
    PCCOMPONENTES = "www.pccomponentes.com"
    AMAZON = "www.amazon.es"
    ZALANDO = "www.zalando.es"
    WORTEN = "www.worten.es"
    NIKE = "www.nike.com"
    ADIDAS = "www.adidas.es"
    CONVERSE = "www.converse.com"
    FOOTDISTRICT = "footdistrict.com"
    # Partially supported domains
    CARREFOUR = "www.carrefour.es"
    ALIEXPRESS = "es.aliexpress.com"

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

        DI = DomainInfo
        elements = [NULLVAL for _ in range(0, LIST_MAX)]
        html_dictio = {i: copy.deepcopy(elements) for i in HC}
        for i in range(0, LIST_MAX):
            html_dictio[HC.ISCONTAINER][i] = False
            html_dictio[HC.GETFIRST][i] = False
        attr_dictio = {i: copy.deepcopy(html_dictio) for i in AI}
        match self:
            case DI.ELCORTEINGLES:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'id'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'js-product-detail-title'
                # BRAND
                attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'a'
                attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.BRAND][HC.NAME][0] = 'product_detail-brand'
                # PRICE
                # Price container
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'product_detail-buy-price-container'
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
                # Actual price
                attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'p'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][1] = 'price _big'
                # Discounted price
                attr_dictio[AI.PRICE][HC.ELEMENT][2] = 'p'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][2] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][2] = 'price _big _sale'
            case DI.AMAZON:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'span'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'id'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'productTitle'
                # BRAND
                attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'a'
                attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'id'
                attr_dictio[AI.BRAND][HC.NAME][0] = 'bylineInfo'
                # PRICE
                # Price container
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'span'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = re.compile('(.*apexPriceToPay.*|.*priceToPay.*)')
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
                # Price (new)
                attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][1] = 'a-offscreen'
                attr_dictio[AI.PRICE][HC.GETFIRST][1] = True
            case DI.PCCOMPONENTES:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'h4'
                # BRAND
                # Product data container
                attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.BRAND][HC.NAME][0] = 'ficha-producto__datos-de-compra white-card-movil'
                attr_dictio[AI.BRAND][HC.ISCONTAINER][0] = True
                # Brand row
                attr_dictio[AI.BRAND][HC.ELEMENT][1] = 'div'
                attr_dictio[AI.BRAND][HC.ATTRIBUTE][1] = 'class'
                attr_dictio[AI.BRAND][HC.NAME][1] = 'col-xs-12 col-sm-9'
                # PRICE
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'id'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'precio-main'
            case DI.ZALANDO:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'span'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'EKabf7 R_QwOV'
                # BRAND
                attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'h3'
                attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.BRAND][HC.NAME][0] = 'SZKKsK mt1kvu FxZV-M pVrzNP _5Yd-hZ'
                # PRICE
                # Price container
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'Bqz_1C'
            case DI.WORTEN:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'w-product__name iss-product-name'
                # BRAND
                # Info container
                attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'li'
                attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.BRAND][HC.NAME][0] = 'clearfix'
                attr_dictio[AI.BRAND][HC.ISCONTAINER][0] = True
                # Text search inside info container
                attr_dictio[AI.BRAND][HC.TEXT][1] = 'Marca'
                # Brand
                attr_dictio[AI.BRAND][HC.ELEMENT][1] = 'span'
                attr_dictio[AI.BRAND][HC.ATTRIBUTE][1] = 'class'
                attr_dictio[AI.BRAND][HC.NAME][1] = 'details-value'
                # PRICE
                # Price (Worten)
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'span'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'w-product__price__current iss-product-current-price'
                # Price (first marketplace seller)
                attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][1] = 'product-offers__price-title'
            case DI.CARREFOUR:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'product-header__name'
                # BRAND NOT SUPPORTED (is inside product name)
                # PRICE
                # Seller container
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'buybox'
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
                # Current price
                attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][1] = 'buybox__price'
                # Discounted price
                attr_dictio[AI.PRICE][HC.ELEMENT][2] = 'span'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][2] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][2] = 'buybox__price--current'
            case DI.ALIEXPRESS:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'product-title-text'
                # BRAND NOT SUPPORTED (is inside product name)
                # PRICE
                # Price container
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'uniform-banner'
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
                # Price
                attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][1] = 'uniform-banner-box-price'
            case DI.NIKE:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'data-test'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'product-title'
                attr_dictio[AI.PROD_NAME][HC.GETFIRST][0] = True
                # BRAND NOT SUPPORTED (is always Nike)
                # PRICE
                # Price container
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'product-price__wrapper css-13hq5b3'
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
                # Discounted price
                attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'data-test'
                attr_dictio[AI.PRICE][HC.NAME][1] = 'product-price-reduced'
                # Current price
                attr_dictio[AI.PRICE][HC.ELEMENT][2] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][2] = 'data-test'
                attr_dictio[AI.PRICE][HC.NAME][2] = 'product-price'

            case DI.ADIDAS:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'data-testid'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'product-title'
                # BRAND NOT SUPPORTED (is always Adidas)
                # PRICE
                # Price container
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'product-description___2cJO2'
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
                # Discounted price
                attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][1] = 'gl-price-item gl-price-item--sale notranslate'
                # Current price
                attr_dictio[AI.PRICE][HC.ELEMENT][2] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][2] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][2] = 'gl-price-item notranslate'
            case DI.CONVERSE:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h1'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'itemprop'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'name'
                # BRAND NOT SUPPORTED (is always Converse)
                # PRICE
                # Price container
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'itemprop'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'offers'
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
                # Price (current or discounted)
                attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'itemprop'
                attr_dictio[AI.PRICE][HC.NAME][1] = 'price'
            case DI.FOOTDISTRICT:
                # PRODUCT NAME
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'span'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'data-ui-id'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'page-title-wrapper'
                # BRAND
                attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.BRAND][HC.NAME][0] = 'amshopby-option-link'
                # PRICE
                # Price container
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'product-info-price'
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
                # Price (current or discounted)
                attr_dictio[AI.PRICE][HC.ELEMENT][1] = 'span'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][1] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][1] = 'price'
            case _:     # Covered by detect_domain(), should never enter here
                logging.fatal("Domain doesn't match checks")
                exit(1)
        return attr_dictio


class DomainSupported:
    """
    Used to mark domain support.
    """
    # Add domains to mark them
    PARTIALLY_SUPPORTED = [DomainInfo.CARREFOUR,    # Domains that can fetch some attributes
                           DomainInfo.ALIEXPRESS]
    NOT_SUPPORTED = []                              # Domains that cannot/should not be fetched
