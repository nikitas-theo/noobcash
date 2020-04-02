from time import time

from pymerkle import MerkleTree
from Crypto.Hash import SHA256
import simplejson as json
from state import state
from transactions import Transaction

CAPACITY = 10
DIFFICULTY = 4
class Block :
    """ 

        block index, the unique ID of the block
        timestamp : current Unix time 
        transactions : list of CONFIRMED transactions in block 
        previous_hash : hash of previous block in blockchain , bytestring 
        nonce : solution of PoW
        size : curr number of transactions 

        header : header of block, bytestring
        hash: the hash of the block
        difficulty :  number of leading zeros required in Hex
        capacity : number of transactions required for mining 

    """

    def __init__(self, index, transactions, prev_hash, nonce =  None):
        
        self.difficulty = DIFFICULTY 
        self.capacity = CAPACITY # number of transactions 
        '''
        shouldnt we initialize the header  and the hashas well?
        '''
        self.header = 'a'
        self.hash = 'b'
        self.index = index 
        self.timestamp = str(time()).encode()
        self.transactions = transactions
        self.previous_hash = prev_hash
        self.nonce = nonce
        self.size = 0 
        
    def put_extra_info(self,j):
        '''
        fill the extra attributes from the json object j to the block
        '''
        self.difficulty = j['difficulty']
        self.capacity = j['capacity']
        self.header = j['header']
        self.hash = j['hash']
        self.timestamp = j['timestamp']
        self.size = j['size']
        

    def validate_block_hash_value(self):
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
    
    def to_json(self):
        # use obj dict to convert to json, needed for broadcasting
        return json.dumps(self.__dict__)
    
    def calculate_hash(self):    
        self.hash = SHA256.new(self.to_json.encode())
        self.id = self.hash.hexdigest()

if __name__ == '__main__':
    ''' Α dummy mining test''' 
    x = [Transaction('asdf','asdf',10,[],b'0x23423423') for i in range(5)]
    y = Block(0,b'0x234234134',)
    y.transactions = x
    y.mine()
    print(y.validate())