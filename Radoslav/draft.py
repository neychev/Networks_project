history_of_users = []
error_string = []
import datetime
def Enter(client_id, location_id):
    global history_of_users
    global error_string
    element_of_history = {'client_id': client_id, 'location_id': location_id, 'time_in': datetime.datetime.now(), 'time_out': None}
    a = len(history_of_users)
    history_of_users.append(element_of_history)
    flag = (len(history_of_users) - a == 1)
    if not flag:
        error_string = 'Failed to add action to history:'+str(client_id)+' entered to location '+str(location_id)
    return flag

def Exit(client_id):
    global history_of_users
    global error_string
    index_of_entering = [i for i, x in enumerate(history_of_users) if x['time_out'] is None and x['client_id'] == client_id]
    flag = (len(index_of_entering) == 1)
    if flag:
        history_of_users[index_of_entering]['time_out'] = datetime.datetime.now()
    else:
        error_string = 'Failed to add action to history:'++str(client_id)+' left current location '
    return flag

def getLocation(admin_id, client_id, datetime):
    return

def createUser(admin_id, client_id):
    return

def upgradeUser(admin_id, client_id):
    return

def downgradeUser(admin_id, client_id):
    return

def createLocation(admin_id):
    return

def getUsers(admin_id, location_id, datetime):
    return

def getDiagnostics():
    return



while True:
    command = raw_input("Enter command:\n")
    command_list = command.split(' ')
    print command_list
    if command == 'quit':
        break
