from Crypto.Hash import SHA256
from random import randint
from pymerkle import MerkleTree
from time import time

from transactions import Transaction

CAPACITY = 10

class Block :
    def __init__(self,index, transactions, prev_hash, nonce =  None):
        self.difficulty = 4 # number of leading zeros required in Hex
        self.index = index 
        self.timestamp = str(time()).encode()
        self.transactions = transactions
        self.previous_hash = prev_hash
        self.nonce = nonce
        self.size = 0 
        self.capacity = CAPACITY # must be even number
    
    def mine(self):
        " Proof Of Work"
        
        # Create hash of transactions with a Merkel Tree
        tree = MerkleTree()
        for t in self.transactions :
            tree.encryptRecord(t.id)
        merkel_hash = tree.rootHash
        
        # 32-bit sized nonce 
        for nonce in range(2 << 32):
            # header consists of prev_hash, nonce, merkel of transactions
            # and the block timestamps. 
            # see: https://en.bitcoin.it/wiki/Block_hashing_algorithm
            nonce = hex(nonce).encode()
            header = self.previous_hash + nonce +\
                  merkel_hash + self.timestamp
            h = SHA256.new()
            # apply hashing 2 times 
            hash_value = h.new(h.new(header).digest()).hexdigest()
            hash_value = hash_value[::-1] # reverse, little endian
            if int(hash_value[0:self.difficulty],16) == 0 :
                solved = True
                break
        if solved :
            self.nonce = nonce
            self.hash = hash_value
            self.header = header
            return 0
        else : 
            self.mine()

    def validate(self):

        tree = MerkleTree()
        for t in self.transactions :
            tree.encryptRecord(t.hash)
        merkel_hash = tree.rootHash

        header = self.previous_hash + self.nonce+\
                merkel_hash + self.timestamp
        h = SHA256.new()
        hash_value = h.new(h.new(header).digest()).hexdigest()[::-1]
        return  int(hash_value[0:self.difficulty],16) == 0 



if __name__ == '__main__':
    ''' Α dummy mining test''' 
    x = [Transaction('asdf','asdf',10,[],b'0x23423423') for i in range(5)]
    y = Block(0,b'0x234234134',)
    y.transactions = x
    y.mine()
    print(y.validate())