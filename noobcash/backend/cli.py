
import sys
import broadcast
import requests
import argparse
import simplejson as json
from flask import Flask, request
from config import *
import time


"""
Command Line Interface

usage:
    python cli.py HOST PORT -ch COORD_HOST -cp COORD_PORT: start a client and coordinate it to the coordinator.
    python cli.py HOST PORT -n CLIENTS start the coordinator,
    CLIENTS : number of nodes 
Also includes a full CLI implementation.

"""


parser = argparse.ArgumentParser()
parser.add_argument('host', type=str) #the host of the address 
parser.add_argument('port', type=int) #the port of the address
parser.add_argument('-n', type=int) #the number of nodes (when running as coordinator)
parser.add_argument('-ch', type=str) #the host of the coordinator address (when running as client)
parser.add_argument('-cp', type=str) #the port of the coordinator address (when running as client)
args = parser.parse_args()

# ----- parse -----
HOST = f'http://{args.host}:{args.port}'

NODES = args.n
IS_COORDINATOR = True if NODES else False 

 

if (IS_COORDINATOR):
    URL = f'{HOST}/start_coordinator'
    response = requests.post(URL, json=json.dumps({'NODE_CAPACITY': str(NODES),\
                             'host': HOST }))
else:
    COORDINATOR_HOST = f'http://{args.ch}:{args.cp}'
    URL = f'{HOST}/start_client'
    response = requests.post(URL, json=json.dumps({'host': HOST, 'coordinator_host' : COORDINATOR_HOST}))
    while(True):
        response = requests.get(f'{HOST}/notify_start')
        answer = response.json()['resp']
        if (answer == "no"):
            #to avoid overflooding the server
            time.sleep(1)
        else:
            break
    
time.sleep(1)
my_id = response.json()['id']
f = open(f'5nodes/transactions{my_id}.txt','r')
transactions = []
for line in f :
    transactions.append(line[2:-1])

for line in transactions:
    cli = f't {line}'
    command = cli.split()[1:]
    print(command)
    response = requests.post(f'{HOST}/new_transaction', json = json.dumps({'recipient_address': f'{command[0]}', 'amount': f'{command[1]}'}))
    if (response.status_code != 200):
        print('Invalid Transaction')

'''
while(True):

    """ CLI implementation """
    
    cli = input('(cli) > ') 
    cli = cli.strip()
    if (cli.startswith('t')):

        command = cli.split()[1:]
        response = requests.post(f'{HOST}/new_transaction', json = json.dumps({'recipient_address': f'{command[0]}', 'amount': f'{command[1]}'}))
        if (response.status_code != 200):
            print('Invalid Transaction')
        
        """ 

        Parameters
        ----------
        recipient_address : the address and the port
        the recipient is listening to, e.g. "127.0.0.1:5050"
        amount : the amount of cash the recipient
        will receive, e.g. "30"

        Returns
        -------
        #TODO:
        203 if the request and the transaction was complete
        400 if the request was bad
        500 if the request was good but the transaction failed

        """
        
    
    elif (cli == 'view'):
        """
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        Prints the transactions in the last validated
        block of the chain. Calls view_transactions()
        functions that does this.
        
        """
        response = requests.get(f'{HOST}/view_transactions')
        ret = response.json()
        print('Showing latest block transactions:')
        for i,t in enumerate(ret['transactions']): 
            print(f'Transaction #{i+1}\n')
            t = json.loads(t)
            for key,val in t.items():
                print(f'{key} : {val}')
    
    elif (cli == 'balance'):
        """ 
        Print the current balance of the wallet,
        by calculating UTXOs.
        """
        response = requests.get(f'{HOST}/balance')
        balance =  response.json()
        print('Current wallet balance : ', balance)
    
    elif (cli == 'help'):
        """
        explanation of the above commands
        """
    elif cli == 'exit':
        exit(-1)

    else :
        print('Unknown command, see : help')
'''