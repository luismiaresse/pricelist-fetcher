
from selenium.common.exceptions import WebDriverException, TimeoutException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import pyshorteners
import fetch.conditions as cond
import fetch.chromedriver as cd
from common.domains import AttributeInfo as AI, DomainInfo as DI, TLDInfo as TLDI
from common.definitions import HTMLPARSER, NOT_SUPPORTED, UNKNOWN, clean_content
from common.classes import Product, Domain, Pricing, Data


def fetch_attributes(source: BeautifulSoup, dom: Domain):
    """
    Gets all existing attributes

    :param source: BeautifulSoup
    :param dom: Domain
    :return: dictio: dict
    """
    dictio = DI.get_domain_dictio(dom.name, dom.tld)
    attributes = [e for e in AI]
    for attr in attributes:
        if attr in dictio:
            if isinstance(dictio[attr], str):
                pass
            else:
                dictio[attr] = AI.find_attribute(dictio[attr], source=source)
                if dictio[attr] in NOT_SUPPORTED:
                    dictio[attr] = UNKNOWN
        else:
            dictio[attr] = UNKNOWN
    return dictio


def detect_tld(domain: str):
    """
    Detects top-level domain from URL

    :param domain: str
    :return: tld: TLDInfo
    """
    tlds = [e for e in TLDI]
    for tld in tlds:
        if str(tld.value) in domain.split('.'):
            return TLDI(tld)


def detect_domain(url: str):
    """
    Checks domain of URL in the supported domains enum.

    :param url: str
    """
    domain = urlparse(url).netloc
    tld = detect_tld(domain)
    for d in [dom for dom in DI]:
        if domain in str(d.value) or str(d.value) in domain:
            return Domain(name=d, tld=tld)
    else:
        logging.error("Domain not recognized")
        raise ValueError(f"Domain {domain} not recognized")


def fetch_page(url, driver=None):
    if driver is None:
        driver = cd.webdriver_init()

    try:
        driver.execute_script("window.open('');")          # Open new tab
        driver.switch_to.window(driver.window_handles[1])  # Switch to new tab
        driver.get(url)
    except TimeoutException as e:
        logging.error(e.msg + " Retrying one more time")
        try:
            driver.get(url)
        except TimeoutException as e:
            logging.fatal(e.msg + " Retry failed.")
            raise e
    except WebDriverException as e:
        logging.fatal(e.msg)
        exit(1)
    return driver


def validate_data(attrs, dom: Domain, surl):
    must_attrs = (attrs[AI.PROD_NAME], attrs[AI.PRICETAG])
    must_vars = (dom.name.name, dom.tld.name, surl)
    for attr in must_attrs + must_vars:
        if attr in NOT_SUPPORTED:
            logging.fatal("Could not fetch some mandatory attributes")
            logging.debug("Attributes state:")
            for att in must_attrs + must_vars:
                logging.debug(f"{att}")
            raise ValueError(f"Could not fetch some mandatory attributes for domain {dom.name.name}")


def shorten_url(url):
    if "https://da.gd" not in url:
        # TODO: URL must be cleaned before shortening to prevent equal products with diff URLs
        shortener = pyshorteners.Shortener().dagd
        url = shortener.short(url)
    return url


def get_page_soup(url, driver=None):
    logging.info(f"Checking {urlparse(url).netloc}...")
    domain = detect_domain(url)
    driver: uc.Chrome = fetch_page(url, driver)
    html = driver.page_source
    source = BeautifulSoup(html, features=HTMLPARSER)
    source = cond.preconditions(url, domain, driver, source)
    driver.close()
    driver.quit()
    clean_content(source)
    return source


def get_data_from_soup(url: str, source: BeautifulSoup):
    """
    Gets data from BeautifulSoup object.

    :param url: str
    :param source: BeautifulSoup
    :return: data: Data
    """
    domain = detect_domain(url)   # Needed twice (for tests)
    attrs = fetch_attributes(source, domain)
    cond.postconditions(attrs, domain)
    url = shorten_url(url)
    validate_data(attrs, domain, url)
    prod = Product(name=attrs[AI.PROD_NAME], brand=attrs[AI.BRAND], category=attrs[AI.CATEGORY],
                   color=attrs[AI.COLOR], size=attrs[AI.SIZE])
    dom = Domain(name=domain.name, tld=domain.tld, short_url=url)
    prc = Pricing(pricetag=attrs[AI.PRICETAG], shippingtag=attrs[AI.SHIPPING])
    data = Data(dom=dom, prod=prod, prc=prc)
    return data


def fetch_data(url: str, driver: uc.Chrome = None):
    """
    Main function to fetch data from URL.

    :param url: str
    :param driver: Chromedriver
    :return: data: Data
    """
    source = get_page_soup(url, driver)
    data = get_data_from_soup(url, source)
    return data
