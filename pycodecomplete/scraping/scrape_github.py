import os
import sys
from argparse import ArgumentParser
import json
import requests
import graphene
import pandas as pd


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
 
    data_dict = json.loads(r.text)

    data_df = parse_results(data_dict['data']['search']['edges'])

    data_df.to_csv('repo_list.csv')

def json_query():
    return {'query': '''{
  search(query: "stars:>1000 language:Python", type: REPOSITORY, first: 10) {
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
}'''}


def header(api_token):
    return {'Authorization': 'token %s' % api_token}


def apiurl():
    return 'https://api.github.com/graphql'

def parse_results(edge_list):
    data_list = [pd.DataFrame.from_dict(e['node'], orient='index').T for e in edge_list]
    result = pd.concat(data_list, axis=0)
    result.index = range(result.shape[0])
    result['owner'] = result['owner'].apply(lambda x: x['login'])
    result['stargazers'] = result['stargazers'].apply(lambda x: x['totalCount'])
    result['watchers'] = result['watchers'].apply(lambda x: x['totalCount'])
    return(result)

def clone_repos(to_path, repos_df):
    for repo in repos_df:
        print(repo['name'],repo['url'])

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