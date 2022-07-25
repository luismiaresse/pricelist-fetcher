# PriceList fetcher
A python script that fetches information about products across many websites  

### Dependencies
* python 3.10+
* pip

The following Python packages can be autoinstalled by executing <code> pip install -r requirements.txt</code>:
* selenium
* undetected_chromedriver
* bs4 (BeautifulSoup)
* pytest

### Dictionary structure
```
domains
├── domain0
│   ├── attribute0
│   │   ├── html-element: list
│   │   │   ├── element[0]
│   │   │   ...
│   │   │   └── element[LIST_MAX-1]
│   │   │
│   │   ├── html-attribute: list
│   │   │   ├── attribute[0]
│   │   │   ...
│   │   │   └── attribute[LIST_MAX-1]
│   │   │
│   │   └── html-name: list
│   │       ├── name[0]
│   │       ...
│   │       └── name[LIST_MAX-1]
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

