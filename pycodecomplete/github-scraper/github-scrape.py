import pymongo

mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
pycodecomplete_db = mongo_client['pycodecomplete_database']
repo_col = pycodecomplete_db['repos']

mydict = { "name": "John", "address": "Highway 37" }

x = repo_col.insert_one(mydict)

def mongo_collection(host='mongodb://localhost:27017/',
                     database='pycodecomplete_database',
                     collection='repos'):
'''Return MongoDB repo collection'''
    mongo_client = pymongo.MongoClient('mongodb://localhost:27017/')
    pycodecomplete_db = mongo_client['pycodecomplete_database']
    repo_col = pycodecomplete_db['repos']
    #Check if the MongoDB service is running
    try:
        mongo_client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(e)
        print('Start MongoDB with: sudo service mongod start')
        raise    

    return repo_col
                    
def main(argv):
    pass

if __name__ == "__main__":
    main(sys.argv[1:])