'''
This is the main module
'''
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template


APP = Flask(__name__)
EMPTY_LIST = []

BASE_URL = 'https://thepiratebay.org/'


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
    if cat == 0:
        url = BASE_URL + 'top/' + 'all/'
    else:
        url = BASE_URL + 'top/' + str(cat)
    return jsonify(parse_page(url)), 200


@APP.route('/top48h/<int:cat>/', methods=['GET'])
def top48h_torrents(cat=0):
    '''
    Returns top torrents last 48 hrs
    '''
    if cat == 0:
        url = BASE_URL + 'top/48h' + 'all/'
    else:
        url = BASE_URL + 'top/48h' + str(cat)
    return jsonify(parse_page(url)), 200


@APP.route('/recent/', methods=['GET'])
@APP.route('/recent/<int:page>/', methods=['GET'])
def recent_torrents(page=0):
    '''
    This function implements recent page of TPB
    '''
    url = BASE_URL + 'recent/' + str(page)
    return jsonify(parse_page(url)), 200


@APP.route('/search/', methods=['GET'])
def default_search():
    '''
    Default page for search
    '''
    return "No search term entered<br/>Format for search: /search/search_term/page_no(optional)/"


@APP.route('/search/<term>/', methods=['GET'])
@APP.route('/search/<term>/<int:page>/', methods=['GET'])
def search_torrents(term=None, page=0):
    '''
    Searches TPB using the given term. If no term is given, defaults to recent.
    '''
    url = BASE_URL + 'search/' + str(term) + '/' + str(page)
    return jsonify(parse_page(url)), 200


def parse_page(url):
    '''
    This function parses the page and returns list of torrents
    '''
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'lxml')
    table_present = soup.find('table', {'id': 'searchResult'})
    if table_present is None:
        return EMPTY_LIST
    titles = parse_titles(soup)
    magnets = parse_magnet_links(soup)
    times, sizes, uploaders = parse_description(soup)
    seeders, leechers = parse_seed_leech(soup)
    cat, subcat = parse_cat(soup)
    torrents = []
    for torrent in zip(titles, magnets, times, sizes, uploaders, seeders, leechers, cat, subcat):
        torrents.append({
            'title': torrent[0],
            'magnet': torrent[1],
            'time': torrent[2],
            'size': torrent[3],
            'uploader': torrent[4],
            'seeds': torrent[5],
            'leechs': torrent[6],
            'category': torrent[7],
            'subcat': torrent[8],
        })
    return torrents


def parse_magnet_links(soup):
    '''
    Returns list of magnet links from soup
    '''
    magnets = soup.find('table', {'id': 'searchResult'}).find_all('a', href=True)
    magnets = [magnet['href'] for magnet in magnets if 'magnet' in magnet['href']]
    return magnets


def parse_titles(soup):
    '''
    Returns list of titles of torrents from soup
    '''
    titles = soup.find_all(class_='detLink')
    titles[:] = [title.get_text() for title in titles]
    return titles


def parse_description(soup):
    '''
    Returns list of time, size and uploader from soup
    '''
    description = soup.find_all('font', class_='detDesc')
    description[:] = [desc.get_text().split(',') for desc in description]
    times, sizes, uploaders = map(list, zip(*description))
    times[:] = [time.replace(u'\xa0', u' ').replace('Uploaded ', '') for time in times]
    sizes[:] = [size.replace(u'\xa0', u' ').replace(' Size ', '') for size in sizes]
    uploaders[:] = [uploader.replace(' ULed by ', '') for uploader in uploaders]
    return times, sizes, uploaders


def parse_seed_leech(soup):
    '''
    Returns list of numbers of seeds and leechs from soup
    '''
    slinfo = soup.find_all('td', {'align': 'right'})
    seeders = slinfo[::2]
    leechers = slinfo[1::2]
    seeders[:] = [seeder.get_text() for seeder in seeders]
    leechers[:] = [leecher.get_text() for leecher in leechers]
    return seeders, leechers


def parse_cat(soup):
    '''
    Returns list of category and subcategory
    '''
    cat_subcat = soup.find_all('center')
    cat_subcat[:] = [c.get_text().replace('(', '').replace(')', '').split() for c in cat_subcat]
    cat = [cs[0] for cs in cat_subcat]
    subcat = [' '.join(cs[1:]) for cs in cat_subcat]
    return cat, subcat


if __name__ == '__main__':
    APP.run()
