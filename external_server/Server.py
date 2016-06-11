from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import Binary
import xmlrpclib
import datetime
import string
import random


inner_server = xmlrpclib.ServerProxy('http://192.168.1.106:8000')

def GetChain():
    return inner_server.getChain()

def GetChainAt(at):
    return inner_server.getChainAt(at)

def addBlock(x):
    return inner_server.addBlock(x)

server = SimpleXMLRPCServer(("", 8000), logRequests=True, allow_none=True)
server.register_introspection_functions()

history_of_users = []
error_string = ['']


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
        return str(arg), str(type(arg)), arg

    def raises_exception(self, msg):
        #Always raises a RuntimeError with the message passed in
        raise RuntimeError(msg)

    def send_back_binary(self, bin):
        #Accepts single Binary argument, unpacks and repacks it to return it
        data = bin.data
        response = Binary(data)
        return response


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def getDiagnostics_function():
    return error_string.pop()

server.register_function(getDiagnostics_function, 'getDiagnostics')

def enter_function(id, location_id):
    BList = GetChain()
    user_found = False
    location_found = False
    user_iocount = 0
    for block in BList:
        for action in block['actions']:
            if action['name'] == 'CreateUser' and action['id'] == id:
                user_found = True
            if action['name'] == 'CreateLocation' and action['id'] == location_id:
                location_found = True
    if user_found == True and location_found == True:
        for block in BList:
            for action in block['actions']:
                if action['name'] == 'Enter' and action['id'] == id :
                    user_iocount+=1
                if action['name'] == 'Exit' and action['id'] == id:
                    user_iocount-=1
        if user_iocount == 0:
            x = {}
            x['prev_hash'] = BList[-1]['hash']
            x['actions'] = [{'name':'Enter', 'id':id, 'location_id':location_id}]
            addBlock(x)
            return True
        else:
            error_string.append('Enter fail: User is already inside some location.')
            return False
    else:
        if user_found == False:
            error_string.append('Enter fail: User not found.')
        if location_found == False:
            error_string.append('Enter fail: Location not found.')
        return False

server.register_function(enter_function, 'Enter')

def exit_function(id):
    BList = GetChain()
    user_found = False
    user_iocount = 0
    for block in BList:
        for action in block['actions']:
            if action['name'] == 'CreateUser' and action['id'] == id:
                user_found = True
    if user_found == False:
        error_string.append('Exit fail: User not found.')
        return False
    else:
        for block in BList:
            for action in block['actions']:
                if action['name'] == 'Enter' and action['id'] == id:
                    user_iocount+=1
                if action['name'] == 'Exit' and action['id'] == id:
                    user_iocount-=1
        if user_iocount == 1:
            x = {}
            x['prev_hash'] = BList[-1]['hash']
            x['actions'] = [{'name':'Exit', 'id':id}]
            addBlock(x)
            return True

server.register_function(exit_function, 'Exit')


def checkAdminRights(admin_id, BList):
    user_found = False
    admin_found = False
    admin_updowncount = 0
    for block in BList:
        for action in block['actions']:
            if action['name'] == 'CreateUser' and action['id'] == admin_id:
                user_found = True
    if user_found == True:
        for block in BList:
            for action in block['actions']:
                if action['name'] == 'UpgradeUser' and action['admin_id'] == admin_id:
                    admin_updowncount+=1
                if action['name'] == 'DowngradeUser' and action['admin_id'] == admin_id:
                    admin_updowncount-=1
        if admin_updowncount == 1:
            admin_found = True
            return 0
        else:
            error_string.append('Administrator identity fail: This user does not have the superuser rights.')
            return -2       #The user is not admin
    else:
        error_string.append('Administrator identity fail: There is no such superuser.')
        return -1           #No such admin user


def getLocation_function(admin_id, id, at):
    at = datetime.datetime.strptime(str(at), "%Y%m%dT%H:%M:%S")
    BCList = GetChainAt(at)
    BList = GetChain()
    admin_found = checkAdminRights(admin_id, BList)
    if admin_found != 0:
        return admin_found

    user_found = False
    loc_id = 0

    for block in BCList:
        for action in block['actions']:
            if action['name'] == 'CreateUser' and action['id'] == id and action['created_at'] <= at:
                user_found = True
    if user_found == True:
        for block in BCList:
            for action in block['actions']:
                if action['name'] == 'Enter' and action['id'] == id and action['created_at'] <= at:
                    loc_id = action['location_id']
                if action['name'] == 'Exit' and action['id'] == id and action['created_at'] <= at:
                    loc_id = 0
    else:
        error_string.append('Location identification fail: There is no such user.')
        return -1
    return loc_id
    #if user is not at any location return 0

