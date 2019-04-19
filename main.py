# Import required modules
import os
import sys
import json
import base64
import requests
import asana as Asana
from flask import Flask

# Flask
app = Flask(__name__)
@app.route('/')

# Generate Asana API client
def asana_client():
    return Asana.Client.access_token(os.environ['ASANA_TOKEN'])

# Get template project details
def get_tmp(id):

    # Check for PAT
    if 'ASANA_TOKEN' in os.environ:

        tasks_list = []
        asana = asana_client()
        tasks = asana.tasks.find_by_project(id)
        project = asana.projects.find_by_id(id)

        # Tasks iteration
        for task in tasks:
            subtasks = asana.tasks.subtasks(task["id"])
            subtasks_list = []
            
            # Subtasks iteration
            for subtask in subtasks:
                subtasks_list.append(subtask["name"])
            
            # Add subtasks to tasks array
            tasks_list.append({
                "task": task["name"],
                "subtasks" : subtasks_list
            })

        return {
            "workspace": project['workspace'],
            "team": project['team'],
            "tasks": tasks_list,
        }

    else:
        print('Unable to find the Asana token')


# Create new Asana project
def copy_project(src):

    # Instantiate Asana Client
    asana = asana_client()

    # Get Template Data
    src_project = get_tmp(src['id'])
    workspace = src_project['workspace']['id']
    team = src_project['team']['id']
    name = src['name']

    # Reverse task list to make way for Asana ordering
    tasks = reversed(src_project['tasks'])

    # Send request to API
    project = asana.projects.create({
        "workspace": workspace,
        "team": team,
        "name": name
    })

    print("Created project {0}" .format(project['id']))

    # Iterate through tempalate tasks
    for task in tasks:
        # Create new tasks
        new_task = asana.tasks.create({"projects": [project['id']],"name" : task['task']})
       
        if task['subtasks']:  # Check for subtasks
            # Add subtasks for parent tasks
            for subtask in reversed(task['subtasks']):
                asana.tasks.add_subtask(new_task['id'], {"name": subtask})

    return project['id']


# Get Asana template ID
def get_src(order):

    # Dict for new project parameters
    params = dict()

    # Set dict based on matching project
    if 'Dialpad Implementation' in order['product']:
        params['id'] = os.environ['DPI_PROJECT_ID']
        params['name'] = "DP " + order['domain']
        params['hook'] = os.environ['DPI_HOOK']
       
    elif 'Dialpad Guided Trial' in order['product']:
        params['id'] = os.environ['DPT_PROJECT_ID']
        params['name'] = "DPT " + order['domain']
        params['hook'] = os.environ['DPT_HOOK']
    
    elif 'G Suite Implementation' in order['product']:
        params['id'] = os.environ['GSM_PROJECT_ID']
        params['name'] = "GSM " + order['domain']
        params['hook'] = os.environ['GSM_HOOK']
       
    else:
        return False

    return params


# The start of the function.
def onboard_dp_gsm(message, context):
    if 'data' in message:
        data = base64.b64decode(message['data']).decode('utf-8')
        order = json.loads(data)
        print(order)
        src = get_src(order)
        if src:
            project = copy_project({
                "id": src['id'],
                "name": src['name']
            })
            order['project'] = project
            response = requests.post(url=src['hook'], data=order)
        else:
            print("Invalid order type, aborting operation.")
    else:
        print('No data found from Pub/Sub message.')

