
from selenium.common.exceptions import WebDriverException, TimeoutException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

import fetch.domains as doms
import pricelist as pl
import fetch.conditions as cond
import classes

AI = doms.AttributeInfo
DI = doms.DomainInfo
HC = doms.HTMLComponent
TLDI = doms.TLDInfo

# Constants
HTMLPARSER = "html.parser"
NULLVAL = 'null'                        # Non-existent value in list
LIST_MAX = 5                            # Maximum number of elements in each html component list
NOT_SUPPORTED = 'Not supported'
NOT_AVAILABLE = -1.00                    # Price when classes is not available
DOMAINS_PATH = 'fetch/domains.json'
DOMAIN: DI = None                       # Extracted domain from URL
TLD: TLDI = None                        # Extracted top-level domain from URL


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


def fetch_attributes(source: BeautifulSoup):
    """
    Gets all existing attributes

    :param source:
    :return:
    """
    dictio = DI.get_domain_info(DOMAIN)
    attributes = [e for e in AI]
    for attr in attributes:
        dictio[attr] = AI.find_attribute(dictio[attr], source=source)
    return dictio


def detect_tld(domain: str):
    """
    Detects top-level domain from URL
    :param domain: str
    :return: tld: TLDInfo
    """
    global TLD
    tlds = [e for e in TLDI]
    for tld in tlds:
        if str(tld.value) in domain:
            TLD = TLDI(tld)


def detect_domain(url: str):
    """
    Checks domain of URL in the supported domains enum and returns it.

    :param url: str
    :return: domain: DomainInfo
    """
    global DOMAIN
    global TLD
    domain = urlparse(url).netloc
    detect_tld(domain)
    logging.info("Checking domain " + domain + "...")
    domains = [e for e in DI]
    for d in domains:
        if domain in str(d.value) or str(d.value) in domain:
            DOMAIN = d
            return d
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


def fetch_data(url: str = None, opts=None):
    """
    Main function to fetch URLs. domain parameter useful for debugging
    :param url: str
    :param opts:
    :return: prod: Product
    """
    if opts is None:
        opts = {pl.Options.V: False, pl.Options.VV: False}
    if not opts[pl.Options.VV]:
        pl.set_logger(logging.INFO)
    detect_domain(url)
    driver = fetch_page(url)
    html = driver.page_source
    content = BeautifulSoup(html, features=HTMLPARSER)
    cond.preconditions(url, driver, content)
    if opts[pl.Options.V]:
        pl.set_logger(logging.DEBUG)
    data = fetch_attributes(content)
    cond.postconditions(data)
    prod = classes.Product(name=data[AI.PROD_NAME], brand=data[AI.BRAND])
    dom = classes.Domain(name=DOMAIN.name, tld=TLD.name)
    pricing = classes.Pricing(pricetag=data[AI.PRICE])
    return prod, dom, pricing
