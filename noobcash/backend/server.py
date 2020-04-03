# -*- coding: utf-8 -*-

'''
application in order to receive requests
'''
from flask import Flask
import argparse
import requests
import flask
from example import idiot_funcs
from state import state
from broadcast import API_communication

parser = argparse.ArgumentParser()
parser.add_argument('host', type=str) #the host of the address
parser.add_argument('port', type=int) #the port of the address
args = parser.parse_args()

app = Flask(__name__)

app.register_blueprint(idiot_funcs)
app.register_blueprint(API_communication)

if __name__ == '__main__':    
    app.run(host = args.host, port=args.port, debug = True)
    