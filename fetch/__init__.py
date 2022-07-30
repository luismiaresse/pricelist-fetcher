# Selenium (headless browser)
# from selenium import webdriver


from selenium.common.exceptions import WebDriverException, TimeoutException
# from selenium.webdriver.chrome.options import Options

# Undetected chromedriver (avoid bot detection)
import undetected_chromedriver as uc

# BeautifulSoup (find info in page source)
from bs4 import BeautifulSoup

# URL parsing
from urllib.parse import urlparse

# Parameters and logging
import argparse
import logging

# Internal classes
from domains import DomainInfo, DomainInfo as DI
import data
from data import AttributeInfo as AI
from pricelist import Options, set_logger
import fetch.conditions

# Constants
HTMLPARSER = "html.parser"


def webdriver_init():
    chrome_options = uc.ChromeOptions()
    chrome_options.headless = True
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    # chrome_options.add_argument('--user-agent= Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:70.0) Gecko/20100101 Firefox/70.0')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver


def fetch_attributes(domain, source: BeautifulSoup):
    """
    Gets all existing attributes

    :param domain:
    :param source:
    :return:
    """
    dictio = DI.get_domain_info(domain)
    attributes = [e for e in AI]
    for attr in attributes:
        dictio[attr] = AI.find_attribute(dictio[attr], domain, source=source)
    return dictio


def detect_domain(url):
    """
    Checks domain of URL in the supported domains enum and returns it.

    :param url:
    :return: domain
    """
    domain = urlparse(url).netloc
    logging.info("Checking domain " + domain + "...")
    doms = [e for e in DomainInfo]
    for dom in doms:
        if domain in str(dom.value) or str(dom.value) in domain:
            return dom
    else:
        logging.error("Domain not recognized")
        exit(1)


def split_and_join_str(text: str, split_char: str = None, join_char: str | None = ' ', word_index: int = None):
    """
    Splits and joins text.
    """
    string = text.split(split_char)
    if join_char is not None:
        string = join_char.join(string)
    elif word_index is not None:
        return string[word_index]
    return string


# def preconditions(url: str, domain: DomainInfo, driver: uc.Chrome, source: BeautifulSoup):
#     """
#     Executes extra steps for specific websites after getting their page.
#
#     :param url: str
#     :param domain: DomainInfo
#     :param driver: chromedriver
#     :param source: BeautifulSoup
#     :return:
#     """
#     match domain:
#         case DI.ELCORTEINGLES:
#             pass
#             # Needed to bypass 5-second timer for bots
#             # attr_dictio = DI.get_domain_info(DI.ELCORTEINGLES)
#             # delay = 5
#             # # Waits -delay- seconds or until -element- is present
#             # logging.info("Waiting for bot validation...")
#             # try:
#             #     WebDriverWait(driver, delay) \
#             #         .until(EC.presence_of_element_located((By.ID, attr_dictio[AI.PROD_NAME][HC.NAME][0])))
#             # except TimeoutException:
#             #     logging.fatal("Timeout: Could not bypass bot detection")
#             #     exit(1)
#         case DI.WORTEN:
#             # Switch price container to marketplace if Worten does not exist
#             attr_dictio = DI.get_domain_info(DI.WORTEN)
#             if not source.find(attr_dictio[AI.PRICE][HC.ELEMENT],
#                                attrs={attr_dictio[AI.PRICE][HC.ATTRIBUTE][0]: attr_dictio[AI.PRICE][HC.NAME][0]}):
#                 # Price container (marketplace)
#                 attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'li'
#                 attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'class'
#                 attr_dictio[AI.PRICE][HC.NAME][0] = 'accordion-item'
#                 attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = True
#                 DI.set_domain_info(DI.WORTEN, attr_dictio)
#         case DI.NIKE:
#             if source.find("h1", attrs={"class": re.compile('.*not-found.*')}):
#                 logging.error("Product is not available or does not exist")
#                 exit(1)
#             # Detect if page is SNKRS
#             if "launch" in url:
#                 attr_dictio = DI.get_domain_info(DI.NIKE)
#                 # Product name
#                 attr_dictio[AI.PROD_NAME][HC.ELEMENT][0] = 'h5'
#                 attr_dictio[AI.PROD_NAME][HC.ATTRIBUTE][0] = 'data-qa'
#                 attr_dictio[AI.PROD_NAME][HC.NAME][0] = 'product-title'
#                 # Sub-brand
#                 attr_dictio[AI.BRAND][HC.ELEMENT][0] = 'h1'
#                 attr_dictio[AI.BRAND][HC.ATTRIBUTE][0] = 'class'
#                 attr_dictio[AI.BRAND][HC.NAME][0] = 'headline-5=small'
#                 # Price
#                 attr_dictio[AI.PRICE][HC.ELEMENT][0] = 'div'
#                 attr_dictio[AI.PRICE][HC.ATTRIBUTE][0] = 'data-qa'
#                 attr_dictio[AI.PRICE][HC.NAME][0] = 'price'
#                 attr_dictio[AI.PRICE][HC.ISCONTAINER][0] = False
#                 DI.set_domain_info(DI.NIKE, attr_dictio)


