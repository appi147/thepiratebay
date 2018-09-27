# thepiratebay API

This is unofficial API of thepiratebay.org. It is currently hosted on Heroku and returns JSON data. It uses Flask framework to display the results and Beautifulsoup for parsing the data. 

## Current Features

### Sort filters

On `top` and `search` queries, results can be sorted by using the `sort` GET parameter.

Example: `http://<api-address>/top/?sort=title_asc`

|Value|Filter|
|---|---|
|`title_asc`|Torrent names A-Z|
|`title_desc`|Torrent names Z-A|
|`seeds_asc`|Seed count low-high|
|`seeds_desc`|Seed count high-low|
|`leeches_asc`|Leech count low-high|
|`leeches_desc`|Leech count high-low|
|`time_asc`|Upload date old-recent|
|`time_desc`|Upload date recent-old|
|`uploader_asc`|Uploader username A-Z|
|`uploader_desc`|Uploader username Z-A|
|`size_asc`|Filesize low-high|
|`size_desc`|Filesize high-low|
|`category_asc`|Filetype A-Z|
|`category_desc`|Filetype Z-A|

### Recent torrents

Recent torrents can be accessed through the `/recent/page_number/` endpoint.

### Search

Search can be accessed through the `/search/search_term/page_number/` endpoint.

### Top torrents

Top torrents can be accessed through the `/top/category_code/` endpoint. Category code can be found in `/top/`.

### Top(48h) torrents

Top torrents for last 48hours can be accessed through the `/top48h/category_code/` endpoint. Category code can be found in `/top48h/`.

**Contributions are welcome**

#### Running with Docker
```bash
# Assuming you have docker on your machine this should work
docker build -t pirate-bay .
docker container run -e "BASE_URL=https://thepiratebay.asia/" -p 5000:5000 --name pirateBay pirate-bay
```
