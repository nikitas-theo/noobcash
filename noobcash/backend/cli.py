# -*- coding: utf-8 -*-
'''
application in order to send requests and perform functions

usage:
    python active_app.py HOST PORT --l COORD_HOST --lp COORD_PORT: start a client and coordinate it to the coordinator.
    python active_app.py HOST PORT --c CLIENTS --m MONEY: start the coordinator,
    with a capacity of CLIENTS clients and give them MONEY money in the wallet.

Also includes a full CLI implementation.
'''

import sys
import broadcast
import requests
import argparse
import simplejson as json
from flask import Flask, request
from config import *

parser = argparse.ArgumentParser()
parser.add_argument('host', type=str) #the host of the address 
parser.add_argument('port', type=int) #the port of the address
parser.add_argument('--c', type=int) #the number of clients (when running as coordinator)
parser.add_argument('--m', type=int) #the number of initial money (when running as coordinator)
parser.add_argument('--l', type=str) #the host of the coordinator address (when running as client)
parser.add_argument('--lp', type=str) #the port of the coordinator address (when running as client)
args = parser.parse_args()

HOST = f'http://{args.host}:{args.port}'
PORT = str(args.port)
CLIENTS = args.c
MONEY = args.m
COORDINATOR_HOST = args.l
COORDINATOR_PORT = args.lp
COORDINATOR_URL = f'http://{COORDINATOR_HOST}:{COORDINATOR_PORT}'
URL = f'{HOST}/start_coordinator' if CLIENTS else f'{COORDINATOR_URL}/register_node'

if (CLIENTS):
    IS_COORDINATOR = True
    response = requests.post(URL, json=json.dumps({'num_clients': str(CLIENTS), 'initial_money': str(MONEY),\
                             'host': HOST, 'port': str(PORT)}))
else:
    IS_COORDINATOR = False
    print(state.pub)
    response = requests.post(URL, json=json.dumps({'ip': HOST, 'port': str(PORT), 'pub': state.pub.exportKey().decode()}))




while(True):
    '''
    CLI implementation
    '''
    
    cli = input('(cli) > ') #gets the command, adding a $ to prompt in style
    
    if (cli[0] == 't'):
        command = cli.split()
        recipient_address = command[2]
        amount = command[4]
        response = requests.post(f'{HOST}/new_transaction', json = json.dumps({'recipient_address': f'{command[2]}', 'amount': f'{command[4]}'})
        '''
        

        Parameters
        ----------
        recipient_address : the address and the port
        the recipient is listening to, e.g. "127.0.0.1:5050"
        amount : the amount of cash the recipient
        will receive, e.g. "30"

        Returns
        -------
        todo
        203 if the request and the transaction was complete
        400 if the request was bad
        500 if the request was good but the transaction failed

        '''
        
    
    elif (cli == 'view'):
        '''
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        Prints the transactions in the last validated
        block of the chain. Calls view_transactions()
        functions that does this.
        
        '''
        response = requests.post(f'{HOST}/view_transactions')
    
    elif (cli == 'balance'):
        '''
        
        Print the current balance of the wallet,
        by calculating UTXOs.
        
        '''
        response = requests.post(f'{HOST}/balance')
    
    elif (cli == 'help'):
        '''
        explanation of the above commands
        '''
