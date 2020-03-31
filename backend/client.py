from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
 # doc: https://www.dlitz.net/software/pycrypto/api/current/Crypto.PublicKey.RSA._RSAobj-class.html 



class Client :
    def __init__(self):
        self.wallet = Wallet()
        self.id = 47 
        # we need to communicate with the bootstrap node 
        self.blockchain = []
        self.nodes = [{'ip' : '', 'port' : '', 'pub' : ''}]
    