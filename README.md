# freedcamp_client
This Python module provides an interface to interact with Speakleash's Freedcamp datasets backlog. With it, contributors can effortlessly fetch the next task from a specified list name in the backlog.


# Features
Instantiate Freedcamp api client under the ID of the current user.

Fetch the next task from a specific list name.

Get task details

Start, complete or mark tasks as failed.

# Usage
1. Initialization
Create an instance of the FreedcampClient class by providing your api_key, api_secret, and optionally the project_id if it's different from the default.
To obtain your api_key and api_secret refer to https://freedcamp.com/help_/tutorials/wiki/wiki_public/view/DFaab#setup
Only keys secured by api secret are supported

2. Retrieve a Task
Call the get_task method with the desired liat_group_name to retrieve the next task from that group. This method returns next task from a given list which is not assigned and not started. None returned if task not found.

3. Task Operations

With a retrieved task, you can:
Start the task with start_task() - task is assigned to calling user an its status is set to 'In Progress'
Complete the task with complete_task() - task status is set to 'Completed'
Mark the task as failed with fail_task(comment). Comment is optional and added if present. Since Freedcamp does not support custom statuses the failed task remains 'In Progress' with high priority (red flag) set.
Get task details

# Example:
```python
api = FreedcampClient('api_key', 'api_secret')

task = api.get_task('List name')
if task:
  url = task.data['title']
  task.start_task()
  ...
  task.complete_task()
  

  


