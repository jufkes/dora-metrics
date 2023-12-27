from datetime import datetime
import json
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

def open_time(pr):
  dateCreated = pr['created_at']
  dateCreated = datetime.strptime(dateCreated, '%Y-%m-%dT%H:%M:%SZ')
  currentTime = datetime.utcnow().replace(microsecond=0)
  timeOpen = currentTime - dateCreated
  return(timeOpen)

def number_files_changed(commits):
  return len(commits)

def total_number_of_changes(commits):
  commitCount = 0
  for c in commits:
    commitCount = c['changes'] + commitCount
  return commitCount

def reviewers(reviews):
  reviewers = []
  for r in reviews:
    reviewers.append(r['user']['login'])
  return reviewers

def review_state(reviews):
  for r in reviews:
    state = r['state']
  return state

def review_count(reviews):
  return len(reviews)