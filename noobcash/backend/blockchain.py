from block import Block

class Blockchain : 
    def __init__(self):
        self.chain = []

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