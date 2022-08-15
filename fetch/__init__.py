
from selenium.common.exceptions import WebDriverException, TimeoutException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import pyshorteners

import fetch.domains as doms
import fetch.conditions as cond
import fetch.chromedriver as cd
import pricelist as pl
import classes


AI = doms.AttributeInfo
DI = doms.DomainInfo
HC = doms.HTMLComponent
TLDI = doms.TLDInfo

# Constants
HTMLPARSER = "html.parser"
# Null values for string and numeric types
NULLVAL_STR = None
NULLVAL_NUM = -1.00
NOT_SUPPORTED = 'Unknown'
DOMAINS_PATH = 'config/domains.json'
DOMAIN: DI | None = None                       # Extracted domain from URL
TLD: TLDI | None = None                        # Extracted top-level domain from URL
PAGE_SOURCE = None                             # Current page source


def update_page_source(driver: uc.Chrome):
    global PAGE_SOURCE
    PAGE_SOURCE = BeautifulSoup(driver.page_source, features=HTMLPARSER)


def fetch_attributes(source: BeautifulSoup):
    """
    Gets all existing attributes

    :param source:
    :return:
    """
    dictio = DI.get_domain_info(DOMAIN)
    attributes = [e for e in AI]
    for attr in attributes:
        if attr in dictio.keys():
            dictio[attr] = AI.find_attribute(dictio[attr], source=source)
            if dictio[attr] is None or dictio[attr] == "None":
                dictio[attr] = NOT_SUPPORTED
        else:
            dictio[attr] = NOT_SUPPORTED
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
        if str(tld.value) in domain.split('.'):
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


def remove_key_whitespaces(dictio: dict):
    for key in dictio.keys():
        dictio[key] = str(dictio[key]).strip()


def fetch_page(url):
    driver = cd.webdriver_init()
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


def clean_content(content: BeautifulSoup):
    for s in content.select('style') + content.select('script'):
        s.decompose()


def fetch_data(url: str = None, opts=None):
    """
    Main function to fetch URLs. domain parameter useful for debugging
    :param url: str
    :param opts:
    :return: data: Data
    """
    if opts is None:
        opts = {pl.Options.V: False, pl.Options.VV: False}
    if not opts[pl.Options.VV]:
        pl.set_logger(logging.INFO)
    detect_domain(url)
    driver: uc.Chrome = fetch_page(url)
    html = driver.page_source
    global PAGE_SOURCE
    PAGE_SOURCE = BeautifulSoup(html, features=HTMLPARSER)
    cond.preconditions(url, driver, PAGE_SOURCE)
    clean_content(PAGE_SOURCE)
    if opts[pl.Options.V]:
        pl.set_logger(logging.DEBUG)
    attrs = fetch_attributes(PAGE_SOURCE)
    cond.postconditions(attrs)
    driver.quit()
    # TODO: URL must be cleaned before shortening to prevent equal products with diff URLs
    shortener = pyshorteners.Shortener().dagd
    short_url = shortener.short(url)
    prod = classes.Product(name=attrs[AI.PROD_NAME], brand=attrs[AI.BRAND], category=attrs[AI.CATEGORY],
                           color=attrs[AI.COLOR], size=attrs[AI.SIZE])
    dom = classes.Domain(name=DOMAIN.name, tld=TLD.name, short_url=short_url)
    prc = classes.Pricing(pricetag=attrs[AI.PRICE], shipping=attrs[AI.SHIPPING])
    return classes.Data(dom=dom, prod=prod, prc=prc)
