from datetime import datetime

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