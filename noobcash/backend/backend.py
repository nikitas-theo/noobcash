

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

class Blockchain : 
    def __init__(self):
        self.block_capacity = CAPACITY
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