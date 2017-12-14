from parse import main
from os import listdir
from os.path import isfile, join
from flask import Flask, request, jsonify
app = Flask(__name__, static_url_path='/static')

# Basic flask app to wrap solver code around an API to be called
# from the web UI

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/solution_viewer")
def solutions():
    return app.send_static_file('solutions.html')

@app.route('/files')
def get_files():
    path = './input'
    return jsonify({file:open(join(path,file)).read() for file in listdir(path) if isfile(join(path, file)) and file != ".DS_Store"})

@app.route('/solutions')
def get_solution_files():
    path = './solutions'
    return jsonify({file:_break_file(open(join(path,file)).read()) for file in listdir(path) if isfile(join(path, file)) and file != ".DS_Store"})

@app.route('/solve', methods=['POST'])
def solve():
    data = request.form
    print(data)
    try:
        solutions, time, num_pieces = main(str(data['file']), str(data['rotate']), str(data['flip']), str(data['first']))
        return jsonify(solutions, time, num_pieces)
    except:
        return jsonify(None, None, None)

def _break_file(text):
    res = []
    for line in text.split("\n"):
        running = []
        chars = []
        for c in line:
            if c == ' ':
                continue
            chars.append(c)

            if c == "]":
                running.append([l for l in chars])
                chars = []
        res.append([l for l in running])
        running = []
    return res