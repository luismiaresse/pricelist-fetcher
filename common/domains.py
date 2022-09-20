import hashlib
import os
import shutil

import json5
import logging
import re
import requests
from common.definitions import NOT_SUPPORTED, CONFIG_DEFAULT_PATH, CONFIG_LINUX_PATH, CONFIG_WINDOWS_PATH, DOMAINS_FILE, DOMAINS_URL, BLACKLIST_FILE, BLACKLIST_URL, TMP_LINUX_DIR, TMP_WINDOWS_DIR
from enum import Enum
from bs4 import BeautifulSoup, ResultSet


class AttributeInfo(Enum):
    """
    Enum that contains all supported extracted attributes.
    """
    PROD_NAME = "prod_name"
    PRICETAG = "price"
    # Optional attributes
    BRAND = "brand"
    CATEGORY = "category"
    COLOR = "color"
    SIZE = "size"
    SHIPPING = "shipping"

    @staticmethod
    def find_text(elements, text):
        for elem in elements:
            if elem.find(string=text):
                return elem
        # logging.error("Cannot find text in elements")
        return elements

    @staticmethod
    def find_attribute(dictio: dict, source: BeautifulSoup | ResultSet, index=0):
        """
        Returns attribute text from source. index param should start in 0.

        :param dictio: dict
        :param source: BeautifulSoup | ResultSet
        :return:
        """
        # Aliases for convenience
        HC = HTMLComponent
        AI = AttributeInfo
        if HC.TEXT in dictio and dictio[HC.TEXT][index] not in NOT_SUPPORTED:
            search = AI.find_text(source, dictio[HC.TEXT])  # is Tag
        else:
            search = source  # is ResultSet if index != 0

        # is first search and not text search
        if not isinstance(search, ResultSet):
            matches = AI.find_matches(dictio, index, search)
        else:
            matches = search

        # (is a previous search or (has multiple tags and is not a container)) and is not first search
        if (isinstance(search, ResultSet) or (len(matches) > 1 and HC.ISCONTAINER in dictio.keys() and dictio[HC.ISCONTAINER][index] is False)) and index != 0:
            matches = AI.iterate_tags(dictio, matches, index)

        if HC.GETFIRST in dictio and dictio[HC.GETFIRST][index] is True:
            while len(matches) > 1:
                matches.pop(-1)
        logging.debug(f"Match for tag '{dictio[HC.NAME][index]}': {str(matches)}")
        return AI.check_matches(dictio, source, matches, index)

    @staticmethod
    def find_matches(dictio, index, search):
        HC = HTMLComponent
        if dictio[HC.ATTRIBUTE][index] in NOT_SUPPORTED:
            matches = search.find_all(dictio[HC.ELEMENT])
        else:
            matches = search.find_all(dictio[HC.ELEMENT][index],
                                      attrs={dictio[HC.ATTRIBUTE][index]: dictio[HC.NAME][index]})
        return matches

    @staticmethod
    def iterate_tags(dictio, tags: ResultSet, index):
        matches = []
        for tag in tags:
            matches = AttributeInfo.find_matches(dictio, index, tag)
            if len(matches) == 1:
                break
        return matches

    @staticmethod
    def check_matches(dictio, source, matches: ResultSet, index):
        HC = HTMLComponent
        listsize = len(dictio[HC.ELEMENT])
        # If there is more than 1 match or current tag is from a container
        if (len(matches) > 1 or (HC.ISCONTAINER in dictio and dictio[HC.ISCONTAINER][index] is True and len(matches) != 0)) and index + 1 < listsize:
            logging.debug("Trying to find attribute with successive elements")
            return AttributeInfo.find_attribute(dictio, matches, index + 1)
        # If there are no matches but there are more components to find
        elif len(matches) == 0 and index + 1 < listsize:
            logging.debug("Current tag did not return matches. Trying another tag")
            return AttributeInfo.find_attribute(dictio, source, index + 1)
        # If there are no matches
        elif len(matches) == 0:
            logging.error("Could not find attribute")
            return None
        else:
            attr = matches[0].getText()
            return attr


class HTMLComponent(Enum):
    """
    Enum that contains all HTML elements needed to find attributes in page source.
    """
    # Used in bsoup.find[_all]("element", attrs={"attribute":"name"})
    ELEMENT = "element"
    ATTRIBUTE = "attribute"
    NAME = "name"
    # Used to find by text
    TEXT = "text"
    # Used to check if element is a container
    ISCONTAINER = "iscontainer"
    # Ignores multiple findings and uses the first one
    GETFIRST = "getfirst"
    # Marks if component can be skipped if not found
    ISSKIPPABLE = "isskippable"


class TLDInfo(Enum):
    """
    Supported TLDs (top-level domains).
    """
    COM = "com"
    NET = "net"
    ES = "es"
    FR = "fr"
    UK = "uk"
    DE = "de"
    IT = "it"
    NL = "nl"
    PL = "pl"
    PT = "pt"


