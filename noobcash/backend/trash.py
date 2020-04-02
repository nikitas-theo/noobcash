# -*- coding: utf-8 -*-
'''
A simple flask server program for debugging and checking certain network functions
'''

import requests
import sys
from flask import Flask, request           # import flask
app = Flask(__name__)             # create an app instance

@app.route("/", methods=['POST'])                   # at the end point /
def hello():          
    data = request.get_json()['NAME']
    return data
if __name__ == "__main__":        # on running python app.py
    app.run(debug=True) 