from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import Binary
import datetime

server = SimpleXMLRPCServer(('localhost', 8000), logRequests=True, allow_none=True)
server.register_introspection_functions()

history_of_users = []
error_string = []

class ExampleService:
    
    def ping(self):
        """Simple function to respond when called to demonstrate connectivity."""
        return True
        
    def now(self):
        """Returns the server current date and time."""
        return datetime.datetime.now()

    def show_type(self, arg):
        """Illustrates how types are passed in and out of server methods.
        
        Accepts one argument of any type.  
        Returns a tuple with string representation of the value, 
        the name of the type, and the value itself.
        """
        return (str(arg), str(type(arg)), arg)

    def raises_exception(self, msg):
        "Always raises a RuntimeError with the message passed in"
        raise RuntimeError(msg)

    def send_back_binary(self, bin):
        "Accepts single Binary argument, unpacks and repacks it to return it"
        data = bin.data
        response = Binary(data)
        return response

    def enter(self, client_id, location_id):
        global history_of_users
        global error_string
        element_of_history = {'client_id': client_id, 'location_id': location_id, 'time_in': datetime.datetime.now(), 'time_out': None}
        a = len(history_of_users)
        history_of_users.append(element_of_history)
        flag = (len(history_of_users) - a == 1)
        if not flag:
            error_string = 'Failed to add action to history:'+str(client_id)+' entered to location '+str(location_id)
        return flag

    def exit(self, client_id):
        global history_of_users
        global error_string
        index_of_entering = [i for i, x in enumerate(history_of_users) if x['time_out'] is None and x['client_id'] == client_id]
        print index_of_entering
        flag = (len(index_of_entering) == 1)
        if flag:
            history_of_users[index_of_entering[0]]['time_out'] = datetime.datetime.now()
        else:
            error_string = [datetime.datetime.now(),'Failed to add action to history:'+str(client_id)+' left current location ']
        return flag

    def getDiagnostics(self):
        global error_string
        return error_string

    def getHistory(self):
        global history_of_users
        return history_of_users

    def clearHistory(self):
        global history_of_users
        history_of_users = []
        return


server.register_instance(ExampleService())

try:
    print 'Use Control-C to exit'
    server.serve_forever()
except KeyboardInterrupt:
    print 'Exiting'

