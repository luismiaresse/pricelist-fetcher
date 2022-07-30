import logging
from enum import Enum

from bs4 import BeautifulSoup, ResultSet

# Constants
NULLVAL = 'null'    # Non-existent value in list
LIST_MAX = 5        # Maximum number of elements in each html component list
NOT_SUPPORTED = 'Not supported'
NOT_AVAILABLE = 'Not available'


class AttributeInfo(Enum):
    """
    Enum that contains all supported extracted attributes.
    For use with fetch data dictionaries.
    """
    PROD_NAME = 0
    BRAND = 1
    PRICE = 2


    @staticmethod
    def find_text(elements, text):
        for elem in elements:
            if elem.find(text=text):
                return elem
        # logging.error("Cannot find text in elements")
        return elements

    @staticmethod
    def find_attribute(dictio, domain, source: BeautifulSoup | ResultSet, index=0):
        """
        Returns attribute text from source. index param should start in 0.

        :param dictio:
        :param domain:
        :param source:
        :return:
        """
        # Aliases for convenience
        HC = HTMLComponent
        AI = AttributeInfo
        if dictio[HC.ELEMENT][0] == NULLVAL:
            return NOT_SUPPORTED
        if dictio[HC.TEXT][index] != NULLVAL:
            search = AI.find_text(source, dictio[HC.TEXT])  # is Tag
        else:
            search = source  # is ResultSet if index != 0

        # is first search and not text search
        if not isinstance(search, ResultSet):
            matches = search.find_all(dictio[HC.ELEMENT][index], attrs={dictio[HC.ATTRIBUTE][index]: dictio[HC.NAME][index]})
        else:
            matches = search

        # (is a previous search or (has multiple tags and is not a container)) and is not first search
        if (isinstance(search, ResultSet) or (len(matches) > 1 and dictio[HC.ISCONTAINER][index] is False)) and index != 0:
            matches = AI.iterate_tags(dictio, matches, index)

        if dictio[HC.GETFIRST][index] is True:
            while len(matches) > 1:
                matches.pop(-1)
        logging.debug("Match: " + str(matches))
        return AI.check_matches(dictio, domain, source, matches, index)

    @staticmethod
    def iterate_tags(dictio, tags: ResultSet, index):
        HC = HTMLComponent
        matches = []
        for tag in tags:
            matches = tag.find_all(dictio[HC.ELEMENT][index], attrs={dictio[HC.ATTRIBUTE][index]: dictio[HC.NAME][index]})
            if len(matches) == 1:
                break
        return matches

    @staticmethod
    def check_matches(dictio, domain, source, matches: ResultSet, index):
        # If there is more than 1 match or current tag is from a container
        if (len(matches) > 1 or dictio[HTMLComponent.ISCONTAINER][index] is True) and index < LIST_MAX and dictio[HTMLComponent.ELEMENT][index + 1] != NULLVAL:
            logging.debug("Trying to find attribute with successive elements")
            return AttributeInfo.find_attribute(dictio, domain, matches, index + 1)
        # If there are no matches but there are more components to find
        elif len(matches) == 0 and index < LIST_MAX and dictio[HTMLComponent.ELEMENT][index + 1] != NULLVAL:
            logging.debug("Current tag did not return matches. Trying another tag")
            return AttributeInfo.find_attribute(dictio, domain, source, index + 1)
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
    For use with DomainParams methods dictionaries.
    """
    # Used in bsoup.find[_all]("element", attrs={"attribute":"name"})
    ELEMENT = 0
    ATTRIBUTE = 1
    NAME = 2
    # Used to find by text
    TEXT = 3
    # Used to check if element is a container
    ISCONTAINER = 4
    # Ignores multiple findings and uses the first one
    GETFIRST = 5
