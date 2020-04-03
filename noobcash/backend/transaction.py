from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
import simplejson as json
from state import state
import base64

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
        signature = None, id = None, outputs = None):
        
        #from state import state

        self.sender = sender
        self.receiver = receiver
        self.amount = float(amount) 
        self.inputs = inputs 
        self.outputs = [] # outputs are assigned post creation
        
        self.id = id
        self.signature = signature

        self.calculate_hash()

    def to_json(self):
        # use obj dict to convert to json 
        return json.dumps(self.__dict__)

    def calculate_hash(self):    
        self.id = SHA256.new(self.to_json().encode()).hexdigest()

    def sign_transaction(self):
        self.signature = base64.b64encode(str((state.key.sign(3,''))[0]).encode())

    def verify_signature(self):

        rsa_key = RSA.importKey(self.sender.encode())
        # use PKCS1 instead of plain RSA to avoid security vulnerabilities
        return rsa_key.verify(3, (int(base64.b64decode(self.signature)),))


    """ Static methods, not object specific, belong to the class s"""
    
    @staticmethod
    def get_node_id(public_key):
        '''
        returns the ID of the node that
        has as public key the public_key
        '''
        for node in state.nodes.items():
            if (node[1]['pubkey'] == public_key):
                return node[0]
            
        return False
    
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

        sender_id = Transaction.get_node_id(t.sender)
        receiver_id = Transaction.get_node_id(t.receiver)

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
        for utxo in pending_removed: 
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

        state.add_utxo(receiver_id, t.outputs[0])
        state.add_utxo(sender_id, t.outputs[1])
        
        # save transaction
        state.transactions.append(t)

        # mine if block is full 
        if (len(state.transactions) == CAPACITY):
            state.mine_block()
        
        return (t,True)
    
    @staticmethod
    def create_transaction(receiver_key, amount):
        """
            - Create a transaction for broadcasting 
            - update transaction listg
            - update utxos 
            - mine if necessary W
        """
        sender_key = state.pub.exportKey().decode()
        sender_id = Transaction.get_node_id(sender_key)
        receiver_id = Transaction.get_node_id(receiver_key)
        inputs = []

        coins = 0
        for utxo in state.utxos[sender_id]:
            coins += float(utxo['amount'])
            inputs.append(utxo['id']) #!this needs to be determined!
            if coins >= amount :
                break 

        t = Transaction(sender_key, receiver_key, amount, inputs)
        t.sign_transaction()

        t.outputs = [{
            'trans_id': t.id,
            'id' : t.id + ':0',
            'owner': t.receiver,
            'amount': t.amount
        }, {
            'trans_id': t.id,
            'id' : t.id + ':1',
            'person': t.sender,
            'amount': coins - t.amount
        }]

        state.add_utxo(receiver_id, t.outputs[0])
        state.add_utxo(sender_id, t.outputs[1])

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


