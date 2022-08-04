
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
import logging
import re
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
    :return:
    """
    match fetch.DOMAIN:
        # case DI.ELCORTEINGLES:
        #     pass
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
            if not source.find(attr_dictio[AI.PRICE][HC.ELEMENT],
                               attrs={attr_dictio[AI.PRICE][HC.ATTRIBUTE][0]: attr_dictio[AI.PRICE][HC.NAME][0]}):
                # Price container (marketplace)
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'li'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'accordion-item'
                attr_dictio[AI.PRICE][HC.ISCONTAINER] = [True, False]
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
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
                attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
                attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'data-qa'
                attr_dictio[AI.PRICE][HC.NAME][0] = 'price'
                attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = False
                DI.set_domain_info(DI.NIKE, attr_dictio)


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
            # Removes spaces before and after classes name
            attrs[AI.PROD_NAME] = fetch.split_and_join_str(attrs[AI.PROD_NAME])
            # Removes "Visit the Store of " and "Brand: "
            text = str(attrs[AI.BRAND])
            if "Marca" in text:
                attrs[AI.BRAND] = text.removeprefix("Marca: ")
            else:
                attrs[AI.BRAND] = text.removeprefix("Visita la Store de ")

        case DI.ZALANDO:
            # Removes 'desde '
            if attrs[AI.PRICE] is not None and "desde" in attrs[AI.PRICE]:
                attrs[AI.PRICE] = str(attrs[AI.PRICE]).removeprefix("desde ")
            # Removes all after 'IVA'
            attrs[AI.PRICE] = re.sub("IVA.*", '', str(attrs[AI.PRICE]))
        case DI.NIKE | DI.ADIDAS | DI.CONVERSE:
            # Brand is always -Name-
            if attrs[AI.BRAND] == fetch.NOT_SUPPORTED:
                attrs[AI.BRAND] = fetch.DOMAIN.name
        case DI.ALIEXPRESS:
            # Gets the lower price
            if attrs[AI.PRICE] is not None:
                attrs[AI.PRICE] = str(attrs[AI.PRICE]).split("-")[0]
    # Common fixes
    # Remove whitespaces
    attrs[AI.PROD_NAME] = str(attrs[AI.PROD_NAME]).strip()
    attrs[AI.BRAND] = str(attrs[AI.BRAND]).strip()
    attrs[AI.PRICE] = str(attrs[AI.PRICE]).strip()
