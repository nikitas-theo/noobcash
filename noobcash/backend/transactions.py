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

    @staticmethod
    def validate_transaction(json_trans):
        t = Transaction(**json.loads(json_trans))
        budget = 0
        if not verify_signature():
            #raise Exception('invalid signature')
            return False

        for input_utxo in t.inputs: #ara to bob einai apla to id
            flag=False          
            for utxo in state.utxos[t.sender]: 
            #maybe check all and check of it's his
                if utxo['id'] == input_utxo['id'] and utxo['person'] == t.sender: # and utxo['who'] == self.sender:
                    flag=True
                    budget+=utxo['amount']
                    state.remove_utxo(utxo)
                    break
            if not flag:
                return False
                # raise Exception('missing transaction inputs')

        if budget < t.amount:
            return False
            #raise Exception('MONEY 404')

        # create outputs
        t.outputs = [{
            'id': t.id,
            'person': t.recepient,
            'amount': t.amount
        }, {
            'id': t.id,
            'person': t.sender,
            'amount': budget - t.amount
        }]

        #we need to replace the sender's utxo and add to the receiver's one
        state.add_utxo(t.sender, t.outputs[1])
        state.add_utxo(t.recepient, t.outputs[0])

        state.transaction.append(t) #can you do that? let's hope so

        return True

        #return t???? UGGGH

    def create_transaction(receiver, amount):
        sender = state.pub
        inputs =[]

        for i in state.utxos[sender]:
            inputs.append(i)
         
        t = Transaction(sender=sender, receiver=receiver, amount=amount, inputs=inputs)

        t.sign()

        t.outputs = [{
            'id': t.id,
            'person': t.recepient,
            'amount': t.amount
        }, {
            'id': t.id,
            'person': t.sender,
            'amount': budget - t.amount
        }]

        state.add_utxo(t.sender, t.outputs[1])
        state.add_utxo(t.recepient, t.outputs[0])

        state.transaction.append(t)
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


