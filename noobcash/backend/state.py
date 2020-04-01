from Crypto.PublicKey import RSA
from Crypto import Random

#from blockchain import Blockchain
import blockchain

class State :
    def __init__(self):
        """ generate wallet """ 
        random_generator = Random.new().read 
        self.key  = RSA.generate(2048,random_generator)
        #key is an RSA key object, the private key is not visible
        self.pub = self.key.publickey

        # we need to communicate with the bootstrap node 
        self.blockchain = Blockchain()
        #self.transactions= [] either here on in blockchain
        self.participants = {} #tuples
        self.participants_num = 0
        self.utxos = []
        self.gen_block = None
        self.gen_utxos = []

        self.total_blocks = 0 #vasika xreiazetai auto?
        self.nodes = [{'ip' : '', 'port' : '', 'pub' : ''}]

    def add_participant(pubkey, host, id):
    	self.participants[pubkey] = {host, id} #uuhm ti grafw?
    	self.participants_num+=1

    def remove_utxo(utxo):
        utxos.remove(utxo)

    def wallet_balance(public_key): 
        balance=0
        for utxo in utxos:
            if utxo.sender == public_key: 
                balance+=utxo.amount
        return amount