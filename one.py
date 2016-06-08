import xmlrpclib

server = xmlrpclib.ServerProxy('http://localhost:8000')
print 'Ping:', server.ping()
print 'enter', server.enter(11, 22)
print 'enter', server.enter(12, 22)
print 'enter', server.enter(13, 25)
print 'enter', server.enter(14, 21)
# print 'exit', server.Exit(11)
# print 'exit', server.Exit(12)
# print 'exit', server.Exit(13)

print 'history', server.getHistory()
