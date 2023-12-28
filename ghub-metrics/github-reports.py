import logging
import json
from environs import Env
from pymongo import MongoClient
import certifi
from processors import pull_request
from handlers import ghub_api

env = Env()
env.read_env()

GH_REPOS = env.list("GH_REPOS", ['eis-liquibase-postgresql'])
MONGO_USER = env('MONGO_USER', 'pygit')
MONGO_PASSWORD = env('MONGO_PASSWORD')
MONGO_DATABASE = env('MONGO_DATABASE', 'dora-metrics')
MONGO_APPNAME = env('MONGO_APPNAME', 'rnd-mongo')
MONGO_HOSTNAME = env('MONGO_HOSTNAME', 'rnd-mongo.mongo.cosmos.azure.com')

# logging setup
FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

def pr_reports():
    pr_collection = 'PullRequests'
    db = 'dora-metrics'

    logging.info("Establishing client for cosmos monogdb...")

    client = MongoClient(
        f"mongodb://{MONGO_HOSTNAME}:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000",
        username=MONGO_USER, password=MONGO_PASSWORD, authSource=MONGO_DATABASE,
        authMechanism='SCRAM-SHA-256', appName=MONGO_APPNAME, tlsCAFile=certifi.where())

    logging.info(f"Using collection {pr_collection} in database {db} for pr's...")
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
                         'merged': pull_request.is_merged(pr), 'closed': pull_request.is_closed(pr),
                         'openTime': str(openTime),
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

def repo_reports():
    collection = 'Repositories'
    db = 'dora-metrics'

    logging.info("Establishing client for cosmos monogdb...")

    client = MongoClient(
        f"mongodb://{MONGO_HOSTNAME}:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000",
        username=MONGO_USER, password=MONGO_PASSWORD, authSource=MONGO_DATABASE,
        authMechanism='SCRAM-SHA-256', appName=MONGO_APPNAME, tlsCAFile=certifi.where())

    logging.info(f"Using collection {collection} in database {db} for repo data...")
    db = client[db]
    collection = db[collection]

    logging.info('Full list of repos to generate reports from: ' + str(GH_REPOS))
    for repo in GH_REPOS:
        logging.info(f"Fetching branch for repo {repo}")
        data = ghub_api.branches(repo)
        repo_record = {
            'repoName': repo, 'branchInfo': {
                'total': repo.total_branches(data),
                'branches': repo.branches(data)
            }
        }

        logging.info(f"Updating record {json.dumps(repo_record)}")

        result = collection.update_one(
            {'repoName': repo}, {"$set": repo_record}, upsert=True
        )

        logging.info(f"Inserted document with _id {result.upserted_id}")

def actions_reports():
    collection = 'ActionsWorkflows'
    db = 'dora-metrics'

    logging.info("Establishing client for cosmos monogdb...")

    client = MongoClient(
        f"mongodb://{MONGO_HOSTNAME}:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000",
        username=MONGO_USER, password=MONGO_PASSWORD, authSource=MONGO_DATABASE,
        authMechanism='SCRAM-SHA-256', appName=MONGO_APPNAME, tlsCAFile=certifi.where())

    logging.info(f"Using collection {collection} in database {db} for actions workflows...")
    db = client[db]
    collection = db[collection]
    for repo in GH_REPOS:
        run = ghub_api.actions(repo)
        for r in run:
            actions_record = {
                'repoName': repo, 'startTime': r['run_started_at'], 'prTitle': r['display_title'], 'user': r['actor']['login'], 'status': r['status'],
                'conclusion': r['conclusion'], 'commit': r['head_sha'], 'branch': r['head_branch'], 'workflow': r['name']
            }
            logging.info(f"Updating record {json.dumps(actions_record)}")

            result = collection.update_one(
                {'prTitle': r['display_title']}, {"$set": actions_record}, upsert=True
            )

            logging.info(f"Inserted document with _id {result.upserted_id}")

if __name__ == "__main__":
  # pr_reports()
  # repo_reports()
  actions_reports()