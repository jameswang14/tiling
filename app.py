from parse import main
from os import listdir
from os.path import isfile, join
from flask import Flask, request, jsonify
app = Flask(__name__, static_url_path='/static')

@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route('/files')
def get_files():
    path = './input'
    return jsonify({file:open(join(path,file)).read() for file in listdir(path) if isfile(join(path, file)) and file != ".DS_Store"})

@app.route('/solve', methods=['POST'])
def solve():
    data = request.form
    print(data)
    try:
        solutions, time, num_pieces = main(str(data['file']), str(data['rotate']), str(data['flip']), str(data['first']))
        return jsonify(solutions, time, num_pieces)
    except:
        return jsonify(None, None, None)
