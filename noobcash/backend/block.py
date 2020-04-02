from time import time

from pymerkle import MerkleTree
from Crypto.Hash import SHA256
import simplejson as json

from state import state
from transaction import Transaction
from config import * 


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

    def __init__(self, id, transactions, prev_hash, nonce =  None):
        
        self.difficulty = DIFFICULTY
        self.capacity = CAPACITY

        self.id = id
        self.timestamp = str(time()).encode()
        self.transactions = transactions
        self.previous_hash = prev_hash
        self.nonce = nonce
    
    def to_json(self):
        return json.dumps(self.__dict__)

    def validate_hash(self):
        # validate block hash value

        tree = MerkleTree()
        for t in self.transactions :
            tree.encryptRecord(t.hash.encode()) # make bytestring
        merkle_hash = tree.rootHash

        header = self.previous_hash + self.nonce+\
                merkle_hash + self.timestamp
        h = SHA256.new()
        hash_value = h.new(h.new(header).digest()).hexdigest()[::-1]
        return  int(hash_value[0:self.difficulty],16) == 0 
    
  
    def mine_block(self):

        # Create hash of transactions with a Merkle Tree
        tree = MerkleTree()
        for t in state.transactions :
            tree.encryptRecord(t.id.encode()) # make bytestring
        merkle_hash = tree.rootHash
        
        # 32-bit sized nonce 
        for nonce in range(2 << 32):
            # header consists of prev_hash, nonce, merkle of transactions
            # and the block timestamps. 
            # see: https://en.bitcoin.it/wiki/Block_hashing_algorithm
            nonce = hex(nonce).encode()
            timestamp = str(time()).encode()
            header = self.previous_hash + nonce +\
                    merkle_hash + timestamp
            h = SHA256.new()
            # apply hashing 2 times 
            hash_value = h.new(h.new(header).digest()).hexdigest()
            hash_value = hash_value[::-1] # reverse, little endian
            if int(hash_value[0:self.difficulty],16) == 0 :
                solved = True
                break
        if solved :
            self.hash = hash_value.encode()
            self.nonce = nonce
            self.timestamp = timestamp
        
            return 0
            
        else : 
            self.mine()

if __name__ == '__main__':
    ''' Α dummy mining test''' 
    x = [Transaction('asdf','asdf',10,[],b'0x23423423') for i in range(5)]
    y = Block(0,b'0x234234134',)
    y.transactions = x
    y.mine()
    print(y.validate())