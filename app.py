import pickle
from types import MethodDescriptorType
from flask import Flask, render_template, request
from flask.json import jsonify
import uuid

app = Flask(__name__)

with open("projects.pickle", "rb") as fajl:
    projects = pickle.load(fajl)


def save_data(data):
    with open("projects.pickle", "wb") as fajl:
        pickle.dump(projects, fajl)


def filter_list_of_dicts(list_of_dicts, fields):  # szűrő függvény
    filtered_dicts = []

    for dict in list_of_dicts:
        copy_dict = dict.copy()
        for key in dict:
            if key not in fields:
                copy_dict.pop(key, None)
        filtered_dicts.append(copy_dict)
    return filtered_dicts


# fields = ["name", "id"]  kulcsok, amiket látni akarunk


@app.route('/')
def home():
    name = "Zsolt"
    return render_template('index.html', user_name=name)


@app.route('/project', methods=["GET", "POST"])
def get_projects():
    request_data = request.get_json()  # kinyeri a 'GET' a body-ból az adatot
    if request_data and len(request_data["fields"]) > 0:
        return jsonify({
            "projects":
            filter_list_of_dicts(projects["projects"], request_data["fields"])
        })
    return jsonify({'projects': projects})


@app.route('/project/<string:id>')
def get_project(id):
    for project in projects["projects"]:
        if project["project_id"] == id:
            return project
    return jsonify({'message': 'project not found'})


# Frissítés
@app.route('/project/<string:id>/complete', methods=['POST'])
def update_project(id):
    for project in projects["projects"]:
        if project["project_id"] == id:
            if project["completed"]:
                return "", 200
            else:
                project["completed"] = True
                save_data(projects)
                return project
    return jsonify({'message': 'project not found'})


@app.route('/project/<string:id>/task', methods=["GET", "POST"])
def get_all_tasks_in_project(id):
    request_data = request.get_json()
    for project in projects["projects"]:
        if project['project_id'] == id:
            if request_data and len(request_data["fields"]) > 0:
                return jsonify({
                    "tasks":
                    filter_list_of_dicts(project["tasks"],
                                         request_data["fields"])
                })
            return jsonify({'tasks': project['tasks']})
    return jsonify({'message': 'project not found'})


@app.route('/project', methods=['POST'])
def create_project():
    #lekérdezzük a http request body-ból a JSON adatot:
    request_data = request.get_json()
    new_project_id = uuid.uuid4().hex[:24]
    new_project = {
        'name': request_data['name'],
        'project_id': new_project_id,
        'creation_date': request_data['creation_date'],
        'completed': request_data['completed'],
        'tasks': request_data['tasks']
    }
    projects["projects"].append(new_project)  # hozzáadja a listához
    save_data(projects)
    return jsonify({'message': f'project created with id: {new_project_id}'})


@app.route('/project/<string:id>/task', methods=['POST'])
def add_task_to_project(id):
    request_data = request.get_json()
    new_task_id = uuid.uuid4().hex[:24]  # task aonosító
    for project in projects["projects"]:
        if project['project_id'] == id:
            new_task = {
                'name': request_data['name'],
                'task_id': new_task_id,
                'completed': request_data['completed'],
                'checklist': request_data['checklist']
            }
            project['tasks'].append(new_task)
            save_data(projects)  # mentjük a módosításokat
            return jsonify(
                {'message': f'task was added with id: {new_task_id}'})
    return jsonify({'message': 'project not found'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
