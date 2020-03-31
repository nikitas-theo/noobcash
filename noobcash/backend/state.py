from Crypto.PublicKey import RSA
from Crypto import Random

class State :
    def __init__(self):
        """ generate wallet """ 
        random_generator = Random.new().read 
        self.key  = RSA.generate(2048,random_generator)
        #key is an RSA key object, the private key is not visible
        self.pub = self.key.publickey

        # we need to communicate with the bootstrap node 
        self.blockchain = []
        self.nodes = [{'ip' : '', 'port' : '', 'pub' : ''}]
