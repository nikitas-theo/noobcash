
from Crypto.Hash import SHA256
from time import time
from pymerkle import MerkleTree
from random import randint
from copy import deepcopy
import requests 
import simplejson as json
from state import state
from block import Block
from broadcast import broadcast_block
from transaction import Transaction
from config import * 

class Blockchain : 
    def __init__(self):
        """
        transactions (imported from state): list of transactions not in block
        chain: the blockchain (list of blocks), chain[0] = genesis block
        """
        self.chain = []
       
        
    def genesis(self,n):
        genesis_trans = Transaction(receiver = state.pub, sender = 0, amount = 100*n, inputs = [])
        genesis_block = Block(id = 0,transactions = genesis_trans, previous_hash = 0, nonce = 0)
        self.chain.append(genesis_block)
  
        

    def add_block(self, block):
        """ Validate a block and add it to the chain """
        if not (block.validate_hash() and (block.previous_hash == self.chain[-1].hash)) :
            return False 
        
        self.chain.append(block)
        for block_t in block.transactions:
            for state_t in state.transactions:
                if (state_t.hash == block_t.hash):
                    state.transactions.remove(state_t)
                        
        return True
        

    def mine_block(self):
        
        copy_trans = deepcopy(self.transactions) # deep copy is needed, lists are passed by reference!
        block = Block(id = len(self.chain)+1, transactions = copy_trans, prev_hash = self.chain[-1].hash)
        block.mine()
        self.transactions = []
        broadcast_block(block)

    def resolve_conflict(self):
        MAX_LENGTH = len(state.chain)
        for node in state.nodes :
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
                state.chain = chain
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
        
  

