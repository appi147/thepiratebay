import requests
import time
import app

# List of category codes for sequential endpoint testing
CATEGORY_MAP = [
  100, 101, 102, 103, 104, 199, 200, 201, 202,
  203, 204, 205, 206, 207, 208, 209, 299, 300,
  301, 302, 303, 304, 305, 306, 399, 400, 401,
  402, 403, 404, 405, 406, 407, 408, 499, 500,
  501, 502, 503, 504, 505, 506, 599, 600, 601,
  602, 603, 604, 605, 699
]


def test_date_conv():
    '''
    Tests date conversion from string to datetime.
    '''
    test_strings = [
        '01-01 10:00',
        'Today 10:00',
        '1 min ago',
        '3 mins ago',
        '2016-01-01',
        'Y-day 10:00'
    ]

    passed, failed = 0, 0
  
    print('DATE CONVERSION')

    for test_str in test_strings:
        try:
            print('{} -> {}'.format(test_str, app.convert_to_date(test_str)))
            passed += 1
        except:
            print('FAILED: {}'.format(test_str))
            failed += 1

    print('{} PASSED, {} FAILED\n'.format(passed, failed))


def test_size_conv():
    '''
    Tests string to float conversions for sizes.
    '''
    test_strings = [
        '50 PiB',
        '45 TiB',
        '4.3 EiB',
        '1.0 GiB',
        '100 MiB',
        '50 KiB',
        '5 B'
    ]

    passed, failed = 0, 0

    print('SIZE CONVERSION')

    for test_str in test_strings:
        try:
            print('{} -> {}'.format(test_str, app.convert_to_bytes(test_str)))
            passed += 1
        except:
            print('FAILED: {}'.format(test_str))
            failed += 1

    print('{} PASSED, {} FAILED\n'.format(passed, failed))


def test_recent_endpoints(api_base):
    '''
    Tests all the variations of /recent/ and verifies that a 200 response occurs.
    This filters out critical errors.
    '''
    URL = api_base + 'recent/'

    passed, failed = 0, 0

    print('/recent ENDPOINT')

    for sort_filter in app.sort_filters:
        try:
            full_url = URL + '?sort={}'.format(sort_filter)
            resp = requests.get(full_url)
            print('{} -> {}'.format(full_url , resp.status_code))
            passed = passed + 1 if resp.status_code == 200 else passed
            failed = failed + 1 if resp.status_code != 200 else failed

        except:
            print('FAILED: {}'.format(full_url))
            failed += 1
        time.sleep(1)

    print('{} PASSED, {} FAILED\n'.format(passed, failed))


def test_top_endpoints(api_base):
    '''
    Tests all the variations of /top/<category> and verifies that a 200 response occurs.
    This filters out critical errors.
    '''
    URL = api_base + 'top/'

    passed, failed = 0, 0

    print('/top ENDPOINT')

    for sort_filter in app.sort_filters:
        for category in CATEGORY_MAP:
            try:
                full_url = URL + '{}/'.format(category) + '?sort={}'.format(sort_filter)
                resp = requests.get(full_url)
                print('{} -> {}'.format(full_url , resp.status_code))
                passed = passed + 1 if resp.status_code == 200 else passed
                failed = failed + 1 if resp.status_code != 200 else failed

            except:
                print('FAILED: {}'.format(full_url))
                failed += 1
                time.sleep(1)

    print('{} PASSED, {} FAILED\n'.format(passed, failed))


if __name__ == '__main__':
    test_date_conv()
    test_size_conv()

    local_api_base = 'http://127.0.0.1:5000/'

    test_recent_endpoints(local_api_base)
    test_top_endpoints(local_api_base)