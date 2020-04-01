from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
from state import *
class Transaction :
    def __init__(self,sender,receiver,amount,inputs,hash = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount 
        self.inputs = inputs
        self.ouputs = []
        
        # hash obj
        if hash == None :
            self.hash = SHA256.new(
                self.sender + self.recepient + str(self.amount).encode() + self.input
            )
            self.id = hash.hexdigest()
        else : 
            self.hash = hash
            self.id = hash 

    def sign(self):

        signer = PKCS1_v1_5.new(state.key)
        self.signature = signer.sign(self.hash)

    def verify_signature(self):

        verifier = PKCS1_v1_5.new(self.sender) 
        # use PKCS1 instead of plain RSA to avoid security vulnerabilities
        return verifier.verify(self.hash, self.signature)


    def validate_transaction(self):
        budget = 0
        if not verify_signature():
            #raise Exception('invalid signature')
            return False

        for bob in self.inputs: #ara to bob einai apla to id
            flag=False          
            for utxo in State.utxos: 
            #maybe check all and check of it's his
                if utxo['id'] == bob: # and utxo['who'] == self.sender:
                    flag=True
                    budget+=utxo['amount']
                    State.remove_utxo(utxo)
                    break
            if not flag:
                return False
                # raise Exception('missing transaction inputs')

        if budget < self.amount:
            return False
            #raise Exception('MONEY 404')

        # create outputs
        self.outputs = [{
            'id': self.id,
            'person': self.recepient,
            'amount': t.amount
        }, {
            'id': self.id,
            'person': self.sender,
            'amount': budget - self.amount
        }]

        #we need to replace the sender's utxo and add to the receiver's one
        State.add_utxo(self.sender, self.outputs[1])
        State.add_utxo(self.recepient, self.outputs[0])

        State.transaction.append(self) #can you do that? let's hope so

        return True

        #return self???? UGGGH

    def create_transaction(recipient, amount):

        t = Transaction(sender=sender, receiver=receiver, amount=amount, inputs=inputs)

        t.sign()

        return t


 





if __name__ == '__main__':
    hash  = SHA256.new(b'234234223')
    random_generator = Random.new().read 
    key  = RSA.generate(2048,random_generator)
    pub = key.publickey()
    signer = PKCS1_v1_5.new(key)
    sig = signer.sign(hash)
    verifier = PKCS1_v1_5.new(pub) 
    print(verifier.verify(hash, sig))


