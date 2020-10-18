import os

from flask import Flask, escape, request

from .syncsign import BottomButtons, Layout, Text, SyncSignClient
from .todoist import TodoistClient

app = Flask(__name__)


@app.route("/")
def hello():
    return "OK"


@app.route("/update/<token>")
def update(token):
    if token == os.environ["UPDATE_TOKEN"]:
        run_update()
        return "Updated"
    else:
        return "Bad token"


@app.route("/update/<token>/top_done")
def top_done(token):
    if token == os.environ["UPDATE_TOKEN"]:
        todoist = TodoistClient(api_key=os.environ["TODOIST_TOKEN"])
        tasks = todoist.get_pending()
        if tasks:
            todoist.close_task(tasks[0].id)
            run_update()
            return "OK"
        else:
            return "No tasks to close"
    else:
        return "Bad token"


def run_update():
    todoist = TodoistClient(api_key=os.environ["TODOIST_TOKEN"])
    syncsign = SyncSignClient(api_key=os.environ["SYNCSIGN_TOKEN"])

    layout = render_todos(todoist)

    for node in syncsign.node_list():
        if node.model == "D42B":
            syncsign.node_draw(node.id, layout)


def render_todos(todoist: TodoistClient):
    """
    Renders todo items into a SyncSign template
    """

    # Create template
    template = Layout()

    # Title
    template.add(
        Text(
            "Todos",
            position=(0, 0),
            size=(400, 30),
            offset=(4, 0),
            font="DDIN_24",
            color="WHITE",
            background_color="BLACK",
        )
    )

    # Buttons
    template.add(BottomButtons([("Top Done", True)]))

    # Todo items
    y_offset = 34
    for i, todo in enumerate(todoist.get_pending()):
        # Title
        template.add(
            Text(
                todo.title,
                (0, y_offset + 2),
                offset=(30, 0),
                font="ROBOTO_CONDENSED_24",
            )
        )
        # Icon
        icon_codepoint = {3: "\uf102", 2: "\uf106", 1: "\uf107", 0: "\uf103"}[
            todo.priority
        ]
        template.add(
            Text(
                icon_codepoint,
                position=(0, y_offset),
                size=(30, 30),
                offset=(3, 0),
                font="ICON_FA_SOLID",
            )
        )
        # Overdue notice
        if todo.days_overdue():
            if todo.days_overdue() == 1:
                text = "1 day overdue"
            else:
                text = "%s days overdue" % todo.days_overdue()
            template.add(
                Text(
                    text,
                    position=(37, y_offset + 28),
                    size=(200, 20),
                    font="APRILSANS_16",
                )
            )
            y_offset += 12
        y_offset += 36

    return template
