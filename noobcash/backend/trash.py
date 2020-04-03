# -*- coding: utf-8 -*-
'''
A simple flask server program for debugging and checking certain network functions
'''

import requests
import sys
import simplejson as json
from flask import Blueprint, request, make_response         # import Flask

idiot_funcs = Blueprint('idiot_fun',__name__)

@idiot_funcs.route("/", methods=['POST'])                   # at the end point /
def hello():          
    print(request.is_json)
    sys.stdout.flush()
    data = request.get_json()
    print(data)
    return make_response(json.dumps(data), 200)

@idiot_funcs.route("/int1", methods=['GET'])
def int1():
    return "Hello world 1"

@idiot_funcs.route("/int2", methods=['GET'])
def int2():
    return "Hello world 2"
