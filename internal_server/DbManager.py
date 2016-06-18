from sqlite3 import connect, PARSE_DECLTYPES
from datetime import datetime
import json
import os
import hash

class DbManager:

    """
    Attributes:
        db_name: Name(filename) of SQLite database
        db_conn: Connection
    """

    def __init__(self, db_name):
        empty = not os.path.isfile(db_name)
        self.db_name = db_name
        self.db_conn = connect(db_name, detect_types=PARSE_DECLTYPES)

        if empty:
            b = {'prev_hash': '', 'created_at': datetime.now(), 'actions': [{'name': 'CreateUser', 'id': '1'}, {'name': 'UpgradeUser', 'id': '1'}]}
            b['hash'] = hash.get_hash(b)
            self.create_schema()
            self.add_block(b)

    def close(self):
        self.db_conn.close()

    def add_block(self, block):
        record = (block['prev_hash'], block['hash'], json.dumps(block['actions']), block['created_at'])
        
        c = self.db_conn.cursor()
        c.execute('INSERT INTO current_chain(prev_hash, hash, actions, created_at) VALUES (?,?,?,?)', record)
        self.db_conn.commit()

    def get_chain_by_table_name(self, table_name):
        blocks = []

        query = "SELECT prev_hash, hash, actions, created_at FROM %s ORDER BY created_at" % table_name
        rows = self.db_conn.execute(query).fetchall()
        for row in rows:
            actions = json.loads(row[2])
            blocks.append({'prev_hash': row[0], 'hash': row[1], 'actions': actions, 'created_at': row[3]})

        return blocks

    def get_chain(self):
        return self.get_chain_by_table_name('current_chain')

    def get_chain_at(self, at):
        query = "SELECT id FROM archived_chain_info WHERE started_at < ? AND finished_at >= ?"
        c = self.db_conn.cursor()
        result = c.execute(query, [str(at), str(at)]).fetchone()
            
        table_name = 'current_chain' if result is None else 'chain_' + str(result[0])

        return self.get_chain_by_table_name(table_name)

    def archive_current_chain(self, first_block):
        c = self.db_conn.cursor()

        query = "SELECT created_at FROM current_chain WHERE prev_hash=(SELECT hash FROM current_chain WHERE prev_hash = '')"
        started_at = c.execute(query).fetchone()[0]

        c.execute("SELECT count(id) FROM archived_chain_info ORDER BY id DESC")
        chain_count = c.execute("SELECT count(id) FROM archived_chain_info ORDER BY id DESC").fetchone()[0]
        chain_id = c.execute("SELECT id FROM archived_chain_info ORDER BY id DESC").fetchone()[0] if chain_count > 0 else 1
        info = (chain_id, started_at, datetime.now())

        c.execute("ALTER TABLE current_chain RENAME TO ?", "chain_%d" % chain_id)
        c.execute("INSERT INTO archived_chain_info(id, started_at, finished_at) VALUES (?,?,?)", info)

        self.db_conn.commit()
        self.create_table_current_chain
        self.add_block(first_block)

    def create_schema(self):
        self.create_table_current_chain()
        self.create_table_archived_chain_info()

    def create_table_current_chain(self):
        query = 'CREATE TABLE current_chain(prev_hash CHAR(128), hash CHAR(128), actions TEXT, created_at TIMESTAMP)'
        self.send_and_commit(query)

    def create_table_archived_chain_info(self):
        query = 'CREATE TABLE archived_chain_info(id INT, started_at TIMESTAMP, finished_at TIMESTAMP)'
        self.send_and_commit(query)

    def drop_schema(self):
        c = self.db_conn.cursor()
        c.execute("DROP TABLE current_chain")
        c.execute("DROP TABLE archived_chain_info;")
        self.db_conn.commit()

    def send_and_commit(self, query):
        c = self.db_conn.cursor()
        c.execute(query)
        self.db_conn.commit()
