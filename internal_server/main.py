from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from DbManager import DbManager
from datetime import datetime
import json
from hash import get_hash

current_ip = None
errors = {}

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
    def __init__(self, request, client_address, server):
        global current_ip
        current_ip = client_address[0]
        SimpleXMLRPCRequestHandler.__init__(self, request, client_address, server)

server = SimpleXMLRPCServer(("0.0.0.0", 8000), requestHandler=RequestHandler)
server.register_introspection_functions()
db_manager = DbManager("chains.db")

def add_error(ip, error_string):
    global errors
    errors[ip] = error_string

def get_chain_function():
    return db_manager.get_chain()
server.register_function(get_chain_function, 'getChain')

def get_chain_at_function(at):
    return db_manager.get_chain_at(datetime.strptime(str(at), "%Y%m%dT%H:%M:%S"))
server.register_function(get_chain_at_function, 'getChainAt')

def add_block_function(block):
    global current_ip
    if 'hash' in block:
        add_error(current_ip, 'hash value has been set')
        return False
    if 'created_at' in block:
        add_error(current_ip, 'created_at value has been set')
        return False
    if not 'prev_hash' in block:
        add_error(current_ip, 'prev_hash has not been set')
        return False
    if not 'actions' in block:
        add_error(current_ip, 'actions has not been set')
        return False
    if not isinstance(block['actions'], list):
        add_error(current_ip, 'actions must be a list')
        return False

    block['created_at'] = datetime.now()
    block['actions'] = json.dumps(block['actions'])
    block['hash'] = get_hash(block)

    try:
        db_manager.add_block(block)
    except Exception as thrown:
        add_error(current_ip, str(thrown))
        return False

    return True

server.register_function(add_block_function, 'addBlock')

def get_diagnostics_function():
    global errors
    global current_ip
    return errors[current_ip]


server.register_function(get_diagnostics_function, 'getDiagnostics')

def archive_chain():
    chain = db_manager.get_chain()

    fb_actions = []
    entered_users = []
    user_locations = {}
    admins = []

    for block in chain:
        for action in block['actions']:
            if action['name'] == "Enter":
                entered_users.append(action['id'])
                user_locations[action['id']] = action['location_id']
            elif action['name'] == "Exit":
                entered_users.remove(action['id'])
                del user_locations[action['id']]
            elif action['name'] == "CreateUser":
                fb_actions.append(action)
            elif action['name'] == "CreateLocation":
                fb_actions.append(action)
            elif action['name'] == "UpgradeUser":
                admins.append(action['id'])
            elif action['name'] == "DowngradeUser":
                admins.remove(action['id'])
    for admin_id in admins:
        fb_actions.append({'name': 'UpgradeUser', 'id': admin_id})

    for user_id in entered_users:
        fb_actions.append({'name': 'Enter', 'id': user_id, 'location_id': user_locations[user_id]})

    fb = {'prev_hash': '', 'actions': fb_actions, 'created_at': datetime.now()}
    fb['hash'] = get_hash(fb)
    
    db_manager.archive_current_chain(fb)


# Run the server's main loop
server.serve_forever()
