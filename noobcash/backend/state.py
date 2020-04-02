from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random
from random import randint

from copy import deepcopy

import simplejson as json
import requests

from config import *
from block import Block
import broadcast
from transaction import Transaction


from flask import Flask



class State :
    """
        chain : our version of the blockchain :: list(B)
        utxos : unspent trans for all nodes :: utxos[owner] = {trans_id, id, owner, amount}
        nodes : node information :: nodes[id] = {ip,port,pub}
        transactions : list of verified transactions not in a block :: 
        key: RSA key including private and public key :: string
        pub : RSA public part of key :: string

    """

    def __init__(self):
       
        self.generate_wallet()
        self.chain = ()
        self.utxos = {}
        self.nodes = {}
        self.transactions = []
   
    
    def connect_to_coordinator(self, coordinator_ip, coordinator_port, client_ip, client_port):
        """
        send a POST request for connection to the coordinator.
        returns the blockchain 
        """

        response = requests.post(f'http://{coordinator_ip}:{coordinator_port}/register_node',\
                      json={f'"ip":"{client_ip}"',f'"port":"{client_port}"',\
                            f'"pubkey":"{self.pub}"'})
        # we request node_id
        if response.status_code == 200 :
            self.id = response.json()['id']

            # we also request the chain
            response = requests.post(f'http://{coordinator_ip}:{coordinator_port}/request_chain',\
                    json={f'"ip":"{client_ip}"',f'"port":"{client_port}"',\
                        f'"pubkey":"{self.pub}"'})

            if response.status_code == 200 :
                block_list = json.loads(response.json()['chain'])
                chain = [Block(**json.loads(block))for block in block_list]
                if self.validate_chain(chain) : 
                    self.chain = chain
                return True 
        return False 

    def generate_wallet(self): 
        random_generator = Random.new().read 
        self.key  = RSA.generate(2048,random_generator)
        #key is an RSA key object, the private key is not visible
        self.pub = self.key.publickey

    def remove_utxo(self, utxo):
        self.utxos[utxo['owner']].remove(utxo)

    def add_utxo(self, utxo):
        self.utxos[utxo['owner']].append(utxo)
    
    def wallet_balance(self): 
        balance = 0
        for u in self.utxo[self.pub]: 
            balance+=self.utxo['amount']
        return balance 
        
    
    def __init__(self):
        """
        transactions (imported from state): list of transactions not in block
        chain: the blockchain (list of blocks), chain[0] = genesis block
        """
        self.chain = []
       
        
    def genesis(self,n):
        genesis_trans = Transaction(receiver = self.pub, sender = 0, amount = 100*n, inputs = [])
        genesis_block = Block(id = 0,transactions = genesis_trans, previous_hash = 0, nonce = 0)
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
app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug = True)