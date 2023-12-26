# github-pr-reports
This directory holds the script for running reports against the CenturylinkFederal Github Repos. The list is tbd and this is currently targeted at a single repo.

## RUNNING LOCALLY
To run locally, go to the  directory. Set up the the virtual environment by running:
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r  requirements.txt
```
**NOTE**: the python3 command may just be python depending on your machine setup but the script should be run using Python 3.

After this you can add environment variables and run the script with:
```
python3 get_pr_details.py
```
The script will create a csv file locally and push the file to the Azure Storage Account.

To exit the virtual environment, execute:
```
deactivate
```

#### ENVIRONMENT VARIABLES
The script needs the following environment variables set although some have defaults if they are not set.

| VARIABLE         | DESCRIPTION                                                                      | DEFAULT                          | 
|------------------|----------------------------------------------------------------------------------|----------------------------------|
| GH_REPOS         | Comma separated list of repos to gather data. NOTE -- tight list...no whitespace | 'azure-templates'                |
| GH_REPO_OWNER    | The GitHub org that owns the repo.                                               | CenturyLinkFederal               |
| GH_TOKEN         | GitHub token that has permissions to pull the Github api.                        | null                             |
| GH_PAGES         | Number of pages worth of data to pull from Github.                               | 1                                |
| GH_NUMBER_OF_PRS | Number of PR records to return on a single page (max: 100).                      | 100                              |
| MONGO_USER       | Mongo user name                                                                  | pygit                            |
| MONGO_PASSWORD   | Mongo password                                                                   |                                  |
| MONGO_DATABASE   | Mongo Database                                                                   | dora-metrics                               |
| MONGO_APPNAME    | AppName for Mongo instance (for Azure, this is the same as the Cosmos instance)  | null                             |
| MONGO_HOSTNAME | Mongo instance hostname                                                          | rnd-mongo.mongo.cosmos.azure.com | 
