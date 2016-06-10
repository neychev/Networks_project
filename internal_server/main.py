from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from DbManager import DbManager
from datetime import datetime

current_ip = None
errors = {}

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)
    def __init__(self, request, client_address, server):
        global current_ip
        current_ip = client_address
        SimpleXMLRPCRequestHandler.__init__(self, request, client_address, server)

server = SimpleXMLRPCServer(("0.0.0.0", 8000), requestHandler=RequestHandler)
server.register_introspection_functions()
db_manager = DbManager("chains.db")

def add_error(ip, error_string):
    global errors
    errors[ip] = error_string

def get_chain_function():
    return db_manager.get_chain
server.register_function(get_chain_function, 'getChain')

def get_chain_at_function(at):
    return db_manager.get_chain_at(at)
server.register_function(get_chain_at_function, 'getChainAt')

def add_block_function(block):
    if 'hash' in block:
        add_error(current_ip, 'hash value has been set')
        return False
    if 'created_at' in block:
        add_error(current_ip, 'created_at value has been set')
        return False

    block['created_at'] = datetime.now()
    block['hash'] = '123'

    db_manager.add_block(block)

    return True
server.register_function(add_block_function, 'addBlock')


# Run the server's main loop
server.serve_forever()