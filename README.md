# thepiratebay API

This is unofficial API of thepiratebay.org. It is currently hosted on Heroku and returns JSON data. It uses Flask framework to display the results and Beautifulsoup for parsing the data. 

## Current Features

### Recent torrents

Recent torrents can be accessed through the `/recent/page_number/` endpoint.

### Search

Search can be accessed through the `/search/search_term/page_number/` endpoint.

### Top torrents

Top torrents can be accessed through the `/top/category_code/` endpoint. Category code can be found in `/top/`.

### Top(48h) torrents

Top torrents for last 48hours can be accessed through the `/top48h/category_code/` endpoint. Category code can be found in `/top48h/`.

**Contributions are welcome**
