import datetime
from typing import List
import requests
from dataclasses import dataclass


class TodoistClient:
    """
    A simple client for the Todoist service.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_pending(self) -> List["Todo"]:
        """
        Retrieves todos due today or overdue, in priority order.
        """
        response = requests.get(
            "https://api.todoist.com/rest/v1/tasks?filter=(today|overdue)",
            headers={"Authorization": "Bearer %s" % self.api_key},
        )
        todos = []
        for item in response.json():
            due_date = datetime.datetime.strptime(item["due"]["date"], "%Y-%m-%d")
            todos.append(
                Todo(
                    id=item["id"],
                    title=item["content"],
                    priority=item["priority"],
                    due=due_date.date(),
                )
            )
        todos.sort(key=lambda x: x.priority, reverse=True)
        return todos

    def close_task(self, task_id):
        """
        Closes a task by ID
        """
        requests.post(
            "https://api.todoist.com/rest/v1/tasks/%s/close" % task_id,
            headers={"Authorization": "Bearer %s" % self.api_key},
        )


@dataclass
class Todo:
    """
    Represents a single todo
    """

    id: int
    title: str
    priority: int
    due: datetime.date

    def days_overdue(self):
        return (datetime.date.today() - self.due).days
