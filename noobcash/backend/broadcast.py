from Crypto.PublicKey import RSA
from Crypto import Random
from flask import Flask, request, Blueprint, make_response
import requests
import simplejson as json


from block import Block
import state as State
from transaction import Transaction
import config
app = Flask(__name__)



#------------------------------------------------------------
# BROADCASTING

def broadcast_block(block,node_id = None) :
    json_block = block.to_json()
    return broadcast(json_block,'receive_block',node_id)

def broadcast_transaction(t,node_id = None ) :
    json_t = t.to_json()
    return broadcast(json_t,'receive_transaction',node_id)


def broadcast(json_obj,rest_point,node_id = None):
    """ Broadcast object to network """
    if node_id == None :
        broadcast_nodes = list(State.state.nodes.values()) 
    else :
        broadcast_nodes = [State.state.nodes[node_id]]

    for node in broadcast_nodes:
        #broadcast to everyone except sender
        if (node['pub'] == State.state.pub):
            continue
        ip = node["ip"]
        response = requests.post(f'{ip}/{rest_point}', json=json_obj)
        if (response.status_code != 200):
            return False
    return True


def broadcast_nodes_info():
    """
    when all nodes are in the state.nodes dictionary,
    notify all nodes about the others
    """
    json_obj = json.dumps({'chain' : [b.to_json() for b in State.state.chain] , 
                           'utxos' : State.state.utxos, 
                           'transactions' : [t.to_json() for t in State.state.transactions],
                           'nodes' : State.state.nodes})


    ret = broadcast(json_obj,'receive_info')  
    for node in State.state.nodes.values():
        if node['pub'] == State.state.pub : 
            continue 
        new_transaction(node['pub'],100)


def new_transaction(receiver, amount,new_id = None):
    #creates t, the new transaction, and broadcasts it
    t = Transaction.create_transaction(receiver, amount)
    return broadcast_transaction(t,new_id)

# ------------------------------------------



API_communication = Blueprint('API_communication',__name__)

@API_communication.route('/receive_block', methods=['POST'])
def receive_block():
    json_string = request.get_json()
    block =  Block(**json.loads(json_string))
    # pass to Blockchain to add block
    return State.state.add_block(block)

    
@API_communication.route('/receive_transaction', methods=['POST'])
def receive_transaction():
    # Call static method, object creation is handled in function
    json_string = request.get_json()
    t,return_val = Transaction.validate_transaction(json_string)
    print(return_val)
    return make_response("OK",200)
    

# We receive a chain, this is in a different senario than the request_chain function
@API_communication.route('/receive_info',methods=['POST'])
def receive_info():
    json_obj = request.get_json()
    obj_dict = json.loads(json_obj)
    block_list = obj_dict['chain']
    # we also receive transactions we might have missed 
    # this is the init so we do not validate!

    if State.state.chain != [] and State.state.transactions != []:
        return make_response('Bad Init',500)

    transactions = obj_dict['transactions']
    utxos = obj_dict['utxos']
    nodes = obj_dict['nodes']
    State.state.nodes = nodes
    for utxo in utxos.keys():
        utxos[utxo] = list(utxos[utxo])

    State.state.transactions =  [Transaction(**json.loads(t)) for t in transactions]
    State.state.chain = [Block(**json.loads(block)) for block in block_list]
    for b in State.state.chain :
        b.transactions = [Transaction(**json.loads(t)) for t in b.transactions]
    State.state.utxos = utxos 

    return make_response('OK',200)

# All necessary communication for a new node to enter the network 
@API_communication.route('/register_node', methods=['POST'])
def register_node():
    '''
    An incoming node posts a request to enter the network 
    - Handle request and post in return 
    '''
    data = json.loads(request.get_json())
    node_ip = data['ip']
    node_pubkey = data['pub']
    if (not node_ip or not node_pubkey):
        return "Invalid", 400

    new_id = str(len(State.state.nodes))  # it works
    print('new node id is:',new_id)

    State.state.utxos[node_pubkey] = []

    State.state.nodes[new_id] = {}
    State.state.nodes[new_id]['ip'] = node_ip
    State.state.nodes[new_id]['pub'] = node_pubkey

    if (int(new_id) == config.NODE_CAPACITY - 1) :
        broadcast_nodes_info()

    return make_response(json.dumps({'id' : new_id}),200)

# A node requests the chain via a GET request , we return the chain
@API_communication.route('/request_chain',methods=['GET'])
def request_chain():
    block_list = [block.to_json() for block in State.state.chain]        
    json_chain = json.dumps({"chain": block_list})
    return json_chain 




# ------------------- CLI COMMANDS --------------------- 

@API_communication.route('/start_coordinator', methods=['POST'])
def start_coordinator():

    json_string = request.get_json()
    d = json.loads(json_string)
    config.NODE_CAPACITY = int(d['NODE_CAPACITY'])
    State.state.nodes[0] = {'ip': d['host'], 'pub': State.state.pub}
    State.state.genesis() # Create genesis block and transaction
    
    return make_response('OK', 201)

@API_communication.route('/new_transaction', methods=['POST'])
def cli_new_transaction():
    json_string = request.get_json()
    d = json.loads(json_string)
    node_id = d['recipient_address']
    amount = int(d['amount'])
    node = State.state.nodes[node_id]
    if (new_transaction(node['pub'], amount)):
        return make_response('OK',200)
    else:
        return make_response('Transaction Failed',400)
        

#! DONE
# Please read the exercise report before chaning stuff
@API_communication.route('/view_transactions', methods=['GET'])
def view_transactions():
    # there is always a last block so no need to check for empty chain
    last_block = State.state.chain[-1]
    json_trans = [t.to_json() for t in last_block.transactions]
    res = json.dumps({'transactions' : json_trans})
    return res

#! DONE 
@API_communication.route('/balance', methods=['GET'])
def show_balance():
    return json.dumps(State.state.wallet_balance())


@API_communication.route('/start_client', methods=['POST'])
def start_client():

    json_string = request.get_json()
    data = json.loads(json_string)
    COORDINATOR_IP = data['coordinator_host']
    State.state.nodes[0] = {'ip': data['coordinator_host']}

    # give coordinator 
    json_data = json.dumps({'ip' : data['host'], 'pub' : State.state.pub})
    response = requests.post(f'{COORDINATOR_IP}/register_node', json=json_data)
    State.state.id = response.json()['id']
    print('Our very own id is :',State.state.id)
    return make_response("OK",200)
