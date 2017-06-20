# Run with python -i open_db.py

from pymongo import MongoClient
import os

def initialize_mongo_db():
    mongo_client = None
    mongo_db = None
    mongo_default_hostname = "localhost"
    mongo_default_port = "27017"                                                                                                    
    mongo_default_database = "smear"

    if "MONGODB_URI" in os.environ:
        uri = os.environ["MONGODB_URI"]
        mongo_client = MongoClient(uri)
        mongo_db = uri.split('/')[-1]
        print "Using {} for mongodb database server, database: {}".format(uri.split('@')[-1].split('/')[0], mongo_db)
    else:
        mongo_client = MongoClient("{}:{}".format(mongo_default_hostname, mongo_default_port))
        mongo_db = mongo_default_database
        print "Using {}:{} for mongodb database server, database: {}".format(mongo_default_hostname, mongo_default_port, mongo_db)

    return mongo_client[mongo_db]

db = initialize_mongo_db()
