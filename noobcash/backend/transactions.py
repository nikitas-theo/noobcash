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
        
        # hash obj
        if hash == None :
            self.hash = SHA256.new(
                self.sender + self.recepient + str(self.amount).encode() + self.input
            )
            self.id = hash.hexdigest()
        else : 
            self.hash = hash
            self.id = hash 
    def sign(self,private_key):
        # TODO: private_key should be provided by state 
        signer = PKCS1_v1_5.new(private_key)
        self.signature = signer.sign(self.hash)

    def verify_signature(self):

        verifier = PKCS1_v1_5.new(self.sender) 
        # use PKCS1 instead of plain RSA to avoid security vulnerabilities
        return verifier.verify(self.hash, self.signature)


if __name__ == '__main__':
    hash  = SHA256.new(b'234234223')
    random_generator = Random.new().read 
    key  = RSA.generate(2048,random_generator)
    pub = key.publickey()
    signer = PKCS1_v1_5.new(key)
    sig = signer.sign(hash)
    verifier = PKCS1_v1_5.new(pub) 
    print(verifier.verify(hash, sig))


