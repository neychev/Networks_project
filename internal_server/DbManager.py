from sqlite3 import connect
from datetime import datetime
import json

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
        record = (block['prev_hash'], block['hash'], json.dumps(block['actions']), block['created_at'])
        
        c = self.db_conn.cursor()
        c.execute('INSERT INTO current_chain(prev_hash, hash, actions, created_at)', record)
        self.db_conn.commit()

    def get_chain_by_table_name(self, table_name):
        blocks = []

        query = "SELECT prev_hash, hash, actions, created_at FROM %s" % table_name
        rows = self.db_conn.execute(query)
        for row in rows:
            actions = json.loads(row[2])
            blocks.push({prev_hash: row[0], hash: row[1], actions: actions, created_at: row[3]})

        return blocks

    def get_chain(self):
        return get_chain_by_table_name(self, 'current_chain')

    def get_chain_at(self, at):
        query = "SELECT id FROM archived_chain_info WHERE started_at < ? AND finished_at => ?"
        c = self.db_conn.cursor()
        chain_id = c.execute(query, (at, at)).fetchone()[0]

        table_name = 'chain_' + str(chain_id)

        return get_chain_by_table_name(self, table_name)

    def archive_current_chain(self, started_at):
        c = self.db_conn.cursor()

        chain_id = c.fetchone("SELECT id FROM archived_chain_info ORDER BY id DESC")[0]
        info = (chain_id, started_at, datetime.now())

        c.execute("ALTER TABLE current_chain RENAME TO ?", "chain_%d" % chain_id)
        c.execute("INSERT INTO archived_chain_info(id, started_at, finished_at) VALUES (?,?,?)", info)

        c.commit()
        self.create_table_current_chain

    def create_schema(self):
        self.create_table_current_chain
        self.create_table_archived_chain_info

    def create_table_current_chain(self):
        query = 'CREATE TABLE current_chain(prev_hash CHAR(128), hash CHAR(128), actions TEXT, created_at TEXT)'
        self.send_and_commit(query)

    def create_table_archived_chain_info(self):
        query = 'CREATE TABLE archived_chain_info(id INT, started_at TEXT, finished_at TEXT)'
        self.send_and_commit(query)

    def drop_schema(self):
        c = self.db_conn.cursor()
        c.executemany("DROP TABLE current_chain; DROP TABLE archived_chain_info;");

    def send_and_commit(self, query):
        c = self.db_conn.cursor()
        c.execute(query)
        c.commit()
