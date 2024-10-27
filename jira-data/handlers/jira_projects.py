from jira import JIRA
from environs import Env

env = Env()
env.read_env()

token = env('JIRA_TOKEN')
email = env('JIRA_EMAIL')
host = env('JIRA_HOST')

auth_jira = JIRA(basic_auth=(email, token),server=host)

def get_projects():
    '''
    :return: formatted dictionary of key:value project relationships
    '''
    jira_projects = auth_jira.projects()
    projects = {}
    for p in jira_projects:
        projects[p.key] = p.name
    return projects

def get_project(project):
    '''
    :param project: jira project KEY
    :return: json object of jira project data
    '''
    jira_project = auth_jira.project(project).raw
    return jira_project