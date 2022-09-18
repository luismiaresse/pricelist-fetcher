
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
import logging
import re
from price_parser import Price
from common.domains import AttributeInfo as AI, DomainInfo as DI, HTMLComponent as HC, TLDInfo as TLDI
from common.classes import Domain
from common.definitions import split_and_join_str, remove_key_whitespaces, update_page_source, NOT_SUPPORTED, NULLVAL_NUM


def preconditions(url: str, dom: Domain, driver: uc.Chrome, source: BeautifulSoup):
    """
    Executes extra steps for specific websites after getting their page.

    :param url: str
    :param dom: Domain
    :param driver: chromedriver
    :param source: BeautifulSoup
    :return: updated source: BeautifulSoup
    """
    match dom.name:

        case DI.ELCORTEINGLES:
            if source.find("input", attrs={"data-status": "not_available"}):
                raise ValueError("Product is not available or does not exist")

        # Needed to bypass 5-second timer for bots
            # attr_dictio = DI.get_domain_info(DI.ELCORTEINGLES)
            # delay = 5
            # # Waits -delay- seconds or until -element- is present
            # logging.info("Waiting for bot validation...")
            # try:
            #     WebDriverWait(driver, delay) \
            #         .until(EC.presence_of_element_located((By.ID, attr_dictio[AI.PROD_NAME][HC.NAME][0])))
            # except TimeoutException:
            #     logging.fatal("Timeout: Could not bypass bot detection")
            #     exit(1)

        case DI.WORTEN:
            # Switch price container to marketplace if Worten does not exist
            attr_dictio = DI.get_domain_dictio(DI.WORTEN, dom.tld)
            if not source.find(attr_dictio[AI.PRICETAG][HC.ELEMENT],
                               attrs={attr_dictio[AI.PRICETAG][HC.ATTRIBUTE][0]: attr_dictio[AI.PRICETAG][HC.NAME][0]}):
                # Price container (marketplace)
                attr_dictio[AI.PRICETAG][HC.ELEMENT][0] = 'li'
                attr_dictio[AI.PRICETAG][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICETAG][HC.NAME][0] = 'accordion-item'
                attr_dictio[AI.PRICETAG][HC.ISCONTAINER] = [True, False]
            # Get the category from URL
            # https://worten.es/productos/<category>/...
            slash_url = url.split('/')
            attr_dictio[AI.CATEGORY] = slash_url[4].upper()
            DI.set_domain_dictio(DI.WORTEN, attr_dictio)

        case DI.NIKE:
            if source.find("h1", attrs={"class": re.compile('.*not-found.*')}):
                raise ValueError("Product is not available or does not exist")
            # Detect if page is SNKRS
            if "launch" in url:
                attr_dictio = DI.get_domain_dictio(DI.NIKE, dom.tld)
                # Product name
                attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h5'
                attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'data-qa'
                attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'classes-title'
                # Sub-brand
                attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'h1'
                attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.BRAND][HC.NAME][0] = 'headline-5=small'
                # Price
                attr_dictio[AI.PRICETAG][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICETAG][HC.ATTRIBUTE][0] = 'data-qa'
                attr_dictio[AI.PRICETAG][HC.NAME][0] = 'price'
                attr_dictio[AI.PRICETAG][HC.ISCONTAINER][0] = False
                DI.set_domain_dictio(DI.NIKE, attr_dictio)

        case DI.FOOTLOCKER:
            # Waits for the product to be loaded
            delay = 3
            try:
                driver.implicitly_wait(delay)
                soup = update_page_source(driver)
                return soup
            except TimeoutException:
                logging.fatal("Timeout: Could not load product info")
                exit(1)

    return source


def postconditions(attrs: dict, dom: Domain):
    """
    Processes data for specific domains.

    :param attrs: dict
    :param dom: Domain
    """
    # Change str to float
    if attrs[AI.SHIPPING] in NOT_SUPPORTED:
        attrs[AI.SHIPPING] = NULLVAL_NUM
    match dom.name:

        case DI.PCCOMPONENTES:
            # Remove P/N code and trailing newline from brand
            attrs[AI.BRAND] = split_and_join_str(attrs[AI.BRAND], '-', None, 0).rsplit("\n")[0]

        case DI.AMAZON:
            # Removes spaces before and after product name
            attrs[AI.PROD_NAME] = split_and_join_str(attrs[AI.PROD_NAME])
            text = str(attrs[AI.BRAND])
            # Removes "Visit the Store of " or "Brand: "
            # TODO Do for all Amazon domains
            match dom.tld:
                case TLDI.ES:
                    if "Marca" in text:
                        attrs[AI.BRAND] = text.removeprefix("Marca: ")
                    else:
                        attrs[AI.BRAND] = text.removeprefix("Visita la Store de ")
                case TLDI.FR:
                    if "Marque" in text:
                        attrs[AI.BRAND] = text.removeprefix("Marque : ")
                    else:
                        attrs[AI.BRAND] = text.removeprefix("Visiter la boutique ")
                case TLDI.COM:
                    if "Brand" in text:
                        attrs[AI.BRAND] = text.removeprefix("Brand: ")
                    else:
                        attrs[AI.BRAND] = text.removeprefix("Visit the Store of ")

        case DI.WORTEN:
            if attrs[AI.SHIPPING] not in NOT_SUPPORTED:
                attrs[AI.SHIPPING] = Price.fromstring(attrs[AI.SHIPPING])

        case DI.NIKE | DI.ADIDAS | DI.CONVERSE:
            # Brand is always -Name-
            attrs[AI.BRAND] = dom.name.name

    # Common fixes
    # Remove whitespaces
    remove_key_whitespaces(attrs)