server.register_function(getLocation_function, 'getLocation')

def createUser_function(admin_id):
    BList = GetChain()
    ifadmin = checkAdminRights(admin_id, BList)
    if ifadmin == 0:
        user_found = True
        while user_found == True:
            user_found = False
            id = id_generator(20)
            for block in BList:
                for action in block['actions']:
                    if action['name'] == 'CreateUser' and action['id'] == id:
                        user_found = True
        x = {}
        x['prev_hash'] = BList[-1]['hash']
        x['actions'] = [{'name': 'CreateUser', 'id': id}]
        addBlock(x)
        return id
    else:
        return ''

server.register_function(createUser_function, 'createUser')

def upgradeUser_function(admin_id, id):
    BList = GetChain()
    ifadmin = checkAdminRights(admin_id, BList)
    user_updowncount = 0
    if ifadmin == 0:
        user_found = False
        for block in BList:
            for action in block['actions']:
                if action['name'] == 'CreateUser' and action['id'] == id:
                    user_found = True
        if user_found == True:
            user_updowncount = 0
            for block in BList:
                for action in block['actions']:
                    if action['name'] == 'UpgradeUser' and action['id'] == id:
                        user_updowncount+=1
                    if action['name'] == 'DowngradeUser' and action['id'] == id:
                        user_updowncount-=1
            if user_updowncount == 1:
                error_string.append('User upgrade fail: The user has already been upgraded.')
                return False
            else:
                x = {}
                x['prev_hash'] = BList[-1]['hash']
                x['actions'] = [{'name':'UpgradeUser', 'id':id}]
                addBlock(x)
                return True
        else:
            error_string.append('User upgrade fail: User not found.')
            return False

    else:
        return False

server.register_function(upgradeUser_function, 'upgradeUser')

def downgradeUser_function(admin_id, id):
    BList = GetChain()
    ifadmin = checkAdminRights(admin_id, BList)
    if ifadmin == 0:
        user_found = False
        for block in BList:
            for action in block['actions']:
                if action['name'] == 'CreateUser' and action['id'] == id:
                    user_found = True
        if user_found == True:
            user_updowncount = 0
            for block in BList:
                for action in block['actions']:
                    if action['name'] == 'UpgradeUser' and action['id'] == id:
                        user_updowncount+=1
                    if action['name'] == 'DowngradeUser' and action['id'] == id:
                        user_updowncount-=1
            if user_updowncount == 0:
                error_string.append('User downgrade fail: The user has already been downgraded.')
                return False
            else:
                x = {}
                x['prev_hash'] = BList[-1]['hash']
                x['actions'] = [{'name':'DowngradeUser', 'id':id}]
                addBlock(x)
                return True
        else:
            error_string.append('User downgrade fail: There is no such user.')
            return False
    else:
        return False

server.register_function(downgradeUser_function, 'downgradeUser')


def createLocation_function(admin_id):
    BList = GetChain()
    prev_loc_id = 0
    ifadmin = checkAdminRights(admin_id, BList)
    if (ifadmin == 0):
        for block in BList:
            for action in block['actions']:
                if action['name'] == 'CreateLocation':
                    prev_loc_id = action['id']
        x = {}
        x['prev_hash'] = BList[-1]['hash']
        x['actions'] = [{'name':'CreateLocation', 'id':prev_loc_id+1}]
        addBlock(x)
        return prev_loc_id + 1
    else:
        return ifadmin

server.register_function(createLocation_function, 'createLocation')


def getUsers_function(admin_id, location_id, at):
    at = datetime.datetime.strptime(str(at), "%Y%m%dT%H:%M:%S")
    BCList = GetChainAt(at)
    BList = GetChain()
    UList = []
    ifadmin = checkAdminRights(admin_id, BList)
    if ifadmin == 0:
        for block in BCList:
            for action in block['actions']:
                if action['name'] == 'Enter' and action['location_id'] == location_id and action['created_at'] < at:
                    UList.append(action['id'])
                if action['name'] == 'Exit' and action['location_id'] == location_id and action['created_at'] < at:
                    UList.remove(action['id'])
        return UList
    else:
        return ifadmin
server.register_function(getUsers_function, 'getUsers')

server.register_instance(ExampleService())


try:
    print 'Use Control-C to exit'
    server.serve_forever()
except KeyboardInterrupt:
    print 'Exiting'