class DomainInfo(Enum):
    """
    Class with methods that return dictionaries with the corresponding HTML components of each attribute in a page.
    """
    # General stores
    ELCORTEINGLES = "elcorteingles"
    AMAZON = "amazon"
    WORTEN = "worten"
    CARREFOUR = "carrefour"
    ALIEXPRESS = "aliexpress"
    # Electronics
    PCCOMPONENTES = "pccomponentes"
    COOLMOD = "coolmod"
    # Fashion, clothing and footwear
    ZALANDO = "zalando"
    NIKE = "nike"
    ADIDAS = "adidas"
    CONVERSE = "converse"
    FOOTDISTRICT = "footdistrict"
    FOOTLOCKER = "footlocker"

    def __init__(self, _):
        self.domain_dictio = None

    def set_domain_dictio(self, attr_dictio: dict):
        """
        Used to change elements to fetch based on a precondition
        """
        self.domain_dictio = attr_dictio

    def get_domain_dictio(self, tld: TLDInfo):
        """
        Returns the domain dictionary
        """
        if self.domain_dictio is not None:
            return self.domain_dictio
        conf = get_config_path()
        with open(os.path.join(conf, DOMAINS_FILE), 'r') as f:
            data = None
            domain: dict = json5.load(f)[self.value]
            tlds = domain.keys()
            for t in tlds:
                if tld.value in t.split(","):
                    data: dict = domain[t]
            if data is None:
                raise ValueError("Current TLD for this domain is not supported")
            # Replace all str keys with enum keys
            htmlkeys = {i.value: i for i in HTMLComponent}
            attrkeys = {i.value: i for i in AttributeInfo}
            for attr in attrkeys.keys():
                if attr in data.keys():
                    for html in htmlkeys.keys():
                        if html in data[attr].keys():
                            data[attr][htmlkeys[html]] = data[attr].pop(html)
                            # Detect if regex is used
                            for i in range(len(data[attr][htmlkeys[html]])):
                                if isinstance(data[attr][htmlkeys[html]][i], str) and "(" == data[attr][htmlkeys[html]][i][0] and ")" == data[attr][htmlkeys[html]][i][-1]:
                                    data[attr][htmlkeys[html]][i] = re.compile(data[attr][htmlkeys[html]][i])
                    data[attrkeys[attr]] = data.pop(attr)

        return data


def fetch_latest_config(path: str):
    """
    Fetches config files from the repository.
    """
    def fetch_file(url: str, filepath: str, overwrite: bool = False):
        if not os.path.exists(filepath) or overwrite:
            try:
                r = requests.get(url)
            except requests.exceptions.ConnectionError | requests.exceptions.Timeout:
                logging.error("Could not connect to the repository")
                return
            with open(filepath, 'w') as f:
                f.write(r.text)

    os.makedirs(path, exist_ok=True)
    logging.info("Fetching config files")
    fetch_file(DOMAINS_URL, os.path.join(path, DOMAINS_FILE), True)
    fetch_file(BLACKLIST_URL, os.path.join(path, BLACKLIST_FILE), True)


def compare_config_md5(src: str, dst: str):
    """
    Compares the MD5 hash of the config files of both directories.
    Expects a source directory (where newest config was downloaded)
    and a destination directory (where the config is stored).
    """
    def get_md5(path: str):
        with open(path, 'r') as f:
            check = hashlib.md5(f.read().encode('utf-8')).hexdigest()
        return check

    if not os.path.exists(src):
        raise ValueError("Source directory does not exist")
    if not os.path.exists(dst):
        os.makedirs(dst, exist_ok=True)
    md5 = get_md5(os.path.join(src, DOMAINS_FILE))
    srcchecks = [get_md5(os.path.join(src, file)) for file in os.listdir(src)]
    dstchecks = [get_md5(os.path.join(dst, file)) for file in os.listdir(dst)]
    return srcchecks == dstchecks


def get_config_path():
    """
    Gets the config files path.
    If they are not present, downloads them from the repository.
    """
    # Default config path (in project folder)
    # if os.path.exists(CONFIG_DEFAULT_PATH):
    #     logging.debug(f"Using config files in {CONFIG_DEFAULT_PATH}")
    #     return CONFIG_DEFAULT_PATH
    # Repository config path (in user folder)
    # Linux
    if os.name == "posix":
        if os.path.exists(CONFIG_LINUX_PATH):
            fetch_latest_config(TMP_LINUX_DIR)
            if compare_config_md5(TMP_LINUX_DIR, CONFIG_LINUX_PATH) is False:
                # Overwrite newer files (temp) to user folder
                logging.debug("MD5 Failed: Updating config files")
                for file in os.listdir(TMP_LINUX_DIR):
                    shutil.copy(os.path.join(TMP_LINUX_DIR, file), os.path.join(CONFIG_LINUX_PATH, file))
        else:
            fetch_latest_config(CONFIG_LINUX_PATH)
        logging.debug(f"Using config files in {CONFIG_LINUX_PATH}")
        return CONFIG_LINUX_PATH

    # Windows
    # TODO Needs testing on Windows
    if os.name == "nt":
        if os.path.exists(CONFIG_WINDOWS_PATH):
            fetch_latest_config(TMP_WINDOWS_DIR)
            if compare_config_md5(TMP_WINDOWS_DIR, CONFIG_WINDOWS_PATH) is False:
                # Overwrite newer files (temp) to user folder
                logging.debug("MD5 Failed: Updating config files")
                for file in os.listdir(TMP_WINDOWS_DIR):
                    shutil.copy(os.path.join(TMP_WINDOWS_DIR, file), os.path.join(CONFIG_WINDOWS_PATH, file))
        else:
            fetch_latest_config(CONFIG_WINDOWS_PATH)
        logging.debug(f"Using config files in {CONFIG_WINDOWS_PATH}")
        return CONFIG_WINDOWS_PATH
