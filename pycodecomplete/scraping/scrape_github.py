import os
import sys
from argparse import ArgumentParser
import json
import requests
import graphene


def main():
    parser = ArgumentParser(description='Github scraper')
    parser.add_argument('destination', action='store',
                        help='Destination folder for the scraped GitHub repositories')
    parser.add_argument('-t', action='store', dest='token_file',
                        help='File containing GitHub API OAuth token')

    settings = parser.parse_args()

    try:
        with open(settings.token_file, 'r') as f:
            token = f.readline().strip()
    except FileNotFoundError:
        with open(os.path.normpath(settings.token_file), 'r') as f:
            token = f.readline().strip()
    except FileNotFoundError:
        with open(os.path.expanduser(settings.token_file), 'r') as f:
            token = f.readline().strip()
    except IsADirectoryError:
        print('error:', settings.token_file,
              'is not a valid GitHub token file')
        sys.exit()
    except FileNotFoundError:
        print('error:', settings.token_file, 'not found')
        sys.exit()

    print(json_query())

    r = requests.post(apiurl(),
                      json=json_query(),
                      headers=header(token))

    print(r.text)


def json_query():
    return {'query': '{ viewer { repositories(first: 30) { totalCount pageInfo { hasNextPage endCursor } edges { node { name } } } } }'}


def header(api_token):
    return {'Authorization': 'token %s' % api_token}


def apiurl():
    return 'https://api.github.com/graphql'


if __name__ == '__main__':
    main()
