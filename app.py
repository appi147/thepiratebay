import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template


APP = Flask(__name__)


@APP.route('/', methods=['GET'])
def index():
    return render_template('index.html'), 200


@APP.route('/recent/', methods=['GET'])
def recent_torrents():
    data = requests.get('https://thepiratebay.org/recent').text
    soup = BeautifulSoup(data, 'lxml')
    # title of torrents
    titleList = soup.find_all(class_='detLink')
    titles = []
    for title in titleList:
        titles.append(title.get_text())
    # magnet links of torrents
    magnetList = soup.find('table', {'id': 'searchResult'}).find_all('a', href=True)
    magnets = []
    for magnet in magnetList:
        if 'magnet' in magnet['href']:
            magnets.append(magnet['href'])
    # time, size and uploader
    times = []
    sizes = []
    uploaders = []
    description = soup.find_all('font', class_='detDesc')
    for desc in description:
        temp = desc.get_text().split(',')
        times.append(temp[0].replace(u'\xa0', u' ').replace('Uploaded ', ''))
        sizes.append(temp[1].replace(u'\xa0', u' ').replace(' Size ', ''))
        uploaders.append(temp[2].replace(' ULed by ', ''))
    # seeders and leechers
    slinfo = soup.find_all('td', {'align': 'right'})
    seederList = slinfo[::2]
    leecherList = slinfo[1::2]
    seeders = []
    leechers = []
    for seeder in seederList:
        seeders.append(seeder.get_text())
    for leecher in leecherList:
        leechers.append(leecher.get_text())
    # torrents
    torrents = []
    for (title, magnetLink, time, size, uploader, seed, leech) in zip(titles, magnets, times, sizes, uploaders, seeders, leechers):
        torrents.append({
            'title': title,
            'magnet': magnetLink,
            'time': time,
            'size': size,
            'uploader': uploader,
            'seeds': seed,
            'leechs': leech,
        })
    return jsonify(torrents)


if __name__ == '__main__':
    APP.run()
