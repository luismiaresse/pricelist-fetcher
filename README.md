# PriceList fetcher
A Python script that fetches information (name, brand, price, ...) about a product, and informs if a lower price was recorded in its price history

![test-linux](https://github.com/luismiaresse/pricelist-fetcher/actions/workflows/test-linux.yml/badge.svg)

### Dependencies
* python 3.10+
* pip

The following Python packages can be autoinstalled by executing `pip install -r requirements.txt`:
* selenium
* undetected_chromedriver
* bs4 (BeautifulSoup)
* pandas
* psycopg (database connection, can be another if database is not PostgreSQL)
* 

### Usage
This tool uses a command-line interface that receives the desired URL as argument and other flags. 
It can be executed by typing:

#### Linux
`$ python pricelist.py [OPTIONS] URL` \
or \
`$ ./pricelist [OPTIONS] URL` \
\
in the shell of your liking.

#### Windows
`> python pricelist.py [OPTIONS] URL` \
or \
`> .\pricelist.exe [OPTIONS] URL` \
\
in CMD or Powershell.

It will check the URL and return all possible attributes in the page. 
**If binary/release version is used**, it will check the lowest price recorded in a PostgreSQL database in ElephantSQL.
This can be user defined in `database/dbsecrets.py` (should be renamed)

### Domain dictionary structure
Each domain has a dictionary with attributes as keys, and each attribute another with HTML components and flags as keys. These are needed to find text for a specific attribute.  

```
domains
├── domain0
│   ├── attribute0
│   │   │   (lists of HTML Components here) 
│   │   ├── element
│   │   │   ├── element[0]
│   │   │   ...
│   │   │   └── element[LIST_MAX-1]
│   │   │
│   │   ├── attribute
│   │   │   ├── attribute[0]
│   │   │   ...
│   │   │   └── attribute[LIST_MAX-1]
│   │   │
│   │   ├── name
│   │   │   ├── name[0]
│   │   │   ...
│   │   │   └── name[LIST_MAX-1]
│   │   │
│   │   └ ... (other components and flags)
│   │
│   ├── attribute1
│   │   ├── ...
│   │   ...
│   ...
│   
├── domain1
│   ├── ...
│   ...
...
```

### Contributing
The best way to add a domain to the domains list (`DomainInfo`) is as follows:

1. Check that the desired attributes are listed in `AttributeInfo`. If you consider that any attribute should be listed, please open an issue.
2. Fork this project and add the domain to the domains list. If a page detects the script as a bot, try to avoid it in `preconditions()` by adding a case. 
3. Inspect the page HTML and look for at least three HTML components: `element`, `attribute` and `name`.
For instance: to find `<h2 class="oBOnKe">Text I really want</h2>`, `h2` is the `element`, `class` the `attribute` and `oBOnKe` the `name`. \
If the attribute cannot be fetched as it repeats, or changes across different states (i.e. discounted price instead of regular price),
previously grab the innermost container of that attribute that is not repeated, and set the `ISCONTAINER` flag to `true`. 
This will focus the scope on where the attribute should be looked for.
4. Check different products which may modify the position, state or even presence of the attribute you are looking for and adjust the components in the previous step.
If an element is sometimes present and is preferable over another, it should be closer to the start of the list.
5. Add the domain to `DomainSupported` partially supported if there is no possible way to extract an attribute.
6. Add an URL to a product to `testURLs` to keep checking it in the future. It is preferable to be a discounted or unavailable product,
even if in the future it may not be anymore.

**Domains that contain scam/fake products should NOT be fetched**. These are in `DomainSupported` not supported list.
Feel free to suggest possible improvements and new ideas!