from block import Block

class Blockchain : 
    def __init__(self):
        self.chain = []

    def validate_chain(self):
        for block in self.blockchain[1:]: 
            if not self.validate_block(block) :
                return False 
        return True
        
    def validate_block(self,block):
        """ check if prev_hash and computed has are valid 
        """
        return (
            self.blockchain[block.index-1] == block.prev_hash and 
            block.validate()
        )