from block import Block
from broadcast import broadcast_block
from Crypto.Hash import SHA256
from time import time
from pymerkle import MerkleTree
from random import randint
from state import state

class Blockchain : 
    def __init__(self):
        '''
        transactions (imported from state): list of transactions not in block
        chain: the list (chain) of blocks. chain[0] = genesis block
        
        miner implementation and calls are also implemented here

        '''
        self.chain = []
        self.genesis_block = Block(0, [], '0', time())
        self.genesis_block.hash = self.genesis_block.calculate_hash()
        
    
        
    def add_block(self, block, nonce):
        '''
        after successful transaction mining, all the transactions
        that were successfully mined will be put in one block,
        which will be added to the chain then will be broadcast
        to everyone else.
        
        before we add it, we need to confirm that the previous_hash
        is indeed the previous one, and that the nonce (proof of work) is
        correct.
        
        note that the validation process is different than validate_block(), 
        because validate_block() is about blocks that are already in the chain
        and used in validate_chain()
        '''
        if (block.validate_block_hash_value() and (block.previous_hash == self.chain[-1].hash)):
            self.chain.append(block)
            return True
        
        return False
        
    def add_transaction(self, tx):
        '''
        add a new unconfirmed transaction to the list
        '''
        state.transactions.append(tx)
        
        
    def mine_unconfirmed_transactions(self):
        '''
        mine the unconfirmed transactions.
        for every transaction that you find the nonce,
        broadcast the block to everyone and confirm it
        by making an API call
        '''
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
            header = self.previous_hash + nonce +\
                  merkle_hash + self.timestamp
            h = SHA256.new()
            # apply hashing 2 times 
            hash_value = h.new(h.new(header).digest()).hexdigest()
            hash_value = hash_value[::-1] # reverse, little endian
            if int(hash_value[0:self.difficulty],16) == 0 :
                solved = True
                break
        if solved :
            new_block = Block(self.chain[-1].index + 1, state.transactions, self.chain[-1].hash, nonce)
            new_block.hash = hash_value.encode()
            new_block.header = header
            broadcast_block(new_block) #implemented in broadcast.py
            state.transactions = []
            self.add_block(new_block, nonce)
            return 0
        else : 
            self.mine()
            
    def validate_block(self,block, i):
        """ check if prev_hash and computed hash are valid .
        i is the position of the block in the chain
        """
        return (
            self.chain[i-1].hash == block.prev_hash and 
            block.validate()
        )

    def validate_chain(self):
        '''
        validate the blockchain.
        the blocks to be validated are only these in the chain
        (not these waiting to be added)
        '''
        for i in range(1,len(self.chain)):
            if not self.validate_block_in_chain(self.chain[i], i):
                return False 
            
        #validate that the first block is the genesis block
        if self.blockchain[0].index == 0:
            return True
        