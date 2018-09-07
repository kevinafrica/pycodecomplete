# -*- coding: utf-8 -*-
"""scrape_github.py

This module takes three arguments, a GutHub API Token, a destination path
and a number of repositories to clone, and clones all the repositories to 
the specified path.

Example:

    To clone 1000 Python repositories run the following the command:

     $ python scrape_github.py -f /github/token/file /cloned/repos/destination/folder 1000

    or, with a token string:

     $ python scrape_github.py -t 123456789abcdefghi /cloned/repos/destination/folder 1000

Attributes:
    None

Todo:
    * 
"""
import os
import sys
from argparse import ArgumentParser
import json
import requests
import math
import pandas as pd

from git import Repo


def main():
    parser = ArgumentParser(description='Github scraper')
    parser.add_argument('destination', action='store',
                        help='Destination folder for the scraped GitHub repositories')
    parser.add_argument('count', action='store', type=int,
                        help='Maximum number of repos to clone')
    parser.add_argument('-t', action='store', dest='token_string',
                        help='GitHub API OAuth token')
    parser.add_argument('-f', action='store', dest='token_file',
                        help='File containing GitHub API OAuth token')

    settings = parser.parse_args()

    if settings.token_file:
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
    elif settings.token_string:
        token = settings.token_string


    repos_df = df_from_query(token, settings.count, batch_size=100)
    repos_df.to_csv('repo_list.csv')

    clone_repos_from_df(settings.destination, repos_df)


def json_query(batch_size, after_cursor=''):
    '''The GraphQL Query to obtain all relevant meta data from Python
    repositories'''
    return {'query': '''{
  search(query: "stars:>1000 language:Python", type: REPOSITORY, first: %d, %s) {
      pageInfo {
      hasNextPage
      endCursor
      startCursor
    }
    repositoryCount
    edges {
      node {
        ... on Repository {
          name
          owner {
            login
          }
          nameWithOwner
          diskUsage
          homepageUrl
          mirrorUrl
          projectsUrl
          resourcePath
          sshUrl
          url
          forkCount
          stargazers {
            totalCount
          }
          watchers {
            totalCount
          }
        }
      }
    }
  }
}''' % (batch_size, after_cursor)}


def header(api_token):
    '''Header for GraphQL Query'''
    return {'Authorization': 'token %s' % api_token}

def apiurl():
    '''URL for the GitHub GraphQL API''' 
    return 'https://api.github.com/graphql'


def df_from_query(token, n, batch_size=10):
    '''Create a Pandas dataframe from the result of a Query. Since the limit
    for results is 100 per page. While there are next pages available, iterate
    through each page and append those results to the dataframe.

    Args:
        token (String): The user's GitHub OAuth token
        n (int): Number of repositiories to clone
        batch_size (int): Size of the batches to clone the repositories in

    Returns:
        dataframe: Dataframe containing the query results
    '''
    i = 0
    n_batches = math.ceil(n / float(batch_size))
    hasNextPage = True
    end_Cursor = ''
    data_list = []

    while hasNextPage and i < n_batches:

        if batch_size > n:
            batch_size = n
            
        json_result = requests.post(apiurl(),
                                         json=json_query(batch_size, end_Cursor),
                                         headers=header(token))

        data_dict = json.loads(json_result.text)
        edge_list = data_dict['data']['search']['edges']
        hasNextPage = data_dict['data']['search']['pageInfo']['hasNextPage']
        end_Cursor = 'after: "%s"' % (data_dict['data']['search']['pageInfo']['endCursor'])

        data_list.extend([pd.DataFrame.from_dict(
            e['node'], orient='index').T for e in edge_list])

        i += 1
        n -= batch_size

    result = pd.concat(data_list, axis=0)
    result.index = range(result.shape[0])
    result['owner'] = result['owner'].apply(lambda x: x['login'])
    result['stargazers'] = result['stargazers'].apply(
        lambda x: x['totalCount'])
    result['watchers'] = result['watchers'].apply(
        lambda x: x['totalCount'])

    return result


def clone_repos_from_df(to_path, repos_df):
    '''Clone all the repositories from the dataframe to a specified path

    Args:
        to_path (String): The path to clone the repositories to
        repos_df (dataframe): The dataframe containing repository metadata

    Returns:
        None
    '''
    n = repos_df.shape[0]
    for i, row in repos_df.iterrows():
        path = os.path.join(to_path, row['nameWithOwner'])
        print('Cloning repo %d/%d to %s' % (i+1, n, path))
        Repo.clone_from(row['url'], path)

        # Delete non-.py files
        for root, dirs, files in os.walk(path):
            for name in files:
                if not name.endswith(('.py')):
                    os.remove(os.path.join(root, name))


if __name__ == '__main__':
    main()
