
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

# Constants
HTMLPARSER = "html.parser"
# Null values for string and numeric types
NULLVAL_STR = None
NULLVAL_NUM = -1.00
NOT_SUPPORTED = "Unknown"
DOMAINS_PATH = 'config/domains.json5'


def remove_key_whitespaces(dictio: dict):
    for key in dictio:
        if dictio[key] is not NOT_SUPPORTED:
            dictio[key] = str(dictio[key]).strip()


def find_char_positions(string: str, char):
    index = string.find(char)
    while index != -1:
        yield index
        index = string.find(char, index + 1)


def split_and_join_str(text: str, split_char: str = None, join_char: str | None = ' ', word_index: int = None):
    string = text.split(split_char)
    if join_char is not None:
        string = join_char.join(string)
    elif word_index is not None:
        return string[word_index]
    return string


def clean_content(content: BeautifulSoup):
    for s in content.select('style') + content.select('script'):
        s.decompose()


def update_page_source(driver: uc.Chrome):
    source = BeautifulSoup(driver.page_source, features=HTMLPARSER)
    return source
