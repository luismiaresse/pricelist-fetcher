## Ways to contribute to this project

### Adding a domain

#### Domain dictionary structure
`domains.json` contains dictionaries for specific domains, top-level domains (TLDs) for each domain and attributes for each TLD.
These are needed to find text for a specific attribute. Here is where you can add a new domain.

```
domains.json
├── domain0
│   ├── tld0
│   │   ├── attribute0
│   │   │   ├── element[elem0, elem1, ...]
│   │   │   │
│   │   │   ├── attribute[attr0, attr1, ...]
│   │   │   │
│   │   │   ├── name[name0, name1, ...]
│   │   │   │
│   │   │   └ ... (other components and flags)
│   │   │
│   │   ├── attribute1
│   │   │   ├── ...
│   │   │   ...
│   │   ...
│   │   
│   ├── tld1
│   │   ├── ...
│   │   ...
│   ...
│
├── domain1
│   ├── ...
│   ...
...
```

The best way to add support for a domain is as follows:

1. Check that the desired attributes are listed in `AttributeInfo`.
2. Fork this project and add the domain to `DomainInfo`. If a page detects the script as a bot, or any specific checks should be made, try to fix it with `preconditions()`. 
3. Inspect the page HTML and look for at least three HTML components: `element`, `attribute` and `name`.
For instance: to find `<h2 class="oBOnKe">Text I really want</h2>`, `h2` is the `element`, `class` the `attribute` and `oBOnKe` the `name`.
For elements without attributes defined, you can leave attribute and name as `null`. \
If the attribute cannot be fetched as it repeats, or changes across different states (i.e. discounted price instead of regular price),
previously grab the innermost container of that attribute that is not repeated, and set the `ISCONTAINER` flag to `true`. 
This will focus the scope on where the attribute should be looked for.
4. Check different products which may modify the position, state or even presence of the attribute you are looking for and adjust the components in the previous step.
If an element is preferable over another, it should be closer to the start of the list.
5. Add an URL to a product to `testURLs` to keep checking it in the future. It is preferable to be a discounted or unavailable product,
even if in the future it may not be anymore.

**Domains that contain scam/fake products should NOT be added**, such as fake sneakers sites.
These should be added to `config/blacklist.json`, along with the affected TLDs and the reason for blacklisting.

### Fix a previously working domain

Any of the added domains are subject to change, thus breaking functionality such as fetching an attribute
or even entering the page. If a domain is not working anymore (checkable sometimes with `testURLs` and `pytest`),
fork the project and try to resolve it, or open an issue with label `bug`.

