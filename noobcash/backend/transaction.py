from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
import simplejson as json

from config import * 

class Transaction :
    """ sender : pub key :: string
        receiver : pub key :: string
        amount :: float 
        inputs : list of transaction ids :: list(string) 
        outpus : list of utxos 
        id : transaction hash :: hex number
        hash : transaction hash, but as a hash object :: SHA256 obj
        signature :: byte string 
    """

    def __init__(self,sender,receiver,amount,inputs,
        signature = None, id = None):
        
        from state import state

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

    def sign_transaction(self):
       
        signer = PKCS1_v1_5.new(state.key)
        self.signature = signer.sign(self.hash)

    def verify_signature(self):

        rsa_key = RSA.importKey(self.sender.encode())
        verifier = PKCS1_v1_5.new(rsa_key) 
        # use PKCS1 instead of plain RSA to avoid security vulnerabilities
        return verifier.verify(self.hash, self.signature)


    """ Static methods, not object specific, belong to the class s"""
    @staticmethod
    def validate_transaction(json_trans):
        """ 
            - validate incoming transaction
            - update transaction list
            - update corresponding utxos 
            - mine if necessary  
            return :: tuple of (Transaction obj, Bool val)
        """ 
        # load and verify sig
        t = Transaction(**json.loads(json_trans)) 
        if not t.verify_signature():
            return (None,False)

       
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
                return (None,False)
        if budget < t.amount:
            return (None,False)


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
        state.transactions.append(t)

        # mine if block is full 
        if (len(state.transactions) == CAPACITY):
            state.mine_block()
        
        return (t,True)
    
    @staticmethod
    def create_transaction(receiver, amount):
        """
            - Create a transaction for broadcasting 
            - update transaction listg
            - update utxos 
            - mine if necessary W
        """
        sender = state.pub
        inputs = []

        coins = 0
        for utxo in state.utxos[sender]:
            coins += utxo['amount']
            inputs.append(utxo['id'])
            if coins >= amount :
                break 

        t = Transaction(sender, receiver, amount, inputs)
        t.sign_transaction()

        t.outputs = [{
            'trans_id': t.id,
            'id' : t.id + ':0',
            'owner': t.recepient,
            'amount': t.amount
        }, {
            'trans_id': t.id,
            'id' : t.id + ':1',
            'person': t.sender,
            'amount': coins - t.amount
        }]

        state.add_utxo(t.outputs[0])
        state.add_utxo(t.outputs[1])

        state.transactions.append(t)
        
        # mine if block is full 
        if (len(state.transactions) == CAPACITY):
            state.mine_block()
        
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

