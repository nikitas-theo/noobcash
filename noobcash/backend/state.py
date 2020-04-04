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
        
        self.total_time = 0
        self.num_blocks_calculated = 0

    def remove_utxo(self, utxo):
        self.utxos[utxo['owner']].remove(utxo)

    def add_utxo(self, utxo):
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
        genesis_block = Block(id = 0,transactions = [gen_transaction], previous_hash = 1, nonce = 0,hash = b'1')
        self.utxos[self.pub] = [{'trans_id' : gen_transaction.id, 
        'id' : gen_transaction.id + ':0', 'owner' : gen_transaction.receiver , 'amount' : gen_transaction.amount}]
        self.chain.append(genesis_block)

        
    def add_block(self, block):
        """ Validate a block and add it to the chain """
        self.start = time.time()
        self.lock.acquire() #we need to ensure consensus is not running
        self.transactions = []
        if not block.validate_hash():
            #the block cannot be validated; the hash is bogus
            ret = self.resolve_conflict()
        
        elif not (block.previous_hash == self.chain[-1].hash) :
            #the block cannot be validated; the chain is invalid
            ret =  self.resolve_conflict()
        else :
            #the block is valid, add it to the chain
            self.chain.append(block)
        
            #remove block transactions from the transactions not in a block
            for block_t in block.transactions:
                for state_t in self.transactions:
                    if (state_t.hash == block_t.hash):
                        self.transactions.remove(state_t)
        
        #now release the lock
        self.lock.release()

        self.end = time.time()
        self.total_time += (self.end - self.start)
        self.num_blocks_calculated += 1
        self.avg_time = (self.total_time) / (self.num_blocks_calculated)
        print('Running average block addition time: ', self.avg_time,flush=True)
        
        return True
        

    def mine_block(self):
        
        copy_trans = deepcopy(self.transactions) 
        block = Block(id = len(self.chain)+1, transactions = copy_trans, previous_hash = self.chain[-1].hash)
        block.mine()

        if  block.previous_hash == self.chain[-1].hash  :
            self.add_block(block)
            broadcast.broadcast_block(block)
        else :
            self.resolve_confict()
    
    def resolve_conflict(self):
        '''
        implementation of consensus algorithm
        '''
        #acquire lock so that no new blocks get validated during consensus        
        #we have to put a default chain here, we consider our old one as default
        print('Resolve Confict')
        MAX_LENGTH = 0
        while(True):
            for node in self.nodes.values() :
                if node["pub"] == state.pub :
                    continue 
                ip = node['ip']
                response = requests.get('{}/request_chain'.format(ip))

                if (response.status_code != 200):
                    self.lock.release()
                    return False
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
                if not state.validate_chain(chain) :
                    continue

                if len(chain) > MAX_LENGTH : 
                    MAX_LENGTH = len(chain)
                    max_chain = chain 
           
            if MAX_LENGTH != 0 : # we have a valid chain
                self.chain = chain
                break
            
       
        return True
    def validate_chain(self,chain):
        """ validate the blockchain """
        #we should enter this function only if we have the lock from consensus
        for block,block_prev in zip(chain,chain[1:]):
            
            if not block_prev.hash == block.previous_hash and block.validate_hash() :
                self.lock.release()
                return False 
            
        # validate that the first block is the genesis block
        if chain[0].id == 0:
            self.lock.release()
            return True
        else:
            self.lock.release()
            return False

# this is the global state exposed to all modules
state = State()