# NewsScrapers

## Instructions to Run

### Prerequisite:

API-Key to access the Readability-API, which is avaiable once signed-up with personal account

```https://mercury.postlight.com/web-parser/```

Note:
*This key should be preserved, and NOT sharable.*

### Run the following commands to prepare for NewsScraper

```bash
$ sudo apt-get install python3-pip
$ sudo pip install virtualenv
```

Create and activate the virtual environment for NewsScraper

```bash
$ cd NewsScrapers
$ virtualenv -p /usr/bin/python3 venv
$ source venv/bin/activate
```

Install all the necessary dependencies for running NewsScraper

```bash
$ pip3 install -r requirements-install.txt
```

### Run News Scraper to scrape the articles

Before running newspider, set the Readability API Key to ENV Variable

```bash
$ echo READ_API_KEY=<READABILITY-API-KEY>
$ cd news_scraper/
$ scrapy runspider newspider.py -a readability_api_key="$(echo $READ_API_KEY)"
```


### Search for articles based on keywords

```bash
$ python -m search_articles --help
usage: search_articles.py [-h] -f {title,keywords,author,excerpt} -s
                          SEARCH_TERM [-l LIMIT] [-d DUMP_DIR]

optional arguments:
  -h, --help            show this help message and exit
  -f {title,keywords,author,excerpt}, --search-field {title,keywords,author,excerpt}
                        Field to use for search term. default=None
  -s SEARCH_TERM, --search-term SEARCH_TERM
                        Term to search in the document. default=None
  -l LIMIT, --limit LIMIT
                        Limit the number of results. Default=10
  -d DUMP_DIR, --dump-dir DUMP_DIR
                        Destination directory to dump theretrieved results.
                        Default=/tmp
```

#### Search by title, keyword, and author
```bash
$ python -m search_articles --search-field title --search-term Australia
$ python -m search_articles --search-field keyword --search-term NHS
$ python -m search_articles --search-field keywords --search-term Sports
```

#### Search and Dump the documents to custom directory
```bash
$ mkdir ./scraped_docs
$ python -m search_articles --search-field title --search-term Australia --dump-dir ./scraped
```
The files are written to ./Scraped directory as JSON files
