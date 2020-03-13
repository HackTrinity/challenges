import functools

from werkzeug.exceptions import InternalServerError
from flask import Flask, request
import yaml

app = Flask(__name__)

def yaml_request(route):
    @functools.wraps(route)
    def wrap(*args, **kwargs):
        request.yaml = yaml.unsafe_load(request.stream)
        return route(*args, **kwargs)
    return wrap

def yamlify(*args, **kwargs):
    if args and kwargs:
        raise TypeError('yamlify() behavior undefined when passed both args and kwargs')
    elif len(args) == 1:  # single args are passed directly to dumps()
        data = args[0]
    else:
        data = args or kwargs

    return app.response_class(
        yaml.dump(data) + '\n',
        mimetype='application/x-yaml',
    )


people = {}

@app.route('/people')
def get_people():
    return yamlify(people)

@app.route('/people/<name>', methods=['POST'])
@yaml_request
def create_person(name):
    people[name] = request.yaml
    return yamlify(people[name]), 201

@app.route('/people/<name>', methods=['DELETE'])
@yaml_request
def delete_person(name):
    p = people[name]
    del people[name]
    return yamlify(p)

@app.route('/people/<name>')
def get_person(name):
    return yamlify(people[name])


@app.errorhandler(404)
def not_found(_e):
    return yamlify({'message': 'not found'}), 404

@app.errorhandler(InternalServerError)
def internal_error(e):
    original = getattr(e, 'original_exception', None)

    if original is None:
        return yamlify({'message': 'unknown error'}), 500
    return yamlify({'message': str(original)}), 500
