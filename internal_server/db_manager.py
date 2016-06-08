from sqlite3 import connect

class DbManager:

    """
    Attributes:
        db_name: Name(filename) of SQLite database
        db_conn: Connection
    """

    def __init__(self, db_name):
        self.db_name = db_name
        self.db_conn = connect(db_name)

    def close(self):
        self.db_conn.close()

    def add_block(self, block):
        record = (block['prev_hash'], block['hash'], block['actions'], block['created_at'])
        
        c = self.db_conn.cursor()
        c.execute('INSERT INTO current_chain(prev_hash, hash, actions, created_at)', record)
        self.db_conn.commit()

    def get_chain_by_table_name(self, table_name):
        blocks = []
        for row in self.db_conn.execute("SELECT prev_hash, hash, actions, created_at FROM %s" % table_name):
            blocks.push({prev_hash: row[0], hash: row[1], actions: row[2], created_at: row[3]})

        return blocks

    def get_chain(self):
        return get_chain_by_table_name(self, 'current_chain')

    def get_chain_at(self, at):
        # TODO
        tablenname = 'current_chain'

        return get_chain_by_table_name(self, table_name)
