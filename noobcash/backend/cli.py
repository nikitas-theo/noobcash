
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
    python cli.py HOST PORT -ch COORD_HOST -cp COORD_PORT -capacity CAPACITY -difficulty DIFFICULTY: start a client and coordinate it to the coordinator.
    python cli.py HOST PORT -n CLIENTS -capacity CAPACITY -difficulty DIFFICULTY: start the coordinator,
    CLIENTS : number of nodes 
Also includes a full CLI implementation.

"""


parser = argparse.ArgumentParser()
parser.add_argument('host', type=str) #the host of the address 
parser.add_argument('port', type=int) #the port of the address
parser.add_argument('-n', type=int) #the number of nodes (when running as coordinator)
parser.add_argument('-ch', type=str) #the host of the coordinator address (when running as client)
parser.add_argument('-cp', type=str) #the port of the coordinator address (when running as client)
parser.add_argument('-capacity',type=int) #the capacity of the block
parser.add_argument('-difficulty', type=int) #the difficulty of the block
parser.add_argument('-test',type = int) 
args = parser.parse_args()

# ----- parse -----
HOST = 'http://{}:{}'.format(args.host,args.port)

NODES = args.n
CAPACITY = args.capacity
DIFFICULTY = args.difficulty
IS_COORDINATOR = True if NODES else False 
if args.test : 
    TEST = True 
    n_nodes = args.test 
else :
    TEST = False

if (IS_COORDINATOR):
    URL = '{}/start_coordinator'.format(HOST)
    response = requests.post(URL, json=json.dumps({'NODE_CAPACITY': str(NODES),\
                             'host': HOST, 'CAPACITY': str(CAPACITY), 'DIFFICULTY': str(DIFFICULTY)}))
else:
    COORDINATOR_HOST = 'http://{}:{}'.format(args.ch,args.cp)
    URL = '{}/start_client'.format(HOST)
    response = requests.post(URL, json=json.dumps({'host': HOST, 'coordinator_host' : COORDINATOR_HOST, \
                                                   'CAPACITY': str(CAPACITY), 'DIFFICULTY': str(DIFFICULTY)}))
my_id = response.json()['id']

# wait for server to notify that every network node has received node info
while(True):
    response2 = requests.get('{}/notify_start'.format(HOST))
    answer = response2.json()['resp']
    if (answer == 'no'):
        # we poll the server with a given time delay to avoid DDoS
        time.sleep(0.2)
    else:
        break
if TEST: 
    f = open('./{}nodes/transactions{}.txt'.format(n_nodes,my_id))
while(True):

    """ CLI implementation """
    
    if TEST :
        cli = f.readline()
        if cli == '' :
             break 
        cli = 't ' + cli 
    else :
        cli = input('(cli) > ')
    cli = cli.strip()
    if (cli.startswith('t')):
        print(cli)
        [node_id,amount] = cli.split()[1:]
        node_id = node_id[2:]

        response = requests.post('{}/new_transaction'.format(HOST), json = json.dumps({'recipient_address': '{}'.format(node_id), 'amount': '{}'.format(amount)}))
        if (response.status_code != 200):
            print('Invalid Transaction')

    
    elif (cli == 'view'):
        response = requests.get('{}/view_transactions'.format(HOST))
        ret = response.json()
        print('Showing latest block transactions:')
        for i,t in enumerate(ret['transactions']): 
            print('Transaction #{}\n'.format(i+1))
            t = json.loads(t)
            for key,val in t.items():
                print('{} : {}'.format(key,val))
    
    elif (cli == 'balance'):
        """ 
        Print the current balance of the wallet,
        by calculating UTXOs.
        """
        response = requests.get('{}/balance'.format(HOST))
        balance =  response.json()
        print('Current wallet balance : ', balance)
    
    elif (cli == 'help'):
        print('Commands:')
        print('[t <recipient_id> amount]:')
        print('\t\t Give <amount> noobchash coins to network node with id <recipient_id>, usecase: id3 100 \\n')
        print('[view]:')
        print('\t\tview all transactions in the latest block of the blockchain')
        print('[balance]:')
        print('\t\tCurrent balance in noobcash coins, calculated by summing UTXOs (unspent transactions) ')
        print('[exit]:')
        print('\t\texit the command line interface')
    elif cli == 'exit':
        exit(-1)
    else :
        print('`{}`'.format(cli))
        print('Unknown command, see [help]')
