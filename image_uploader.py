from flask import Flask, abort, send_from_directory, jsonify
import os

app = Flask(__name__)
base_path = '/home/onaquest/server-output'

@app.route('/list') # return current list of all images
def get_list():
    lists = [
        [
            [id, file, os.path.getsize(f'{base_path}/images{id}/{file}')] 
            for file in os.listdir(f'{base_path}/images{id}')] 
        for id in range(2)]

    return jsonify(lists[0] + lists[1])

# client will compare its list of images to what it needs and begin making requests 
@app.route('/images<int:id>/<string:date_str>') # request specific image
def get_image(date_str, id):
    return send_from_directory(f'{base_path}/images{id}', f'{date_str}.png')

if __name__ == '__main__':
    print('starting...')
    app.run(host='0.0.0.0', port=6767)
