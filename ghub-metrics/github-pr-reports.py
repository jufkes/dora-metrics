import logging
import json
from environs import Env
from pymongo import MongoClient
import certifi
from processors import pull_request
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
  pr_collection = 'PullRequests'
  db = 'dora-metrics'

  logging.info("Establishing client for cosmos monogdb...")

  client = MongoClient(
    f"mongodb://{MONGO_HOSTNAME}:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000",
    username=MONGO_USER, password=MONGO_PASSWORD, authSource=MONGO_DATABASE,
    authMechanism='SCRAM-SHA-256', appName=MONGO_APPNAME, tlsCAFile=certifi.where())

  logging.info(f"Using collection {pr_collection} in database {db}...")
  db = client[db]
  collection = db[pr_collection]

  logging.info('Full list of repos to generate reports from: ' + str(GH_REPOS))
  for repo in GH_REPOS:
    logging.info(f"Fetching PRs for repo {repo}")
    prList = ghub_api.get_prs(repo)

    for pr in prList:
      if pull_request.is_closed(pr):
        openTime = pull_request.open_to_closed_time(pr)
      else:
        openTime = pull_request.open_time(pr)

      commits = ghub_api.pr_files_changed(repo, pr['number'])
      reviews = ghub_api.pr_reviews(repo, pr['number'])

      if reviews:
        reviewDetails = {
          'reviewers': pull_request.reviewers(reviews),
          'count': pull_request.review_count(reviews),
          'state': pull_request.review_state(reviews)
        }
      else:
        reviewDetails = {}
      pr_record = {'state': pr['state'], 'PRNumber': pr['number'], 'draft': pr['draft'],
                   'githubUser': pr['user']['login'], 'dateCreated': pr['created_at'],
                   'dateClosed': pr['closed_at'], 'dateMerged': pr['merged_at'],
                   'headBranch': pr['head']['ref'], 'baseBranch': pr['base']['ref'], 'repoName': repo,
                   'merged': pull_request.is_merged(pr), 'closed': pull_request.is_closed(pr), 'openTime': str(openTime),
                   'commitDetails': {
                      'totalFilesChanged': pull_request.number_files_changed(commits),
                      'totalNumberOfChanges': pull_request.total_number_of_changes(commits)
                      },
                   'reviewDetails': reviewDetails
                   }
      logging.info(f"Updating record for PR {json.dumps(pr_record)}")
      result = collection.update_one(
        {'PRNumber': pr_record['PRNumber']}, {"$set": pr_record}, upsert=True
      )

      logging.info(f"Inserted document with _id {result.upserted_id}")

    logging.info('Updated: ' + str(len(prList)) + ' records')