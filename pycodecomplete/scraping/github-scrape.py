# -*- coding: utf-8 -*-
'''github-scrape.py

Version of GitHub scraper that collects repo metadata and stores them in a MongoDB

Example:

Attributes:
    None

Todo:
    *
'''
import sys
import pymongo


def mongo_collection(host='mongodb://localhost:27017/',
                     database='pycodecomplete_database',
                     collection='repos'):
    '''Return MongoDB repo collection'''

    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
    pycodecomplete_db = mongo_client['pycodecomplete_database']
    repo_col = pycodecomplete_db['repos']
    # Check if the MongoDB service is running
    try:
        mongo_client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(e)
        print('Start MongoDB with: sudo service mongod start')
        raise

    return mongo_client, pycodecomplete_db, repo_col


def main(argv):
    try:
        mongo_client, pycodecomplete_db, repo_col = mongo_collection()
    except Exception:
        sys.exit(0)

    repo_col.drop()


if __name__ == "__main__":
    main(sys.argv[1:])
