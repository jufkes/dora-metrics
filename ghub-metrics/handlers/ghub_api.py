import requests
from environs import Env
import logging
import json

env = Env()
env.read_env()

#GITHUB VARS
GH_REPO_OWNER = env('GH_REPO_OWNER', 'CenturyLinkFederal')
GH_TOKEN = env('GH_TOKEN')
GH_PAGES = env('GH_PAGES', 2)
GH_NUMBER_OF_PRS = env('GH_NUMBER_OF_PRS', 10)
GH_BRANCHES_PER_PAGE = env('GH_BRANCHES_PER_PAGE', 100)

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

def pr_files_changed(repo, pull_number):
  url = f"https://api.github.com/repos/{GH_REPO_OWNER}/{repo}/pulls/{pull_number}/files"
  logging.info(f"Fetching files for pull {pull_number}")
  payload = {}
  headers = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'Authorization': f'Bearer {GH_TOKEN}'
  }
  response = requests.request("GET", url, headers=headers, data=payload)
  json_response = json.loads(response.text)
  return json_response

def pr_reviews(repo, pull_number):
  url = f"https://api.github.com/repos/{GH_REPO_OWNER}/{repo}/pulls/{pull_number}/reviews"
  logging.info(f"Fetching reviews for pull {pull_number}")
  payload = {}
  headers = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'Authorization': f'Bearer {GH_TOKEN}'
  }
  response = requests.request("GET", url, headers=headers, data=payload)
  json_response = json.loads(response.text)
  return json_response

def branches(repo):
  branches = []
  totalPaging = GH_PAGES + 1
  for page in range(1, totalPaging):
    url = f"https://api.github.com/repos/{GH_REPO_OWNER}/{repo}/branches?per_page={GH_BRANCHES_PER_PAGE}&page={page}"
    logging.info(f"Fetching branches for pull {repo}")
    payload = {}
    headers = {
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Authorization': f'Bearer {GH_TOKEN}'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    json_response = json.loads(response.text)
    logging.debug('Response from GitHub API: {}'.format(json_response))

    logging.info('Generating full list of branches for processing')
    for payload in json_response:
      branches.append(payload)
  return branches

def dependabot(repo):
  #/enterprises/{enterprise}/dependabot/alerts
  pass

def actions(repo):
  total_workflow_runs = []
  totalPaging = GH_PAGES + 1
  for page in range(1, totalPaging):
    url = f"https://api.github.com/repos/{GH_REPO_OWNER}/{repo}/actions/runs?page={page}&per_page=100"

    payload = {}
    headers = {
      'Accept': 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Authorization': f'Bearer {GH_TOKEN}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    json_response = json.loads(response.text)
    if len(json_response['workflow_runs']) == 0:
      break

    logging.info(f"Retrieving page {page}. {json_response['total_count']} total workflow runs.")

    for run in json_response['workflow_runs']:
      total_workflow_runs.append(run)
  return total_workflow_runs