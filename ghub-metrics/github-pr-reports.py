import requests
import json
import logging
from environs import Env
from pymongo import MongoClient
import certifi
from datetime import datetime

env = Env()
env.read_env()

#GITHUB VARS
GH_REPOS = env.list("GH_REPOS", ['azure-templates'])
GH_REPO_OWNER = env('GH_REPO_OWNER', 'CenturyLinkFederal')
GH_TOKEN = env('GH_TOKEN')
GH_PAGES = env('GH_PAGES', 1)
GH_NUMBER_OF_PRS = env('GH_NUMBER_OF_PRS', 10)

# CONNECTION_STRING = env('CONNECTION_STRING')
MONGO_USER = env('MONGO_USER', 'pygit')
MONGO_PASSWORD = env('MONGO_PASSWORD')
MONGO_DATABASE = env('MONGO_DATABASE', 'dora-metrics')
MONGO_APPNAME = env('MONGO_APPNAME', 'rnd-mongo')
MONGO_HOSTNAME = env('MONGO_HOSTNAME', 'rnd-mongo.mongo.cosmos.azure.com')

# logging setup
FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

def get_prs(repo):
  prs = []

  totalPaging = GH_PAGES + 1
  for page in range(1, totalPaging):
    url = f"https://api.github.com/repos/{GH_REPO_OWNER}/{repo}/pulls?state=all&per_page={GH_NUMBER_OF_PRS}&page={page}"
    logging.info(f"Pulling details from {url}")

    payload = {}
    headers = {
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Authorization': f'Bearer {GH_TOKEN}'
    }

    logging.info(f"Fetching page {page}")
    response = requests.request("GET", url, headers=headers, data=payload)

    json_response = json.loads(response.text)
    logging.debug('Response from GitHub API: {}'.format(json_response))

    logging.info('Generating full list of PRs for processing')
    for payload in json_response:
      prs.append(payload)

  return prs

def is_merged(pr):
  if pr['merged_at'] is None:
    return False
  else:
    return True

def is_closed(pr):
  if pr['closed_at'] is None:
    return False
  else:
    return True

def open_to_closed_time(pr):
  dateCreated = pr['created_at']
  dateClosed = pr['closed_at']
  dateCreated = datetime.strptime(dateCreated, '%Y-%m-%dT%H:%M:%SZ')
  dateClosed = datetime.strptime(dateClosed, '%Y-%m-%dT%H:%M:%SZ')
  openTimeLength = dateClosed - dateCreated
  return openTimeLength

if __name__ == "__main__":
  # establish collection
  collection = 'repositories'
  db = 'dora-metrics'

  logging.info("Establishing client for cosmos monogdb...")

  client = MongoClient(
    f"mongodb://{MONGO_HOSTNAME}:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000",
    username=MONGO_USER, password=MONGO_PASSWORD, authSource=MONGO_DATABASE,
    authMechanism='SCRAM-SHA-256', appName=MONGO_APPNAME, tlsCAFile=certifi.where())

  db = client[db]
  logging.info("Listing collections...")
  for coll in db.list_collection_names():
     logging.info({coll})

  collection = db[collection]

  logging.info('Full list of repos to generate reports from: ' + str(GH_REPOS))
  for repo in GH_REPOS:
    logging.info(f"Fetching PRs for repo {repo}")
    prList = get_prs(repo)
    # get the age of PR
    for pr in prList:
      if is_closed(pr):
        openTime = open_to_closed_time(pr)
      else:
        openTime = None

      pr_record = {'state': pr['state'], 'PRNumber': pr['number'], 'draft': pr['draft'],
                   'githubUser': pr['user']['login'], 'dateCreated': pr['created_at'],
                   'dateClosed': pr['closed_at'], 'dateMerged': pr['merged_at'],
                   'headBranch': pr['head']['ref'], 'baseBranch': pr['base']['ref'], 'repoName': repo,
                   'merged': is_merged(pr), 'closed': is_closed(pr), 'openTime': str(openTime)
                   }
      logging.info(f"Updating record for PR {json.dumps(pr_record)}")
      result = collection.update_one(
        {'PRNumber': pr_record['PRNumber']}, {"$set": pr_record}, upsert=True
      )

      logging.info(f"Inserted document with _id {result.upserted_id}")

    logging.info('Updated: ' + str(len(prList)) + ' records')

