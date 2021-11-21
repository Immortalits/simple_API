import pickle
from flask import Flask, render_template, request
from flask.json import jsonify
import uuid

app = Flask(__name__)

with open("projects.pickle", "rb") as fajl:
    projects = pickle.load(fajl)


def save_data(data):
    with open("projects.pickle", "wb") as fajl:
        pickle.dump(projects, fajl)


@app.route('/')
def home():
    name = "Zsolt"
    return render_template('index.html', user_name=name)


@app.route('/project')
def get_projects():
    return jsonify({'projects': projects})


@app.route('/project/<string:id>')
def get_project(id):
    for project in projects["projects"]:
        if project["project_id"] == id:
            return project
    return jsonify({'message': 'project not found'})


@app.route('/project/<string:name>/task')
def get_all_tasks_in_project(name):
    for project in projects:
        if project['name'] == name:
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


@app.route('/project/<string:name>/task', methods=['POST'])
def add_task_to_project(name):
    request_data = request.get_json()
    for project in projects:
        if project['name'] == name:
            new_task = {
                'name': request_data['name'],
                'completed': request_data['completed']
            }
            project['tasks'].append(new_task)
            return jsonify(new_task)
    return jsonify({'message': 'project not found'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
