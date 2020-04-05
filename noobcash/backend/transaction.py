from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto import Random
import simplejson as json
import base64
import state as State 
import config
import functools
from copy import deepcopy
print = functools.partial(print, flush=True)

class Transaction :
    """ sender : pub key :: string
        receiver : pub key :: string
        amount :: float 
        inputs : list of transaction ids :: list(string) 
        outpus : list of utxos 
        id : transaction hash :: hex string
        #?hash : transaction hash, but as a hash object :: SHA256 obj
        signature :: byte string 
    """

    def __init__(self,sender,receiver,amount,inputs,
        signature = None, id = None, outputs = None):
        

        self.sender = sender
        self.receiver = receiver
        self.amount = amount 
        self.inputs = inputs 
        self.outputs = [] # outputs are assigned post creation
        
        self.id = id
        self.signature = signature

    def to_json(self):
        # use obj dict to convert to json 
        return json.dumps(self.__dict__)

    def calculate_hash(self):    
        self.id = str(SHA256.new(self.to_json().encode()).hexdigest())

    def sign_transaction(self):
        hash_obj = SHA256.new(data = self.id.encode())
        rsa_key = State.state.key
        signer = PKCS1_v1_5.new(rsa_key)
        self.signature = base64.b64encode(signer.sign(hash_obj))

    def verify_signature(self):
        rsa_key = RSA.importKey(self.sender.encode())
        verifier = PKCS1_v1_5.new(rsa_key)
        hash_obj = SHA256.new(data = self.id.encode())
        return verifier.verify(hash_obj, base64.b64decode(self.signature))


    """ Static methods, not object specific, belong to the class"""

    @staticmethod
    def validate_transaction(t):
        #print('Requesting VALIDATE TRANSACTION lock', State.state.lock)
        State.state.lock.acquire()
        """ 
            - validate incoming transaction
            - update transaction list
            - update corresponding utxos 
            - mine if necessary  
            return :: tuple of (Transaction obj, Bool val)
        """ 
        # verify sig
        
        if not t.verify_signature():
            #print('Signature did not verify')
            State.state.lock.release()
            #print('Releasing VALIDATE TRANSACTION lock', State.state.lock)
            return (None,False)
        try : 
            coins = 0
            pending_removed = []
            for utxo_input in t.inputs: 
                found = False          
                for utxo in State.state.utxos[t.sender]: 
                
                    if utxo['id'] == utxo_input and utxo['owner'] == t.sender: 
                        found = True
                        coins += utxo['amount']
                        pending_removed.append(utxo)
                        break
                if not found:
                    raise Exception('Given input UTXO is not found in utxo records')
                    
            if coins < t.amount:
                raise Exception('Not enough UTXO coins in sender')
        except Exception as e:
            #print(str(e))
            #print('Releasing VALIDATE TRANSACTION lock', State.state.lock)
            State.state.lock.release()
            return (False)

        # remove all spent transactions    
        for utxo in pending_removed: 
            State.state.remove_utxo(utxo)

        # create outputs
        if (coins > t.amount):  
            t.outputs = [{
                'trans_id': t.id,
                'id' : t.id ,#+ ":0",
                'owner': t.receiver,
                'amount': t.amount
            }, {
                'trans_id': t.id,
                'id' : t.id ,#+ ":1",
                'owner': t.sender,
                'amount': coins - t.amount
            }]
            State.state.add_utxo(t.outputs[0])
            State.state.add_utxo(t.outputs[1])
        else:
            t.outputs = [{
                'trans_id': t.id,
                'id' : t.id ,#+ ":0",
                'owner': t.receiver,
                'amount': t.amount
            }]
            State.state.add_utxo(t.outputs[0])
        # save transaction
        State.state.transactions.append(t)
        #print('Releasing VALIDATE TRANSACTION lock', State.state.lock)
        State.state.lock.release()

   
        return True
    
    @staticmethod
    def create_transaction(receiver_key, amount):
        #print('Requesting CREATE TRANSACTION lock', State.state.lock)
        State.state.lock.acquire()
        """
            - Create a transaction for broadcasting 
            - update transaction listg
            - update utxos 
        """
        sender_key = State.state.pub
        inputs = []

        coins = 0
        pending_removed = []
        for utxo in State.state.utxos[sender_key]:
            coins += utxo['amount']
            inputs.append(utxo['id'])
            pending_removed.append(utxo)
            if coins >= amount :
                break 
        
        if coins < amount:
            #print('Not enough UTXO coins in wallet, requested ', amount, 'but have', coins)
            #print('Releasing CREATE TRANSACTION lock', State.state.lock)
            State.state.lock.release()
            return (False)

        # remove all spent transactions    
        for utxo in pending_removed: 
            State.state.remove_utxo(utxo)

        
        t = Transaction(sender = sender_key,receiver = receiver_key,
            amount =  amount,inputs =  inputs)
        t.calculate_hash()
        t.sign_transaction()

        # create outputs
        if (coins > t.amount):  
            t.outputs = [{
                'trans_id': t.id,
                'id' : t.id ,#+":0",
                'owner': t.receiver,
                'amount': t.amount
            }, {
                'trans_id': t.id,
                'id' : t.id ,#+":1",
                'owner': t.sender,
                'amount': coins - t.amount
            }]
            State.state.add_utxo(t.outputs[0])
            State.state.add_utxo(t.outputs[1])
        else:
            t.outputs = [{
                'trans_id': t.id,
                'id' : t.id ,#+":0",
                'owner': t.receiver,
                'amount': t.amount
            }]
            State.state.add_utxo(t.outputs[0])

        State.state.transactions.append(t)
        #print('Releasing CREATE TRANSACTION lock', State.state.lock)
        State.state.lock.release()
        
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


