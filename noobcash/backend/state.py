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
       
        self.generate_wallet()
        self.utxos = {}
        self.chain = []
        self.nodes = {}
        self.transactions = []
    

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
        genesis_block = Block(id = 0,transactions = [gen_transaction], previous_hash = 0, nonce = 0)
        self.utxos[self.pub] = [{'trans_id' : gen_transaction.id, 
        'id' : gen_transaction.id + ':0', 'owner' : gen_transaction.receiver , 'amount' : gen_transaction.amount}]
        self.chain.append(genesis_block)

        
    def add_block(self, block):
        """ Validate a block and add it to the chain """
        if not (block.validate_hash() and (block.previous_hash == self.chain[-1].hash)) :
            return False 
        
        self.chain.append(block)
        for block_t in block.transactions:
            for state_t in self.transactions:
                if (state_t.hash == block_t.hash):
                    self.transactions.remove(state_t)
                        
        return True
        

    def mine_block(self):
        
        copy_trans = deepcopy(self.transactions) 
        block = Block(id = len(self.chain)+1, transactions = copy_trans, prev_hash = self.chain[-1].hash)
        block.mine()
        #! We need lock, to change state independently from api calls, E.g. when we write a block to state we must not be interrupted with a new block!!!
        if  block.previous_hash == chain[-1].hash  :
            self.transactions = []
            self.add_block(block)
            broadcast.broadcast_block(block)

    def resolve_conflict(self):
        MAX_LENGTH = len(self.chain)
        for node in self.nodes :
            if node["pub"] == state.pub :
                continue 
            ip = node['ip']
            port = node['port']
            response = requests.get(f'http://{ip}:{port}/request_chain')

            if (response.status_code != 200):
                return False
            # extract blocks from chain, they are in string format
            chain_temp = json.loads(response.json()['chain'])
            chain = []
            for block in chain_temp : 
                chain.append(**Block(json.loads(block)))
            if not validate_chain(chain) :
                continue
            if len(chain) > MAX_LENGTH : 
                self.chain = chain
                MAX_LENGTH = len(chain)
        # TODO: Do we need to change utxos? 
        # do we need to change transactions? 
        # see: https://github.com/neoaggelos/noobcash/blob/master/noobcash/backend/consensus.py
         

    @staticmethod
    def validate_chain(chain):
        """ validate the blockchain """
        for block,block_prev in zip(chain,chain[1:]):
            
            if not block_prev.hash == block.prev_hash and block.validate_hash() :
                return False 
            
        # validate that the first block is the genesis block
        if chain[0].index == 0:
            return True
        
# this is the global state exposed to all modules
state = State()