from Crypto.PublicKey import RSA
from Crypto import Random

#from blockchain import Blockchain
from blockchain import Blockchain

class State :
    """


        blockchain : our version of the blockchain
        utxos : unspent trans for all nodes
        nodes : node information
        transactions : list of valid transactions not in a block 
        key: RSA key including private and public key :: string
        pub : RSA public part of key :: string
    """

    def __init__(self):
       
        self.generate_wallet()
        self.blockchain = Blockchain()
        self.utxos = {}
        self.nodes = {}

        # utxos[owner] = {trans_id, id, owner, amount}
        # nodes[id] = {ip, port, pub }

        self.transactions=[] 

    def generate_wallet(self): 
        random_generator = Random.new().read 
        self.key  = RSA.generate(2048,random_generator)
        #key is an RSA key object, the private key is not visible
        self.pub = self.key.publickey

    def add_participant(self,pubkey, ip, port, id):
        nodes[id] = {'ip' : ip , 'port' : port, 'pub' : pubkey}
 
    def remove_utxo(self, utxo):
        self.utxos[utxo['owner']].remove(utxo)

    def add_utxo(self, utxo):
        self.utxos[utxo['owner']].append(utxo)
    
    def wallet_balance(self): 
        balance = 0
        for u in self.utxo[self.pub]: 
            balance+=self.utxo['amount']
        return balance 

# this is the global state exposed to all modules
state = State()


