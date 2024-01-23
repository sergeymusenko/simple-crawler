# simple-crawler

**Simple website crawler** to get all URLs, Meta tags and &lt;H1> from your web site.

Open `main.py` and set up `init_url` variable with you start URL.<br/>
Adjust `use_pause` variable so do not abuse your web server.<br/>
Crawler does not go by redirections (check `allow_redirects=False`).<br/>
Ignores React/JavaScript links if web site uses them.

In Python. Using BeautifulSoup. Saves report in CSV file.

https://github.com/sergeymusenko/simple-crawler/tree/main

**Installation:**
> `pip install bs4`
