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
        #print('Requesting GENERATE WALLET lock', self.lock)
        #self.lock.acquire()
        random_generator = Random.new().read 
        self.key  = RSA.generate(2048,random_generator)
        self.pub = self.key.publickey().exportKey().decode()
        #print('Releasing GENERATE WALLET lock', self.lock)
        #self.lock.release()

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
        self.avg = None
        self.time0 = time.time()
        
    def key_to_id(self, key):
        for node in self.nodes.items():
            if (key == node[1]['pub']):
                return node[0]
    
    def remove_utxo(self, utxo):
        #print('Requesting REMOVE UTXO lock', self.lock)
        #self.lock.acquire()
        self.utxos[utxo['owner']].remove(utxo)
        #print('Releasing REMOVE UTXO lock', self.lock)
        #self.lock.release()

    def add_utxo(self, utxo):
        #print('Requesting ADD UTXO lock', self.lock)
        #self.lock.acquire()
        if utxo['owner'] not in self.utxos : self.utxos[utxo['owner']] = []
        self.utxos[utxo['owner']].append(utxo)
        #print('Releasing ADD UTXO lock', self.lock)
        #self.lock.release()
    
    def wallet_balance(self): 
        #print('Requesting WALLET BALANCE SHOW lock', self.lock)
        self.lock.acquire()
        balance = 0
        for utxo in self.utxos[self.pub]: 
            balance+=utxo['amount']
        #print('Releasing WALLET BALANCE SHOW lock', self.lock)
        self.lock.release()
        return balance 
        
    def genesis(self):
        #print('-------- genesis --------')
        gen_transaction = Transaction(inputs = [],amount = 100*config.NODE_CAPACITY , sender = 0, receiver = self.pub)
        gen_transaction.calculate_hash()
        genesis_block = Block(id = '0',transactions = [gen_transaction], previous_hash = '1', nonce = '0',hash = b'1')
        self.utxos[self.pub] = [{'trans_id' : gen_transaction.id, 
        'id' : gen_transaction.id + ':0', 'owner' : gen_transaction.receiver , 'amount' : gen_transaction.amount}]
        self.chain.append(genesis_block)
    
    def mine_and_broadcast_block(self):
        #print('Requesting MINE BLOCK lock', self.lock)
        copy_trans = deepcopy(self.transactions) 
        block = Block(id = len(self.chain)+1, transactions = copy_trans[0:config.CAPACITY], previous_hash = self.chain[-1].hash)
        block.mine()
        print('Block mined')
        if not self.add_block(block):
            print('Could not add block')
            return False
        if not (broadcast.broadcast_block(block)):
            print('Could not broadcast block as a result of mining')
            return False
        print ('Successful mining and broadcast')
        return True
        
        #print('Releasing MINE BLOCK lock', self.lock)
        
        
    def add_block(self, block):
        """ Validate a block and add it to the chain """
        #print('Requesting ADD BLOCK lock', self.lock)
        self.lock.acquire()
        #print('Acquiring lock')
        self.TRANSACTIONS_BACKUP = deepcopy(self.transactions)
        self.UTXOS_BACKUP = deepcopy(self.utxos)


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
                print('{} :: Inital block was valid, no need to resolve conflict'.format(time.time()))   
                #the block is valid, add it to the chain
                self.chain.append(block)    

        #print('Running average block addition time: ', self.avg_time,flush=True)

        #now release the lock
        #print('Releasing lock')
        #print('Releasing ADD BLOCK lock', self.lock)
        
        self.time1 = time.time()
        self.total_time = self.time1 - self.time0
        self.time0 = self.time1
        self.num_blocks_calculated += 1
        if (self.avg == None):
            self.avg = self.total_time/self.num_blocks_calculated
        else:
            self.avg = ((self.avg)*(self.num_blocks_calculated - 1) + self.total_time)/self.num_blocks_calculated
        print('Average time by now', self.avg)
        print('Number of blocks', self.num_blocks_calculated)
        self.coin_distribution()
        self.lock.release()
        
        return True 

        
    def resolve_conflict(self):
        '''
        implementation of consensus algorithm
        '''

        # acquire lock so that no new blocks get validated during consensus        
        #print('Resolve Confict')
        MAX_LENGTH = len(self.chain)
        MAX_CHAIN = self.chain
        #print('My chain has size ', len(self.chain), ' and the last two blocks are ', self.chain[-2].id, self.chain[-1].id)
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
            if(len(chain_temp) <= MAX_LENGTH):
                continue
            #print('The chain I receive has size ', len(chain_temp))
            chain = []
            for block in chain_temp : 
                b = Block(**json.loads(block))
                b.transactions = [Transaction(**json.loads(t)) for t in b.transactions]
                b.hash = str(b.hash).encode()
                b.nonce = str(b.nonce).encode()
                b.previous_hash = str(b.previous_hash).encode()
                chain.append(b)
            if not self.validate_chain(chain) :
                #print('Invalid chain')
                continue

            if len(chain) > MAX_LENGTH : 
                print('Actually found a different chain')
                MAX_LENGTH = len(chain)
                MAX_CHAIN = chain 
        self.chain = MAX_CHAIN  
        return True
    
    def coin_distribution(self):
        sum_al = 0
        for utxo in self.utxos.items():
            print('For node ',self.key_to_id(utxo[0]),': ',end='')
            summ = 0
            for utxo1 in utxo[1]:
               summ += utxo1['amount']
            print(summ)
            sum_al += summ 
        print('All money : ',sum_al)

    def validate_chain(self,chain):
        """ validate the blockchain """
        #print('Requesting VALIDATE CHAIN lock', self.lock)
        self.lock.acquire()
        # we check that the first block is genesis 
        if (self.chain[0].to_json() != chain[0].to_json()):
            #print('different genesis!')
            #print('Releasing VALIDATE CHAIN lock', self.lock)
            self.lock.release()
            return False 

        self.transactions = []
        #self.temp_transactions 
        # temp_transactions are not necessary as a tx in BACKUP_TRANS will not validate if it is already in a block, 
        # that is the corresponding utxos will not be avaliable, remember utxos have unique ids.
        gen_transaction = self.chain[0].transactions[0]
        self.utxos = {}
        self.utxos[gen_transaction.receiver]  = [{'trans_id' : gen_transaction.id, 
        'id' : gen_transaction.id + ':0', 'owner' : gen_transaction.receiver , 'amount' : gen_transaction.amount}]
        # replay
        for block_prev,block in zip(chain,chain[1:]):
            #print(block_prev.id, block.id, "Chain under check")
            if not block_prev.hash == block.previous_hash:
                #print('Error, block hash is invalid')
                #print('Releasing VALIDATE CHAIN lock', self.lock)
                self.lock.release()
                return False 
            if not block.validate_hash():
                #print('Could not validate hash')
                #print('Releasing VALIDATE CHAIN lock', self.lock)
                self.lock.release()
                return False 

            for t in block.transactions:
                if not Transaction.validate_transaction(t):
                    #print('block transactions are invalid')
                    self.lock.release()
                    return False 
            print(block_prev.id, block.id, "connection is correct")
            
        self.transactions = []
        for tx in self.TRANSACTIONS_BACKUP:
            Transaction.validate_transaction(tx)
        #print('Releasing VALIDATE CHAIN lock', self.lock)
        self.lock.release()
        return True


# this is the global state exposed to all modules
state = State()