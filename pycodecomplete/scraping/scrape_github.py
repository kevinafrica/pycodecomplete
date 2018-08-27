import os
import sys
from argparse import ArgumentParser
import json
import requests
import graphene
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
        token = token_string

    r = requests.post(apiurl(),
                      json=json_query(settings.count),
                      headers=header(token))

    data_dict = json.loads(r.text)

    repos_df = parse_results(data_dict['data']['search']['edges'])

    repos_df.to_csv('repo_list.csv')

    clone_repos(settings.destination, repos_df)


def json_query(count):
    return {'query': '''{
  search(query: "stars:>1000 language:Python", type: REPOSITORY, first: %d) {
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
}''' % (count)}


def header(api_token):
    return {'Authorization': 'token %s' % api_token}


def apiurl():
    return 'https://api.github.com/graphql'


def parse_results(edge_list):
    data_list = [pd.DataFrame.from_dict(
        e['node'], orient='index').T for e in edge_list]
    result = pd.concat(data_list, axis=0)
    result.index = range(result.shape[0])
    result['owner'] = result['owner'].apply(lambda x: x['login'])
    result['stargazers'] = result['stargazers'].apply(
        lambda x: x['totalCount'])
    result['watchers'] = result['watchers'].apply(lambda x: x['totalCount'])
    return(result)


def clone_repos(to_path, repos_df):
    n = repos_df.shape[0]
    for i, row in repos_df.iterrows():
        path = os.path.join(to_path, row['name'])
        print('Cloning repo %d/%d to %s' % (i+1, n, path))
        Repo.clone_from(row['url'], path)

if __name__ == '__main__':
    main()


'''{
  search(query: "stars:>1000 language:Python", type: REPOSITORY, first: 10) {
    repositoryCount
    edges {
      node {
        ... on Repository {
          nameWithOwner
          diskUsage
          homepageUrl
          mirrorUrl
          projectsUrl
          resourcePath
          sshUrl
          url
        }
      }
    }
  }
}'''

"""{'query':
    '''{
          viewer { 
            repositories(first: 1) {
                totalCount pageInfo {
                  hasNextPage endCursor 
                }
                edges { 
                  node { 
                    name
                  }
                }
            }
        } 
        }'''}"""
