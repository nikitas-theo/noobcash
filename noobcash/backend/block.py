from time import time

#from pymerkle import MerkleTree
from Crypto.Hash import SHA256
import simplejson as json
import config
from copy import deepcopy

import functools
print = functools.partial(print, flush=True)

class Block :
    """ 

         id : the unique ID of the block :: int 
         timestamp : current Unix time :: string  
         transactions : list of verified transactions in block :: list(T) 
         previous_hash : hash of previous block in blockchain :: bytestring 
         nonce : solution of PoW :: bytestring
         hash : the hash of the block :: bytestring
         difficulty :  number of leading zeros required in Hex :: int
         capacity : number of transactions required for mining :: int

    """

    def __init__(self, id, transactions, previous_hash,timestamp = None ,hash = None,nonce =  None):

        self.id = id
        self.timestamp = str(time()).encode() if timestamp == None else timestamp.encode()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce 
        self.hash = hash
    
    def to_json(self):
        dict_b = deepcopy(self.__dict__)
        dict_b['transactions'] = [t.to_json() for t in dict_b['transactions']]
        return json.dumps(dict_b)

    def validate_hash(self):
        # validate block hash value
        '''
        tree = MerkleTree()
        for t in self.transactions :
            tree.encryptRecord(t.id.encode()) # make bytestring
        merkle_hash = tree.rootHash
        '''
        merkle_hash = b'5'
        header = self.previous_hash + self.nonce+\
                merkle_hash + self.timestamp
        h = SHA256.new()
        hash_value = str(h.new(h.new(header).digest()).hexdigest()[::-1])
        return (int(hash_value[0:config.DIFFICULTY],16) == 0)
    
  
    def mine(self):

        # Create hash of transactions with a Merkle Tree
        '''
        tree = MerkleTree()
        for t in self.transactions :
            tree.encryptRecord(t.id.encode()) # make bytestring
        merkle_hash = tree.rootHash
        '''
        merkle_hash = b'5'

        # 32-bit sized nonce 
        for nonce in range(2 << 32):
            # header consists ofev_hash, nonce, merkle of transactions
            # and the block timestamps. 
            # see: https://en.bitcoin.it/wiki/Block_hashing_algorithm
            nonce = hex(nonce).encode()
            timestamp = str(time()).encode()
            header = self.previous_hash + nonce + merkle_hash + timestamp
            h = SHA256.new()
            # apply hashing 2 times 
            hash_value = h.new(h.new(header).digest()).hexdigest()
            hash_value = str(hash_value[::-1]) # reverse, little endian
            if int(hash_value[0:config.DIFFICULTY],16) == 0 :
                solved = True
                break
        if solved :
            self.hash = hash_value.encode()
            self.nonce = nonce
            self.timestamp = timestamp            
        else : 
            self.mine()
