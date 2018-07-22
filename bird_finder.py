import argparse
import requests
from requests_html import HTMLSession
import logging
import fileinput
import csv
from urllib.parse import urlparse

session = HTMLSession()


def find(url):
    try:
        r = session.get(url)
    except requests.exceptions.RequestException as e:
        logging.warning('{} errored with {}'.format(url, e))
        return
    if r.status_code != 200:
        logging.warning('{} returned {}'.format(url, r.status_code))
    try:
        for link in r.html.links:
            if (link.startswith('https://www.twitter.com/')
                    or link.startswith('http://www.twitter.com/')
                    or link.startswith('https://twitter.com/')
                    or link.startswith('http://twitter.com/')) \
                    and '/status/' not in link \
                    and '/intent/' not in link \
                    and '/search?' not in link \
                    and '/share?' not in link:
                yield url, link
    except ValueError as e:
        logging.warning('{} errored with {}'.format(url, e))


def find_files(files):
    for url in fileinput.input(files=files):
        for link in find(url.rstrip()):
            yield link


def ask(twitter_links):
    for url, twitter_link in twitter_links:
        cur_screen_name = screen_name(twitter_link)
        clean_screen_name = cur_screen_name[1:].lower()
        split_netloc = [part.lower() for part in urlparse(url).netloc.split('.')]
        if clean_screen_name in split_netloc \
                or clean_screen_name == '{}_{}'.format(split_netloc[-2], split_netloc[-1]) \
                or clean_screen_name == '{}{}'.format(split_netloc[-2], split_netloc[-1]):
            print('Skipping {} => {}'.format(url, cur_screen_name))
            yield url, twitter_link
        elif input('{} => {} [Yn]: '.format(url, cur_screen_name)).lower() in ('', 'y'):
            yield url, twitter_link


def screen_name(twitter_link):
    if twitter_link.endswith('/'):
        twitter_link = twitter_link[:-1]
    if '?' in twitter_link:
        twitter_link = twitter_link[:twitter_link.index('?')]
    name = twitter_link[twitter_link.rfind('/') + 1:]
    if name.startswith('@'):
        name = name[1:]
    return '@{}'.format(name)


def dedupe(twitter_links):
    existing_screen_names = set()
    for url, twitter_link in twitter_links:
        cur_screen_name = screen_name(twitter_link)
        if cur_screen_name not in existing_screen_names:
            existing_screen_names.add(cur_screen_name)
            yield url, twitter_link

if __name__ == '__main__':
    logging.basicConfig(filename='bird_finder.log')

    parser = argparse.ArgumentParser(description='Finds Twitter accounts in web pages.')
    parser.add_argument('--output', help='filename of csv output')
    parser.add_argument('--ask', help='ask about each twitter link', action='store_true')
    subparsers = parser.add_subparsers(dest='command')

    page_parser = subparsers.add_parser('page')
    page_parser.add_argument('url')

    pages_parser = subparsers.add_parser('pages')
    pages_parser.add_argument('files', metavar='FILE', nargs='*', help='files to read, if empty, stdin is used')

    args = parser.parse_args()

    if args.command == 'page':
        twitter_links = find(args.url)
    else:
        twitter_links = find_files(args.files if len(args.files) > 0 else ('-',))

    twitter_links = dedupe(twitter_links)

    if args.ask:
        twitter_links = ask(twitter_links)

    if args.output:
        with open(args.output, 'w') as out:
            csv_out = csv.writer(out)
            csv_out.writerow(['url', 'twitter_link', 'screen_name'])
            for url, twitter_link in twitter_links:
                csv_out.writerow([url, twitter_link, screen_name(twitter_link)])
    else:
        for url, twitter_link in twitter_links:
            print('{} => {} ({})'.format(url, screen_name(twitter_link), twitter_link))