# def postconditions(domain, attrs: dict):
#     """
#     Processes data for specific domains.
#
#     :param domain: DomainInfo
#     :param attrs: dict
#     """
#     match domain:
#         case DI.PCCOMPONENTES:
#             # Remove P/N code and trailing newline from brand
#             attrs[AI.BRAND] = split_and_join_str(attrs[AI.BRAND], '-', None, 0).rsplit("\n")[0]
#         case DI.AMAZON:
#             # Removes spaces before and after product name
#             attrs[AI.PROD_NAME] = split_and_join_str(attrs[AI.PROD_NAME])
#             # Removes "Visit the Store of " and "Brand: "
#             text = str(attrs[AI.BRAND])
#             if "Marca" in text:
#                 attrs[AI.BRAND] = text.removeprefix("Marca: ")
#             else:
#                 attrs[AI.BRAND] = text.removeprefix("Visita la Store de ")
#
#         case DI.ZALANDO:
#             # Removes 'desde '
#             if attrs[AI.PRICE] is not None and "desde" in attrs[AI.PRICE]:
#                 attrs[AI.PRICE] = str(attrs[AI.PRICE]).removeprefix("desde ")
#             # Removes all after 'IVA'
#             attrs[AI.PRICE] = re.sub("IVA.*", '', str(attrs[AI.PRICE]))
#         case DI.NIKE | DI.ADIDAS | DI.CONVERSE:
#             # Brand is always -Name-
#             if attrs[AI.BRAND] == data.NOT_SUPPORTED:
#                 attrs[AI.BRAND] = domain.name
#     # Common fixes
#     # Remove whitespaces
#     attrs[AI.PROD_NAME] = str(attrs[AI.PROD_NAME]).strip()
#     attrs[AI.BRAND] = str(attrs[AI.BRAND]).strip()
#     attrs[AI.PRICE] = str(attrs[AI.PRICE]).strip()


def fetch_page(url):
    driver = webdriver_init()
    try:
        driver.get(url)
    except TimeoutException as e:
        logging.error(e.msg + " Retrying one more time")
        try:
            driver.get(url)
        except TimeoutException as e:
            logging.fatal(e.msg + " Retry failed.")
            exit(1)
    except WebDriverException as e:
        logging.fatal(e.msg)
        exit(1)
    return driver


def fetch_data(url: str = None, opts=None, domain=None):
    """
    Main function to fetch URLs. domain parameter useful for debugging
    :param url: str
    :param opts:
    :param domain:
    :return:
    """
    if opts is None:
        opts = {Options.V: False, Options.VV: False}

    if domain is not None:
        url = testURLs[domain]
    elif url is not None:
        domain = detect_domain(url)
    else:
        logging.error("URL not provided")
        exit(1)

    if not opts[Options.VV]:
        set_logger(logging.INFO)
    driver = fetch_page(url)
    html = driver.page_source
    content = BeautifulSoup(html, features=HTMLPARSER)
    fetch.conditions.preconditions(url, domain, driver, content)
    if opts[Options.V]:
        set_logger(logging.DEBUG)
    attrs = fetch_attributes(domain, content)
    fetch.conditions.postconditions(domain, attrs)
    return attrs


testURLs: dict[DI, str] = {
    DI.ELCORTEINGLES: "https://www.elcorteingles.es/electronica/A43663538-tv-oled-139-cm-55-sony-xr-55a84k-bravia-google-tv-4k-hdr-xr-cognitive-processor-xr-triluminos-pro-hands-free-voice-search/?color=Negro&parentCategoryId=999.52195013",
    DI.AMAZON: "https://www.amazon.es/TD-Systems-Televisores-Chromecast-K32DLC16GLE/dp/B09YVJM363",
    DI.PCCOMPONENTES: "https://www.pccomponentes.com/gigabyte-geforce-rtx-3060-gaming-oc-12gb-gddr6-rev-20",
    DI.ZALANDO: "https://www.zalando.es/nike-sportswear-air-force-1-gtx-unisex-zapatillas-anthraciteblackbarely-grey-ni115o01u-q11.html",
    DI.WORTEN: "https://www.worten.es/productos/belleza-salud-y-bebe/salud-belleza/bascula/bascula-agd-precision-agd-joyeria-MRKEAN-8436538305003",
    DI.CARREFOUR: "https://www.carrefour.es/robot-aspirador-y-friegasuelos-irobot-roomba-combo-r113840/VC4A-12554588/p",
    DI.NIKE: "https://www.nike.com/es/t/air-force-1-07-zapatillas-DMJP7P/CW2288-111",
    DI.ADIDAS: "https://www.adidas.es/sudadera-adidas-sportswear-future-icons-3-bandas/HC5255.html",
    DI.CONVERSE: "https://www.converse.com/es/shop/p/pro-leather-mid-unisex-zapatillas-high-top/169261MP.html",
    DI.FOOTDISTRICT: "https://footdistrict.com/lourdes-men-s-graphic-t-shirt-lof1xh02ap-je130-113.html",
    DI.ALIEXPRESS: "https://es.aliexpress.com/item/1005004340051230.html",
}
