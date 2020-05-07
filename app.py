'''
This is the main module
'''
import os

import requests
import re
import time
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

APP = Flask(__name__)
CORS(APP)
EMPTY_LIST = []

BASE_URL = os.getenv('BASE_URL', 'https://thepiratebay.org/')
HOST_URL = os.getenv('HOST_URL', 'http://0.0.0.0:4444/wd/hub')

JSONIFY_PRETTYPRINT_REGULAR = True

# Translation table for sorting filters
sort_filters = {
    'title_asc': 1,
    'title_desc': 2,
    'time_desc': 3,
    'time_asc': 4,
    'size_desc': 5,
    'size_asc': 6,
    'seeds_desc': 7,
    'seeds_asc': 8,
    'leeches_desc': 9,
    'leeches_asc': 10,
    'uploader_asc': 11,
    'uploader_desc': 12,
    'category_asc': 13,
    'category_desc': 14
}


@APP.route('/', methods=['GET'])
def index():
    '''
    This is the home page and contains links to other API
    '''
    return render_template('index.html'), 200


@APP.route('/top/', methods=['GET'])
@APP.route('/top48h/', methods=['GET'])
def default_top():
    '''
    Returns default page with categories
    '''
    return render_template('top.html'), 200


@APP.route('/top/<int:cat>/', methods=['GET'])
def top_torrents(cat=0):
    '''
    Returns top torrents
    '''

    sort = request.args.get('sort')
    sort_arg = sort if sort in sort_filters else ''
    if cat == 0:
    	url = BASE_URL + 'search.php?q=top100:all'
    else:
        url = BASE_URL + 'search.php?q=top100:' + str(cat)
    return jsonify(parse_page(url, sort=sort_arg)), 200


@APP.route('/top48h/<int:cat>/', methods=['GET'])
def top48h_torrents(cat=0):
    '''
    Returns top torrents last 48 hrs
    '''

    sort = request.args.get('sort')
    sort_arg = sort if sort in sort_filters else ''

    if cat == 0:
        url = BASE_URL + 'search.php?q=top100:48h'
    else:
        url = BASE_URL + 'search.php?q=top100:48h_' + str(cat)

    return jsonify(parse_page(url, sort=sort_arg)), 200


@APP.route('/recent/', methods=['GET'])
def recent_torrents():
    '''
    This function implements recent page of TPB
    '''
    sort = request.args.get('sort')
    sort_arg = sort if sort in sort_filters else ''

    url = BASE_URL + 'search.php?q=top100:recent'
    return jsonify(parse_page(url, sort=sort_arg)), 200


@APP.route('/api-search/', methods=['GET'])
def api_search():
    query = request.query_string.decode('utf-8')
    if not query:
      return 'No search term entered<br/>Format for api-search: /api-search/?q=<search_term>'

    url = BASE_URL + 'search.php?q=' + query
    return jsonify(parse_page(url)), 200


@APP.route('/search/', methods=['GET'])
def default_search():
    '''
    Default page for search
    '''
    return 'No search term entered<br/>Format for search: /search/search_term/page_no(optional)/'


@APP.route('/search/<term>/', methods=['GET'])
def search_torrents(term=None):
    '''
    Searches TPB using the given term. If no term is given, defaults to recent.
    '''

    sort = request.args.get('sort')
    sort_arg = sort_filters[request.args.get('sort')] if sort in sort_filters else ''

    url = BASE_URL + 'search/' + str(term)
    return jsonify(parse_page(url)), 200


def parse_page(url, sort=None):
    
    driver = webdriver.Remote(HOST_URL, DesiredCapabilities.CHROME)
    
    driver.get(url)
    delay = 30 # seconds
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID,'torrents')))
        soup = BeautifulSoup(driver.page_source, 'lxml')
    except TimeoutException:
        return "Could not load search results!"
    
    '''
    This function parses the page and returns list of torrents
    '''
    titles = parse_titles(soup)
    links = parse_links(soup)
    magnets = parse_magnet_links(soup)
    uploaders = parse_uploaders(soup)
    sizes = parse_sizes(soup)
    times = parse_times(soup)
    seeders, leechers = parse_seed_leech(soup)
    cat, subcat = parse_cat(soup)
    torrents = []
    for torrent in zip(titles, magnets, times, sizes, uploaders, seeders, leechers, cat, subcat, links):
        torrents.append({
            'title': torrent[0],
            'magnet': torrent[1],
            'time': convert_to_date(torrent[2]),
            'size': convert_to_bytes(torrent[3]),
            'uploader': torrent[4],
            'seeds': int(torrent[5]),
            'leeches': int(torrent[6]),
            'category': torrent[7],
            'subcat': torrent[8],
            'id': torrent[9],
        })

    if sort:
        sort_params = sort.split('_')
        torrents = sorted(torrents, key=lambda k: k.get(sort_params[0]), reverse=sort_params[1].upper() == 'DESC')

    return torrents


