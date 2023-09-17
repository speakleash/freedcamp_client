import requests
import hmac
import time

class FreedcampClient:
    BASE_URL = 'https://freedcamp.com/api/v1/'
    LIMIT = 200

    def __init__(self, api_key, api_secret, project_id=3369926):
        self.api_key = api_key
        self.api_secret = api_secret
        self.project_id = project_id
        self.offset = 0
        self.user_id = self._get_user_id()

    def get_task(self, tasks_list_name):
        """Retrieve a task based on the group name."""
        while True:
            timestamp, hash_value = self._calculate_hash()

            endpoint = f"/tasks?project_id={self.project_id}&f_cf=1&limit={self.LIMIT}&offset={self.offset}&filter%5Bassigned_to_id%5D%5B%5D=0&filter%5Bstatus%5D%5B%5D=0&order%5Border%5D=asc&substring=&f_url_filters=true"
            url = f"{self.BASE_URL}{endpoint}?api_key={self.api_key}&timestamp={timestamp}&hash={hash_value}"
            headers = {'X-API-KEY': self.api_key}

            response = requests.get(url, headers=headers)
            response_data = response.json()

            tasks = response_data['data']['tasks']
            task_data = self._find_next_task(tasks, tasks_list_name)

            if task_data:
                return Task(task_data, self)

            if not response_data.get('meta', {}).get('has_more', False):
                break

            self.offset += self.LIMIT

        return None

    # Private methods
    def _calculate_hash(self):
        """Calculate and return the hash value."""
        timestamp = str(int(time.time()))
        hash_value = hmac.new(self.api_secret.encode(), (self.api_key + timestamp).encode(), 'sha1').hexdigest()
        return timestamp, hash_value
    
    def _get_user_id(self):
        """Retrieve the user id from the current session."""
        timestamp, hash_value = self._calculate_hash()
        endpoint = '/sessions/current'
        url = f"{self.BASE_URL}{endpoint}?api_key={self.api_key}&timestamp={timestamp}&hash={hash_value}"
        headers = {'X-API-KEY': self.api_key}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            response_data = response.json()
            raise Exception(f"Failed to initialize Freedcamp client. Error: {response_data.get('msg', 'Unknown error')}")
        response_data = response.json()   
        return response_data['data']['user_id']

    def _find_next_task(self, tasks, tasks_list_name):
        """Find the next task ID with the given group name."""
        return next((task for task in tasks if task.get('task_tasks_list_name') == tasks_list_name), None)

    def _update_task(self, task_id, data):
        """Update a task with the provided data."""
        timestamp, hash_value = self._calculate_hash()
        endpoint = f"/tasks/{task_id}"
        url = f"{self.BASE_URL}{endpoint}?api_key={self.api_key}&timestamp={timestamp}&hash={hash_value}"
        headers = {'X-API-KEY': self.api_key}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            response_data = response.json()
            raise Exception(f"Failed to update task. Error: {response_data.get('msg', 'Unknown error')}")

    def _comment_task(self, task_id, comment):
        """Add a comment to a task."""
        data = {
            "item_id": task_id,
            "app_id": "2",
            "description": comment
        }
        timestamp, hash_value = self._calculate_hash()
        endpoint = f"/comments"
        url = f"{self.BASE_URL}{endpoint}?api_key={self.api_key}&timestamp={timestamp}&hash={hash_value}"
        headers = {'X-API-KEY': self.api_key}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:           
            response_data = response.json()
            raise Exception(f"Failed to update task. Error: {response_data.get('msg', 'Unknown error')}")    

        
class Task:
    def __init__(self, task_data, api):
        """Initialize a task object with its data and associated API."""
        self.data = task_data
        self.api = api

    @property
    def task_id(self):
        """Retrieve the ID of the task."""
        return self.data.get('id')

    def start_task(self):
        """Mark a task as started by api user."""
        self.api._update_task(self.task_id, {"assigned_to_id": self.api.user_id, "status": 2})

    def complete_task(self):
        """Mark a task as completed."""
        self.api._update_task(self.task_id, {"status": 1})

    def comment_task(self, comment):
        """Add a comment to the task."""
        self.api._comment_task(self.task_id, comment)

    def fail_task(self, comment=None):
        """
        Mark a task as failed. Since there is no dedicated status, a high priority (red flag) is used to indicate issue
        
        Parameters:
            - comment (str, optional): A comment explaining why the task failed. Defaults to None.
        """
        self.api._update_task(self.task_id, {"priority": 3})

        if comment:
            self.comment_task(comment)