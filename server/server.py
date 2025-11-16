from flask import Flask, abort, send_from_directory, send_file
from util import graphing
import os

app = Flask(__name__)

output_path = '/home/onaquest/server-output'
recent_image_paths = [max(os.listdir(f'{output_path}/images{i}/')) for i in range(2)]

def read_pass(password_path): 
    with open(password_path) as f:
        return f.read()

@app.route('/<string:site_file>')
def get_file(site_file):
    print(f'requesting: {site_file}')
    filepath = f'site/{site_file}'
    if os.path.exists(filepath):
        with open(filepath) as f:
            return f.read()
    else:
        abort(404)

@app.route('/')
def get_root():
    return get_file('index.html')

# latest image captured
@app.route('/api/image/<string:input_password>/<int:id>')
def get_latest_image(input_password, id):
    if(input_password == password):
        recent_image_paths[id] = max(os.listdir(f'{output_path}/images{id}/'))
        return send_from_directory(f'{output_path}/images{id}', recent_image_paths[id])
    else:
        return send_from_directory('./', f'wrong{id}.png')

# latest temp/humid reading
@app.route('/api/env/')
def get_latest_env():
    last_n = []
    with open(f'{output_path}/environment_log.txt') as f:
        return f.read().split('\n')[-1]

@app.route('/api/env/graph/<string:selection>/<float:hours>')
def get_graph(selection, hours):
    range = graphing.get_relative_range(hours)
    image_file = graphing.make_graph(f'{output_path}/environment_log.txt', range, selection)
    return send_file(image_file)

password = read_pass('password.txt')
if __name__ == '__main__':
    print('starting...')
    app.run(host='0.0.0.0', port=80)
