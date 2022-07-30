
from selenium.common.exceptions import WebDriverException, TimeoutException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import tests
from domains import DomainInfo, DomainInfo as DI
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
        url = tests.testURLs[domain]
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
