from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random
from random import randint

from copy import deepcopy

import simplejson as json
import requests

import config
from block import Block
from transaction import Transaction

from flask import Flask
import broadcast

from threading import RLock
import time
import functools
print = functools.partial(print, flush=True)

class State :
    """
        chain : our version of the blockchain :: list(B)
        utxos : unspent trans for all nodes :: utxos[owner] = {trans_id, id, owner, amount}
        nodes : node information :: nodes[id] = {ip,pub}
        transactions : list of verified transactions not in a block :: list(T)
        key: RSA key including private and public key :: string
        pub : RSA public part of key :: string
        id : our id

    """

    def generate_wallet(self): 
        random_generator = Random.new().read 
        self.key  = RSA.generate(2048,random_generator)
        self.pub = self.key.publickey().exportKey().decode()

    def __init__(self):
       
        self.lock = RLock()
        self.generate_wallet()
        self.utxos = {}
        self.chain = []
        self.nodes = {}
        self.transactions = []
        self.last_id = 0 # for coordinator only 
        self.total_time = 0
        self.num_blocks_calculated = 0

    def remove_utxo(self, utxo):
        self.utxos[utxo['owner']].remove(utxo)

    def add_utxo(self, utxo):
        if utxo['owner'] not in self.utxos : self.utxos[utxo['owner']] = []
        self.utxos[utxo['owner']].append(utxo)
    
    def wallet_balance(self): 
        balance = 0
        for utxo in self.utxos[self.pub]: 
            balance+=utxo['amount']
        return balance 
        
    def genesis(self):
        print('-------- genesis --------')
        gen_transaction = Transaction(inputs = [],amount = 100*config.NODE_CAPACITY , sender = 0, receiver = self.pub)
        gen_transaction.calculate_hash()
        genesis_block = Block(id = '0',transactions = [gen_transaction], previous_hash = '1', nonce = '0',hash = b'1')
        self.utxos[self.pub] = [{'trans_id' : gen_transaction.id, 
        'id' : gen_transaction.id + ':0', 'owner' : gen_transaction.receiver , 'amount' : gen_transaction.amount}]
        self.chain.append(genesis_block)
    
    def mine_block(self):
        
        copy_trans = deepcopy(self.transactions) 
        block = Block(id = len(self.chain)+1, transactions = copy_trans, previous_hash = self.chain[-1].hash)
        block.mine()
        self.add_block(block)
        broadcast.broadcast_block(block)
        
    def add_block(self, block):
        """ Validate a block and add it to the chain """
        self.start = time.time()
        self.TRANSACTIONS_BACKUP = deepcopy(self.transactions)
        self.UTXOS_BACKUP = deepcopy(self.utxos)

        print('Requesting lock')
        #self.lock.acquire()
        print('Acquiring lock')

        #we need to ensure consensus is not running
        # check for hash and precious hash
        if not block.validate_hash() or not (block.previous_hash == self.chain[-1].hash) :
            self.resolve_conflict()
        else :
            # check for block transactions
            # check if block contains transactions not in old transactions 
            # if it does, add them (for utxos). 
            valid = True 
            for t in block.transactions:
                exists = False 
                for state_t in self.transactions: 
                    if t.id == state_t.id : 
                        self.transactions.remove(state_t)
                        exists = True
                if not exists : 
                    valid = Transaction.validate_transaction(t)
                    if not valid : 
                        break
                    self.transactions.remove(t) # remove transaction it has been consumed
            if not valid : 
                self.resolve_conflict()
            if valid :
                print('Inital block was valid, no need to resolve conflict')       
        self.end = time.time()
        self.total_time += (self.end - self.start)
        self.num_blocks_calculated += 1
        self.avg_time = (self.total_time) / (self.num_blocks_calculated)
        print('Running average block addition time: ', self.avg_time,flush=True)
        #the block is valid, add it to the chain
        self.chain.append(block)

        #now release the lock
        print('Releasing lock')
        #self.lock.release()
        return True 

        
    def resolve_conflict(self):
        '''
        implementation of consensus algorithm
        '''
        # acquire lock so that no new blocks get validated during consensus        
        print('Resolve Confict')
        MAX_LENGTH = len(self.chain)
        MAX_CHAIN = self.chain
        for node in self.nodes.values() :
            if node["pub"] == self.pub :
                continue 
            ip = node['ip']
            response = requests.get('{}/request_chain'.format(ip))

            if (response.status_code != 200):
                print('Did not receive chain')
                continue
            # extract blocks from chain, they are in string format
            chain_temp = response.json()['chain']
            chain = []
            for block in chain_temp : 
                b = Block(**json.loads(block))
                b.transactions = [Transaction(**json.loads(t)) for t in b.transactions]
                b.hash = str(b.hash).encode()
                b.nonce = str(b.nonce).encode()
                b.previous_hash = str(b.previous_hash).encode()
                chain.append(b)
            if not self.validate_chain(chain) :
                print('Invalid chain')
                continue

            if len(chain) > MAX_LENGTH : 
                MAX_LENGTH = len(chain)
                MAX_CHAIN = chain 
        
            
        self.chain = MAX_CHAIN    

        return True

    def validate_chain(self,chain):
        """ validate the blockchain """

        # we check that the first block is genesis 
        if (self.chain[0].to_json() != chain[0].to_json()):
            print('different genesis!')
            return False 

        self.transactions = []
        gen_transaction = self.chain[0].transactions[0]
        self.utxos = {}
        self.utxos[gen_transaction.receiver]  = [{'trans_id' : gen_transaction.id, 
        'id' : gen_transaction.id + ':0', 'owner' : gen_transaction.receiver , 'amount' : gen_transaction.amount}]
        # replay
        for block_prev,block in zip(chain,chain[1:]):
            if not block_prev.hash == block.previous_hash:
                print('Error, block hash is invalid')
                return False 
            if not block.validate_hash():
                print('Could not validate hash')
                return False 

            for t in block.transactions:
                if not Transaction.validate_transaction(t):
                    print('block transactions are invalid') 
                    return False 
    
 
        for tx in self.TRANSACTIONS_BACKUP:
            Transaction.validate_transaction(tx)

        return True


# this is the global state exposed to all modules
state = State()