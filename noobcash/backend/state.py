from Crypto.PublicKey import RSA
from Crypto import Random
from block import Block
from blockchain import Blockchain
import simplejson as json
import requests
#from blockchain import Blockchain

class State :
    """
        blockchain : our version of the blockchain :: list(B)
        utxos : unspent trans for all nodes :: utxos[owner] = {trans_id, id, owner, amount}
        nodes : node information :: nodes[id] = {ip,port,pub}
        transactions : list of verified transactions not in a block :: 
        key: RSA key including private and public key :: string
        pub : RSA public part of key :: string

    """

    def __init__(self):
       
        self.generate_wallet()
        self.blockchain = Blockchain()
        self.utxos = {}
        self.nodes = {}
        self.transactions = []
   
    
    def connect_to_coordinator(self, coordinator_ip, coordinator_port, client_ip, client_port):
        """
        send a POST request for connection to the
        coordinator.
        returns the blockchain 
        """
        response = requests.post(f'http://{coordinator_ip}:{coordinator_port}/register_node',\
                      json={f'"ip":"{client_ip}"',f'"port":"{client_port}"',\
                            f'"pubkey":"{self.pub}"'})
        if (response.status_code == 200):
            self.generate_chain_from_json_dump(response.json()['chain'])
        
        '''
        todo: sync the newly inserted node to every other network node,
        using register_node_with_another_existing_node() for
        all nodes linked to coordinator
        '''


    def generate_chain_from_json_dump(self, json_chain):
        '''
        generate the chain from json dump and validate it
        '''
        new_blockchain = Blockchain()
        chain = json.loads(json_chain)
        for json_block in chain['chain']:
            info = json.loads(json_block)
            block = Block(info['index'], info['transactions'], info['prev_hash'], info['nonce'])
            block.put_extra_info(info)

        new_blockchain.append(block)
        if len(new_blockchain) == int(chain['length']) and new_blockchain.validate_chain():
            self.blockchain = new_blockchain
            return True
        
        return False
        

    def generate_wallet(self): 
        random_generator = Random.new().read 
        self.key  = RSA.generate(2048,random_generator)
        #key is an RSA key object, the private key is not visible
        self.pub = self.key.publickey

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