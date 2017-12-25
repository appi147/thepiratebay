'''
This is the main module
'''
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template


APP = Flask(__name__)
EMPTY_LIST = []


@APP.route('/', methods=['GET'])
def index():
    '''
    This is the home page and contains links to other API
    '''
    return render_template('index.html'), 200


@APP.route('/recent/', methods=['GET'])
@APP.route('/recent/<int:page>/', methods=['GET'])
def recent_torrents(page=0):
    '''
    This function implements recent page of TPB
    '''
    url = 'https://thepiratebay.org/recent/' + str(page)
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
    torrents = []
    categories, subcategories = parse_category(soup)

    for torrent in zip(titles, magnets, times, sizes, uploaders, seeders, leechers, categories, subcategories):
        torrents.append({
            'title': torrent[0],
            'magnet': torrent[1],
            'time': torrent[2],
            'size': torrent[3],
            'uploader': torrent[4],
            'seeds': torrent[5],
            'leechs': torrent[6],
            'category': torrent[7],
            'subcategory': torrent[8],
        })
    return torrents


def parse_magnet_links(soup):
    '''
    Returns list of magnet links from soup
    '''
    magnet_list = soup.find('table', {'id': 'searchResult'}).find_all('a', href=True)
    magnets = []
    for magnet in magnet_list:
        if 'magnet' in magnet['href']:
            magnets.append(magnet['href'])
    return magnets


def parse_titles(soup):
    '''
    Returns list of titles of torrents from soup
    '''
    title_list = soup.find_all(class_='detLink')
    titles = []
    for title in title_list:
        titles.append(title.get_text())
    return titles


def parse_description(soup):
    '''
    Returns list of time, size and uploader from soup
    '''
    description = soup.find_all('font', class_='detDesc')
    times = []
    sizes = []
    uploaders = []
    for desc in description:
        temp = desc.get_text().split(',')
        times.append(temp[0].replace(u'\xa0', u' ').replace('Uploaded ', ''))
        sizes.append(temp[1].replace(u'\xa0', u' ').replace(' Size ', ''))
        uploaders.append(temp[2].replace(' ULed by ', ''))
    return times, sizes, uploaders


def parse_seed_leech(soup):
    '''
    Returns list of numbers of seeds and leechs from soup
    '''
    slinfo = soup.find_all('td', {'align': 'right'})
    seeder_list = slinfo[::2]
    leecher_list = slinfo[1::2]
    seeders = []
    leechers = []
    for seeder in seeder_list:
        seeders.append(seeder.get_text())
    for leecher in leecher_list:
        leechers.append(leecher.get_text())
    return seeders, leechers


def parse_category(soup):
    '''
    Returns list of category and subcategory from soup
    '''
    categories = []
    subcategories = []
    regex = r'(\w+)\s*\(([\w\s\-\(\)]+)\)'
    cats = soup.find_all('td', {'class': 'vertTh'})
    for cat in cats:
        found = re.search(regex, cat.text.strip())
        if found:
            categories.append(found.group(1))
            subcategories.append(found.group(2))
    return categories, subcategories


if __name__ == '__main__':
    APP.run()
