def total_branches(repo_data):
    return len(repo_data)

def branches(repo_data):
    branches = []
    for branch in repo_data:
        branches.append(branch['name'])
    return branches