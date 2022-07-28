# PriceList fetcher
A Python script that fetches information (name, brand, price, ...) about a product 

### Dependencies
* python 3.10+
* pip

The following Python packages can be autoinstalled by executing `pip install -r requirements.txt`:
* selenium
* undetected_chromedriver
* bs4 (BeautifulSoup)

### Usage
This tool uses a command-line interface that receives the desired URL as argument and other flags
It can be executed by typing:

#### Linux
`$ python pricelist.py [OPTIONS] URL` \
or \
`$ ./pricelist [OPTIONS] URL` \
in the shell of your liking

#### Windows
`> python pricelist.py [OPTIONS] URL` \
or \
`> .\pricelist.exe [OPTIONS] URL` \
in CMD or Powershell

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
2. Inspect the page HTML and look for at least three HTML components: `element`, `attribute` and `name`.
For instance: to find `<h2 class="oBOnKe">Text I really want</h2>`, `h2` is the `element`, `class` the `attribute` and `oBOnKe` the `name`. \
If the attribute cannot be fetched as it repeats, or changes across different states (i.e. discounted price instead of regular price),
grab the innermost container that is not repeated, and set the `ISCONTAINER` flag to `true`. This will focus the scope on where the attribute should be.
3. Check different products which may modify the position, state or even presence of the attribute you are looking for and adjust the components in the previous step.
If an element is sometimes present and is preferable over another, it should be closer to the start of the list.
4. Add the domain to `DomainSupported` partially supported if there is no possible way to extract an attribute.

Domains that contain scam/fake products should NOT be fetched. These are in `DomainSupported` not supported list.
Feel free to suggest possible improvements and new ideas!