def parse_magnet_links(soup):
    '''
    Returns list of magnet links from soup
    '''
    magnets = soup.find('ol', {'id': 'torrents'}).find_all('a', href=True)
    magnets = [magnet['href'] for magnet in magnets if 'magnet' in magnet['href']]
    return magnets


def parse_titles(soup):
    '''
    Returns list of titles of torrents from soup
    '''
    titles = soup.find_all(class_='list-item item-name item-title')
    titles[:] = [title.get_text() for title in titles]
    return titles


def parse_links(soup):
    '''
    Returns list of links of torrents from soup
    '''
    links = soup.find_all(class_='list-item item-name item-title')
    links = [link.find_all('a', href=True) for link in links ]
    links[:] = [link[0]['href'] for link in links]
    return links


def parse_sizes(soup):
    '''
    Returns list of size from soup
    '''
    sizes = soup.find_all(class_='list-item item-size')
    sizes[:] = [size.get_text() for size in sizes]

    return sizes

	
def parse_times(soup):
    '''
    Returns list of time from soup
    '''
    times = soup.find_all(class_='list-item item-uploaded')
    times[:] = [time.get_text() for time in times]

    return times


def parse_uploaders(soup):
    '''
    Returns list of uploader from soup
    '''
    uploaders = soup.find_all(class_='list-item item-user')
    uploaders[:] = [uploader.get_text() for uploader in uploaders]

    return uploaders


def parse_seed_leech(soup):
    '''
    Returns list of numbers of seeds and leeches from soup
    ''' 
    seeders = soup.find_all(class_='list-item item-seed')
    seeders[:] = [seeder.get_text() for seeder in seeders]

    leechers = soup.find_all(class_='list-item item-leech')
    leechers[:] = [leecher.get_text() for leecher in leechers]

    return seeders, leechers


def parse_cat(soup):
    '''
    Returns list of category and subcategory
    '''
    cat_subcat = soup.find_all(class_='list-item item-type')
    cat = [cat.find_all('a', href=True)[::2] for cat in cat_subcat ]
    subcat = [subcat.find_all('a', href=True)[1::2] for subcat in cat_subcat ]
    
    cat[:] = [c[0].get_text() for c in cat]
    subcat[:] = [s[0].get_text() for s in subcat]
    
    return cat, subcat


def convert_to_bytes(size_str):
    '''
    Converts torrent sizes to a common count in bytes.
    '''
    size_data = size_str.split()

    multipliers = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB']

    size_magnitude = float(size_data[0])
    multiplier_exp = multipliers.index(size_data[1])
    size_multiplier = 1024 ** multiplier_exp if multiplier_exp > 0 else 1

    return size_magnitude * size_multiplier


def convert_to_date(date_str):
    '''
    Converts the dates into a proper standardized datetime.
    '''
    date_format = None

    if re.search('^[0-9]+ min(s)? ago$', date_str.strip()):
        minutes_delta = int(date_str.split()[0])
        torrent_dt = datetime.now() - timedelta(minutes=minutes_delta)
        date_str = '{}-{}-{} {}:{}'.format(torrent_dt.year, torrent_dt.month, torrent_dt.day, torrent_dt.hour, torrent_dt.minute)
        date_format = '%Y-%m-%d %H:%M'

    elif re.search('^[0-9]*-[0-9]*\s[0-9]+:[0-9]+$', date_str.strip()):
        today = datetime.today()
        date_str = '{}-'.format(today.year) + date_str
        date_format = '%Y-%m-%d %H:%M'
    
    elif re.search('^Today\s[0-9]+\:[0-9]+$', date_str):
        today = datetime.today()
        date_str = date_str.replace('Today', '{}-{}-{}'.format(today.year, today.month, today.day))
        date_format = '%Y-%m-%d %H:%M'
    
    elif re.search('^Y-day\s[0-9]+\:[0-9]+$', date_str):
        today = datetime.today() - timedelta(days=1)
        date_str = date_str.replace('Y-day', '{}-{}-{}'.format(today.year, today.month, today.day))
        date_format = '%Y-%m-%d %H:%M'

    else:
        # date_format = '%m-%d %Y'
        date_format = '%Y-%m-%d'

    return datetime.strptime(date_str, date_format)
