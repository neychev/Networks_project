from DbManager import DbManager
from datetime import datetime
import json
from hash import get_hash

def archive_chain():
    db_manager = DbManager("chains.db")
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
