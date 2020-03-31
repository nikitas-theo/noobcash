


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