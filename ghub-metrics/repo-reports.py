import logging
import json
from environs import Env
from pymongo import MongoClient
import certifi
from processors import repository
from processors import ghub_api

env = Env()
env.read_env()

GH_REPOS = env.list("GH_REPOS", ['azure-templates'])
MONGO_USER = env('MONGO_USER', 'pygit')
MONGO_PASSWORD = env('MONGO_PASSWORD')
MONGO_DATABASE = env('MONGO_DATABASE', 'dora-metrics')
MONGO_APPNAME = env('MONGO_APPNAME', 'rnd-mongo')
MONGO_HOSTNAME = env('MONGO_HOSTNAME', 'rnd-mongo.mongo.cosmos.azure.com')

# logging setup
FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

if __name__ == "__main__":
  collection = 'Repositories'
  db = 'dora-metrics'

  logging.info("Establishing client for cosmos monogdb...")

  client = MongoClient(
    f"mongodb://{MONGO_HOSTNAME}:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000",
    username=MONGO_USER, password=MONGO_PASSWORD, authSource=MONGO_DATABASE,
    authMechanism='SCRAM-SHA-256', appName=MONGO_APPNAME, tlsCAFile=certifi.where())

  logging.info(f"Using collection {collection} in database {db}...")
  db = client[db]
  collection = db[collection]

  logging.info('Full list of repos to generate reports from: ' + str(GH_REPOS))
  for repo in GH_REPOS:
    logging.info(f"Fetching branch for repo {repo}")
    data = ghub_api.branches(repo)
    print(json.dumps(data))
    repo_record = {
      'repoName': repo, 'branchInfo': {
        'total': repository.total_branches(data),
        'branches': repository.branches(data)
      }
    }

    logging.info(f"Updating record {json.dumps(repo_record)}")

    result = collection.update_one(
      {'repoName': repo}, {"$set": repo_record}, upsert=True
    )

    logging.info(f"Inserted document with _id {result.upserted_id}")