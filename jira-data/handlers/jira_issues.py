from jira import JIRA
from environs import Env

env = Env()
env.read_env()

token = env('JIRA_TOKEN')
email = env('JIRA_EMAIL')
host = env('JIRA_HOST')

auth_jira = JIRA(basic_auth=(email, token),server=host)