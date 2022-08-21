
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
import logging
import re

import classes
import fetch

AI = fetch.domains.AttributeInfo
HC = fetch.domains.HTMLComponent
DI = fetch.domains.DomainInfo


def preconditions(url: str, driver: uc.Chrome, source: BeautifulSoup):
    """
    Executes extra steps for specific websites after getting their page.

    :param url: str
    :param driver: chromedriver
    :param source: BeautifulSoup
    :return: updated source: BeautifulSoup
    """
    match fetch.DOMAIN:
        # case DI.ELCORTEINGLES:
        #     # Needed to bypass 5-second timer for bots
        #     attr_dictio = DI.get_domain_info(DI.ELCORTEINGLES)
        #     delay = 5
        #     # Waits -delay- seconds or until -element- is present
        #     logging.info("Waiting for bot validation...")
        #     try:
        #         WebDriverWait(driver, delay) \
        #             .until(EC.presence_of_element_located((By.ID, attr_dictio[AI.PROD_NAME][HC.NAME][0])))
        #     except TimeoutException:
        #         logging.fatal("Timeout: Could not bypass bot detection")
        #         exit(1)
        case DI.WORTEN:
            # Switch price container to marketplace if Worten does not exist
            attr_dictio = DI.get_domain_info(DI.WORTEN)
            if not source.find(attr_dictio[AI.PRICETAG][HC.ELEMENT],
                               attrs={attr_dictio[AI.PRICETAG][HC.ATTRIBUTE][0]: attr_dictio[AI.PRICETAG][HC.NAME][0]}):
                # Price container (marketplace)
                attr_dictio[AI.PRICETAG][HC.ELEMENT][0] = 'li'
                attr_dictio[AI.PRICETAG][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICETAG][HC.NAME][0] = 'accordion-item'
                attr_dictio[AI.PRICETAG][HC.ISCONTAINER] = [True, False]
                DI.set_domain_info(DI.WORTEN, attr_dictio)
        case DI.NIKE:
            if source.find("h1", attrs={"class": re.compile('.*not-found.*')}):
                logging.error("Product is not available or does not exist")
                exit(1)
            # Detect if page is SNKRS
            if "launch" in url:
                attr_dictio = DI.get_domain_info(DI.NIKE)
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
                DI.set_domain_info(DI.NIKE, attr_dictio)
        case DI.FOOTLOCKER:
            # Waits for the product to be loaded
            delay = 3
            try:
                driver.implicitly_wait(delay)
                soup = fetch.update_page_source(driver)
                return soup
            except TimeoutException:
                logging.fatal("Timeout: Could not load product info")
                exit(1)
    return source


def postconditions(attrs: dict):
    """
    Processes data for specific domains.

    :param attrs: dict
    """
    match fetch.DOMAIN:
        case DI.PCCOMPONENTES:
            # Remove P/N code and trailing newline from brand
            attrs[AI.BRAND] = fetch.split_and_join_str(attrs[AI.BRAND], '-', None, 0).rsplit("\n")[0]
        case DI.AMAZON:
            # Removes spaces before and after product name
            attrs[AI.PROD_NAME] = fetch.split_and_join_str(attrs[AI.PROD_NAME])
            text = str(attrs[AI.BRAND])
            # Removes "Visit the Store of " or "Brand: "
            match fetch.TLD:
                case fetch.TLDI.ES:
                    if "Marca" in text:
                        attrs[AI.BRAND] = text.removeprefix("Marca: ")
                    else:
                        attrs[AI.BRAND] = text.removeprefix("Visita la Store de ")
                case fetch.TLDI.FR:
                    if "Marque" in text:
                        attrs[AI.BRAND] = text.removeprefix("Marque : ")
                    else:
                        attrs[AI.BRAND] = text.removeprefix("Visiter la boutique ")
                case fetch.TLDI.COM:
                    if "Brand" in text:
                        attrs[AI.BRAND] = text.removeprefix("Brand: ")
                    else:
                        attrs[AI.BRAND] = text.removeprefix("Visit the Store of ")
        case DI.WORTEN:
            if attrs[AI.SHIPPING] is not None:
                pos = str(attrs[AI.SHIPPING]).find(classes.Pricing.fromtag(attrs[AI.PRICETAG])[1])
                attrs[AI.SHIPPING] = classes.Pricing.fromtag(attrs[AI.SHIPPING][pos:])[0]
        case DI.ZALANDO:
            # Removes 'desde '
            if attrs[AI.PRICETAG] is not None and "desde" in attrs[AI.PRICETAG]:
                attrs[AI.PRICETAG] = str(attrs[AI.PRICETAG]).removeprefix("desde ")
            # Removes all after 'IVA'
            attrs[AI.PRICETAG] = re.sub("IVA.*", '', str(attrs[AI.PRICETAG]))
        case DI.NIKE | DI.ADIDAS | DI.CONVERSE:
            # Brand is always -Name-
            if attrs[AI.BRAND] == fetch.NOT_SUPPORTED:
                attrs[AI.BRAND] = fetch.DOMAIN.name
        case DI.ALIEXPRESS:
            # Gets the lower price
            if attrs[AI.PRICETAG] is not None:
                attrs[AI.PRICETAG] = str(attrs[AI.PRICETAG]).split("-")[0]
    # Common fixes
    # Remove whitespaces
    fetch.remove_key_whitespaces(attrs)
    # Change str to float
    if attrs[AI.SHIPPING] == fetch.NOT_SUPPORTED:
        attrs[AI.SHIPPING] = fetch.NULLVAL_NUM



