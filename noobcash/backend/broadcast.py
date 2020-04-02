
# TODO: Define broadcasting 
"""
    How do we receive a block or a transaction? 
    Need to specify communication

"""
import simplejson as json
from block import Block
from state import state
from transactions import Transaction
from Crypto.PublicKey import RSA
from Crypto import Random

#from blockchain import Blockchain
from blockchain import Blockchain

from flask import Flask, request
import requests


app = Flask(__name__)

@app.route('/receive_block', methods=['POST'])
def receive_block(json_block):
    '''
    check if the proof is valid (if the hash is correct)
    and if the previous hash of the block is the previous
    hash of the chain.
    then move on to add the received block in the chain.
    
    right after the block is added to the chain, remove
    any transaction from the list transactions[]
    that is both included in the list
    transactions[] of state and in the block.
    '''
    info = json.loads(json_block)
    block = Block(info['index'], info['transactions'], info['prev_hash'], info['nonce'])
    block.put_extra_info(info)
    
    '''
    todo: this might need to involve proof of work
    instead of hash
    
    we use the length of the chain as index, because the function
    will use that index minus one for the previous block validation
    '''
    if (not state.blockchain.validate_block(block, len(state.blockchain.chain))):
        return False
    
    state.blockchain.chain.append(block)

    '''
    remove transaction from transactions not in block
    '''

    for block_transaction in block.transactions:
        for state_transaction in state.transactions:
            if (state_transaction.hash == block_transaction.hash):
                state.transactions.remove(state_transaction)
                
                
    return True

    
@app.route('/receive_transaction', methods=['POST'])
def receive_transaction(json_trans):
    '''
    as happening with json_block, we validate the transaction
    we just received, by calling validate.transaction()
    '''
    if (Transaction.validate_transaction(json_trans)):
        return True
    
    return False
    
@app.route('/receive_other_node_info', methods=['POST'])
def receive_other_note_info(json_nodes):
    '''
    as happening with json_block, we validate the transaction
    we just received, by calling validate.transaction()
    '''
    nodes = json.loads(json_nodes)
    state.nodes = nodes
    
    return True
    

@app.route('/chain',methods=['GET'])
def get_chain():
    '''
    get chain, in order to sync new nodes with the blockchain.
    after that, they have to validate the chain by themselves,
    calling validate_chain()
    '''
    chain_data = []
    for block in state.blockchain.chain:
        chain_data.append(block.__dict__)
    return json.dumps({"length": len(chain_data), "chain": chain_data})


@app.route('/mine',methods=['GET'])
def mine_unconfirmed_transactions():
    '''
    todo: will give the instruction to mine unconfirmed
    transactions for the specific node
    '''
    pass

@app.route('/register_node', methods=['POST'])
def register_new_nodes():
    '''
    register the node of the peer node who has submitted a request
    and give them the blockchain
    '''
    node_ip = request.get_json()['ip']
    node_port = request.get_json()['port']
    node_pubkey = request.get_json()['pubkey']
    if (not node_ip or not node_port or not node_pubkey):
        return "Invalid", 400
    
    #create that node and put it in the dictionary of nodes
    maxid = max(state.nodes, key=int)
    new_id = maxid + 1
    state.nodes[new_id]['ip'] = node_ip
    state.nodes[new_id]['port'] = node_port
    state.nodes[new_id]['pubkey'] = node_pubkey
    
    #sync the new node with the blockchain, by broadcasting chain
    return get_chain()


@app.route('/register_with', methods=['POST'])
def communicate_with_all():
    '''
    when all nodes are in the state.nodes dictionary, tell
    every node about the existing nodes
    '''
    json_nodes = json.dumps(state.nodes)
    for node in state.nodes:
        #broadcast to everyone except sender
        if (node['pub'] == state.pub):
            continue
        ip = node["id"]
        port = node["port"]
        response = requests.post(f'http://{ip}:{port}/receive_other_node_info', json=json_nodes)
        if (response.status_code != 200):
            return False
    
    return True

def resolve_conflict():
    '''
    todo: implementation of consensus algorithm that can occur
    from the entrance of the new node being synced with another
    existing node
    '''
    pass
    
def index():
    return f'Hello world!'

@app.route('/broadcast_transaction', methods=['POST'])
def broadcast_transaction(transaction):
    '''
    broadcast the transaction to every other node
    '''
    # load transaction object from json string 
    json_trans = json.dumps(transaction.__dict__)
    for node in state.nodes:
        #broadcast to everyone except sender
        if (node['pub'] == state.pub):
            continue
        ip = node["id"]
        port = node["port"]
        response = requests.post(f'http://{ip}:{port}/receive_transaction', json=json_trans)
        if (response.status_code != 200):
            return False
        
    return True
    
@app.route('/new_transaction',methods=['POST'])
def new_transaction(receiver, amount):
    #creates t, the new transaction, and broadcasts it
    t = Transaction.create_transaction(receiver, amount)
    broadcast_transaction(t)
    return "Success", 201


@app.route('/broadcast_block', methods=['POST'])
def broadcast_block(block):
    '''
    broadcast the block in json mode when it is complete
    '''
    json_block = block.to_json()
    for node in state.nodes:
        #broadcast to everyone except sender
        if (node['pub'] == state.pub):
            continue
        ip = node["id"]
        port = node["port"]
        response = requests.post(f'http://{ip}:{port}/receive_block', json=json_block)
        if (response.status_code != 200):
            return False
        
    return True
    