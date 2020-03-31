from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
from random import randint
from time import time
from pymerkle import MerkleTree

class Wallet:
    def __init__(self):
        """ generate wallet """ 
        random_generator = Random.new().read 
        self.key  = RSA.generate(2048,random_generator)
        #key is an RSA key object, the private key is not visible
        self.pub = self.key.publickey
        self.K = randint(100)
        # random num, it's ignored    

    def sign_transaction(self,trans):
        sig = self._key.sign(trans,self.K)
        return sig; 
    

class Transaction :
    def __init__(self,sender,receiver,amount,hash_value):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount 
        self.hash = hash_value


        
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
        # 32 bit size nonce 
        
        # Create hash of transactions with a Merkel Tree
        tree = MerkleTree()
        for t in transactions :
            tree.encryptRecord(=t)
        merkel_hash = tree.rootHash


        for nonce in xrange(2 << 32):record
            # header consists of prev_hash, nonce, merkel of transactions
            # and the block timestamps. More could be added, 
            # see: https://en.bitcoin.it/wiki/Block_hashing_algorithm
            
            header = self.previous_hash + nonce + 
                    merkel_hash + self.timestamp
            
            h = SHA256.new()
            h.update(header) 
            hash_value = h.hexdigest()
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

    def validate_hash(self):
        """ validate proof of work """
        tree = MerkleTree()
        for t in transactions :
            tree.encryptRecord(record=t)
        merkel_hash = tree.rootHash

        header = self.previous_hash + self.nonce + 
                    merkel_hash + self.timestamp
        
         
        h = SHA256.new()
        h.update(header) 
        hash_value = h.hexdigest()
        return  int(hash_value[0:self.difficulty],16) == 0

class Blockchain : 
    def __init__(self):
        self.block_capacity = 10
        self.chain = []
        # actual blochain 
        self.transactions = [] 
        # list of transactions that will be added on the next block

        self.chain.append(Block(index = 0 ,prev_hash = 1, nonce = 0))
        # create genesis block 


    def validate_chain(self):
        for block in self.blockchain: 
            if block.index == 0 : 
                return True 
            if not block.validate():
                return False 
        
    def validate_block(self,block):
        """ check if prev_hash and computed has are valid 
        """
        return (
            self.blockchain[block.index-1] == block.prev_hash and 
            block.validate_hash()
        )