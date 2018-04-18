from flask import Flask, jsonify, abort, make_response, request
import push_to_git
import json
from pprint import pprint

app = Flask(__name__)

@app.route('/junos/collect_data', methods=['POST'])
def collect_commands():
 if request.headers['Content-Type'] != 'application/json':
        abort(400, message="Expected Content-Type = application/json")
 data = request.json
 dev = data['status']['entityId']
 push_to_git.collect_and_push(dev)
 return jsonify({'collected data on device ': dev}), 201


@app.route('/test', methods=['POST'])
def print_device_name():
 data = request.json
 device_id = data['status']['entityId']
 print device_id
 return device_id

app.run(
    debug=True,
    port=int("12345"),
    host="0.0.0.0"
    )

