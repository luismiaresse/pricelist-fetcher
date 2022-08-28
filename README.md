# PriceList fetcher (PLF)
A Python script that fetches information (name, brand, price...) about a product, and informs if a lower price was recorded in its price history.

![Linux Tests](https://github.com/luismiaresse/pricelist-fetcher/actions/workflows/test-linux.yml/badge.svg)

This program's output is intended to be used by PriceList, which does not exist yet, but will in the future.
It can also be used as a CLI tool.

## Prerequisites

* Latest [Google Chrome Stable](https://www.google.com/chrome/browser/desktop/)

To run the Python script directly, the following packages are also required:

* [python 3.10+](https://www.python.org/downloads/)
* [pip](https://pypi.org/project/pip/)
* [selenium](https://pypi.org/project/selenium)
* [undetected_chromedriver](https://pypi.org/project/undetected_chromedriver/)
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
* [pandas](https://pypi.org/project/pandas/)
* [psycopg](https://pypi.org/project/psycopg/)
* [psycopg-binary](https://pypi.org/project/psycopg-binary/)
* [pyshorteners](https://pypi.org/project/pyshorteners/)

Many can be autoinstalled by executing `pip install -r requirements.txt` in the project directory.

## Usage
This tool uses a command-line interface that receives the desired URL as argument and other flags. 
It can be executed by typing:

#### Linux
`$ ./pricelist [OPTIONS] URL` \
or \
`$ python pricelist.py [OPTIONS] URL` \
\
in the shell of your liking.

#### Windows
`> .\pricelist.exe [OPTIONS] URL` \
or \
`> python pricelist.py [OPTIONS] URL` \
\
in CMD or Powershell.

PLF will check the URL and return all possible attributes in the page. 
**If binary/release version is used**, the lowest price recorded in a PostgreSQL database
will also be returned.

This database can be user defined in `database/dbsecrets.py`, but must contain the same tables.

## Domains currently supported
See [DOMAINS](https://github.com/luismiaresse/pricelist-fetcher/blob/master/DOMAINS.md).

## Contributing
See [CONTRIBUTING](https://github.com/luismiaresse/pricelist-fetcher/blob/master/CONTRIBUTING.md) for instructions on how to contribute to the project.

## License
Licensed under GPLv3. This should be in any fork or redistribution, and should credit contributors as well. See [LICENSE](https://github.com/luismiaresse/pricelist-fetcher/blob/master/LICENSE).
