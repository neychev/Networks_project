from hashlib import sha224
from json import dumps

def get_hash(block):
    info = dumps(block['actions']) + str(block['created_at']) + block['prev_hash']
    return sha224(info).hexdigest()

