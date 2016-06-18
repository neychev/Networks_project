from hashlib import sha224

def get_hash(block):
    info = block['actions'] + str(block['created_at']) + block['prev_hash']
    return sha224(info).hexdigest()

