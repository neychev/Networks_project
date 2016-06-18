import xmlrpclib
import time
from datetime import datetime

errmsg = 'Error occurred. Get additional information by calling "getDiagnostics"'

def err_num_args(num, time_flag = False):
    msg = '.'
    if time_flag:
        msg = 'with time formatted %d %m %Y %I:%M:%S'
    print 'Wrong number of arguments! Need '+str(num)+' arguments' + msg
    return

"connecting to server"
connection_status = False
server = xmlrpclib.ServerProxy('http://127.0.0.1:8080')

while not connection_status:
    connection_status = server.ping()
    print 'Connection to server:', server.ping()
    if connection_status:
        break
    else:
        time.sleep(2)

print 'Connected to server. Server time:', str(server.now())


while True:
    command = raw_input("Enter command:\n")
    cl = command.split(' ')

    if cl[0] == 'getDiagnostics':
        print server.getDiagnostics()

    if cl[0] == 'Enter':
        if len(cl) == 3:
            result = server.Enter(cl[1], int(cl[2]))
            print 'User '+str(cl[1])+' entered location '+str(cl[2])+':', result
            if not result:
                print errmsg
        else:
            err_num_args(3)

    if cl[0] == 'Exit':
        if len(cl) == 2:
            result = server.Exit(cl[1])
            print 'User '+str(cl[1])+' left location '+str(cl[2])+': ', result
            if not result:
                print errmsg
        else:
            err_num_args(2)

    if cl[0] == 'getLocation':
        time_str = ' '.join(cl[3:])
        if len(cl) > 5:
            time_at = datetime.strptime(time_str, '%d %m %Y %I:%M:%S')
            location_id = server.getLocation(cl[1], cl[2], time_at)
            if location_id > 0:
                print 'User '+str(cl[2])+' was at location '+str(location_id)+' at ' + time_str
            else:
                print errmsg
        else:
            err_num_args(3, True)

    if cl[0] == 'createUser':
        if len(cl) == 2:
            created_user_id = server.createUser(cl[1])
            if created_user_id > 0:
                print 'Created user with id', created_user_id
            else:
                print errmsg
        else:
            err_num_args(2)

    if cl[0] == 'upgradeUser':
        if len(cl) == 3:
            result = server.upgradeUser(cl[1], cl[2])
            print 'Upgrade user '+str(cl[1])+' :', result
            if not result:
                print errmsg
        else:
            err_num_args(3)

    if cl[0] == 'downgradeUser':
        if len(cl) == 3:
            result = server.downgradeUser(cl[1], cl[2])
            print 'Downgrade user '+str(cl[1])+' :', result
            if not result:
                print errmsg
        else:
            err_num_args(3)

    if cl[0] == 'createLocation':
        if len(cl) == 2:
            created_location_id = server.createLocation(cl[1])
            if created_location_id > 0:
                print 'Created location with id', created_location_id
            else:
                print errmsg
        else:
            err_num_args(2)

    if cl[0] == 'getUsers':
        time_str = ' '.join(cl[3:])
        if len(cl) > 5:
            time_at = datetime.strptime(time_str, '%d %m %Y %I:%M:%S')
            server.getUsers(cl[1], cl[2], time_at)
        else:
            err_num_args(3, True)

    if command == 'quit':
        print 'Exiting terminal'
        break
