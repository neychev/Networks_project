from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler)
server.register_introspection_functions()

def get_chain_function():
    pass
server.register_function(get_chain_function, 'getChain')

def get_chain_at_function(at):
    pass
server.register_function(get_chain_at_function, 'getChainAt')

def add_block_function():
    pass
server.register_function(add_block_function, 'addBlock')

# Run the server's main loop
server.serve_forever()
print 1
