import xmlrpclib

server = xmlrpclib.ServerProxy('http://localhost:8000')
print 'Ping:', server.ping()
print 'exit', server.exit(11)
print 'exit', server.exit(11)
print 'error string', server.getDiagnostics()
# print 'history', server.getHistory()
# print 'clear history', server.clearHistory()
# print 'history', server.getHistory()