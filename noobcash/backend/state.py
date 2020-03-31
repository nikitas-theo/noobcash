from Crypto.PublicKey import RSA
class Client :
    def __init__(self):
        self.wallet = Wallet()
        self.id = 47 
        # we need to communicate with the bootstrap node 
        self.blockchain = []
        self.nodes = [{'ip' : '', 'port' : '', 'pub' : ''}]

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