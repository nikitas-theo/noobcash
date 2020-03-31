from Crypto import Random
from Crypto.Hash import SHA256, binascii
from random import randint
from pymerkle import MerkleTree
from time import time
import binascii
class Block :
    def __init__(self,index, prev_hash, nonce = -1):
        self.dificulty = 2 # number of leading zeros required in Hex
        self.index = index 
        self.timestamp = time()
        self.transactions = []
        self.previous_hash = prev_hash
        self.size = 0 
        self.capacity = 20 # must be even number
    
    def mine(self):
        " Proof Of Work"
        
        # Create hash of transactions with a Merkel Tree
        tree = MerkleTree()
        for t in transactions :
            tree.encryptRecord(t.hash)
        merkel_hash = tree.rootHash
        
        # 32-bit sized nonce 
        for nonce in xrange(2 << 32):
            # header consists of prev_hash, nonce, merkel of transactions
            # and the block timestamps. More could be added, 
            # see: https://en.bitcoin.it/wiki/Block_hashing_algorithm
            
            header = self.previous_hash + hex(nonce) + 
                    merkel_hash + hex(self.timestamp)
            h = SHA256.new()
            # apply crypto func 2 times 
            hash_value = h.new(h.new(header.encode().digest()))
            hash_value = h.hexdigest()[::-1] # reverse, little endian
            if int(hash_value[0:self.difficulty],16) == 0 :
                solved = True
                break
        if solved :
            self.nonce = nonce
            self.hash = curr_hash
            self.header = header
            return 0
        else 
            self.mine()

