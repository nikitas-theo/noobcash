from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
import json

from state import *

class Transaction :
    """ sender : pub key, string
        receiver : pub key, string
        amount : float 
        inputs : list of transaction ids 
        outpus : list of utxos
        id : hex number, transaction hash
        hash : hash object 
        signature : byte string
    """
    def __init__(self,sender,receiver,amount,inputs,
        signature = None, id = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = float(amount) 
        self.inputs = inputs 
        self.ouputs = [] # outputs are assigned post creation
        
        self.id = id
        self.signature = signature

        self.calculate_hash()

    def to_json(self):
        # use obj dict to convert to json 
        return json.dumps(self.__dict__)

    def calculate_hash(self):    
        self.hash = SHA256.new(self.to_json.encode())
        self.id = self.hash.hexdigest()

    def sign(self):
       
        key = RSA.importKey(state.private)
        signer = PKCS1_v1_5.new(key)
        self.signature = signer.sign(self.hash)

    def verify_signature(self):

        rsa_key = RSA.importKey(self.sender.encode())
        verifier = PKCS1_v1_5.new(rsa_key) 
        # use PKCS1 instead of plain RSA to avoid security vulnerabilities
        return verifier.verify(self.hash, self.signature)


    """
        The following methods are static, they belong to the class
        and are not object specific 
    """

    @staticmethod
    def validate_transaction(json_trans):
        """ 
            validate incoming transaction,
            update transaction list,
            update corresponding utxos 

            return Bool 
            
        """ 

        # load transaction object from json string 
        t = Transaction(**json.loads(json_trans)) 

        
        if not t.verify_signature():
            return False 

       
        budget = 0
        pending_removed = []
        for utxo_input in t.inputs: 
            found = False          
            for utxo in state.utxos[t.sender]: 
            
                if utxo['id'] == utxo_input and utxo['owner'] == t.sender: 
                    found = True
                    budget += utxo['amount']
                    pending_removed.append(utxo)
                    break
            
            if not found:
                return False
            
        if budget < t.amount:
            return False


        # remove all spent transactions    
        for utxo in pending_removed : 
            state.remove_utxo(utxo)

        # create outputs

        t.outputs = [{
            'trans_id': t.id,
            'id' : t.id + ":0",
            'owner': t.receiver,
            'amount': t.amount
        }, {
            'trans_id': t.id,
            'id' : t.id + ":1",
            'owner': t.sender,
            'amount': budget - t.amount
        }]

        state.add_utxo(t.outputs[0])
        state.add_utxo(t.outputs[1])
        
        # save transaction
        state.transaction.append(t) 

        # bool value indicating a verified transaction
        return True
    
    @staticmethod
    def create_transaction(receiver, amount):

        sender = state.pub
        inputs = []

        coins = 0
        for utxo in state.utxos[sender]:
            coins += utxo['amount']
            inputs.append(utxo['id'])
            if coins >= amount :
                break 

        t = Transaction(sender, receiver, amount, inputs)
        t.sign()

        t.outputs = [{
            'trans_id': t.id,
            'id' : t.id + '0',
            'owner': t.recepient,
            'amount': t.amount
        }, {
            'trans_id': t.id,
            'id' : t.id + '1',
            'person': t.sender,
            'amount': coins - t.amount
        }]

        state.add_utxo(t.outputs[0])
        state.add_utxo(t.outputs[1])

        state.transaction.append(t)
        return t


 





if __name__ == '__main__':
    hash  = SHA256.new(b'234234223')
    print(hash.hexdigest())
    random_generator = Random.new().read 
    key  = RSA.generate(2048,random_generator)
    pub = key.publickey()
    signer = PKCS1_v1_5.new(key)
    sig = signer.sign(hash)
    print(sig)
    verifier = PKCS1_v1_5.new(pub) 
    print(verifier.verify(hash, sig))


