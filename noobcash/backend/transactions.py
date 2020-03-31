from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random

class Transaction :
    def __init__(self,sender,receiver,amount,inputs,hash = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount 
        self.inputs = inputs
        
        # we hash all the input to create the transaction (a hash)
        self.id = hash if hash != None else SHA256.new(
            self.sender + self.recepient + str(self.amount).encode() + self.input
        )
    def sign(self):
        signer = PKCS1_v1_5.new(self.sender)

    def verify_signature(self):
        verifier = PKCS1_v1_5.new(self.sender) 
        # use PKCS1 instead of plain RSA to avoid security vulnerabilities
        return verifier.verify(self.id, self.signature)


if __name__ == '__main__':
    random_generator = Random.new().read 
    key  = RSA.generate(2048,random_generator)
    pub = key.publickey()
    x = key.encrypt(b'x32823',42)

    verifier = PKCS1_v1_5.new(pub(
    verifier.verify(x, )
