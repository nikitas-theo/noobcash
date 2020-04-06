# -*- coding: utf-8 -*-

'''
application in order to receive requests
'''
from flask import Blueprint, request, make_response , Flask
from broadcast import API_communication
import argparse
import functools
print = functools.partial(print, flush=True)

server = Blueprint('server',__name__)
parser = argparse.ArgumentParser()
parser.add_argument('host', type=str) #the host of the address
parser.add_argument('port', type=int) #the port of the address
args = parser.parse_args()

app = Flask(__name__)

app.register_blueprint(server)
app.register_blueprint(API_communication)



if __name__ == '__main__':    
    app.run(host = args.host, port=args.port, debug = False,threaded = True)
    