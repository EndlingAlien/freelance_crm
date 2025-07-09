import sqlite3
import pandas as pd


class TestDB:
    def __init__(self):
        self.db_name = 'test_stats.db'
        # TODO: Future match case/if statement, what backend are we using? [sqlite or mysql]
        self.conn = sqlite3.connect(self.db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create all tables if they don't already exist."""
        commands = {
            # Table for Clients
            'command_1': """CREATE TABLE IF NOT EXISTS Client (
                client_id INTEGER PRIMARY KEY,
                client_name TEXT,
                client_email TEXT,
                client_company TEXT
            )
            """,

            # Table for Projects
            'command_2': """CREATE TABLE IF NOT EXISTS Project (
                project_id INTEGER PRIMARY KEY,
                project_name TEXT,
                client_id INTEGER NOT NULL,
                start_date DATETIME,
                due_date DATETIME,
                status TEXT,
                FOREIGN KEY (client_id) REFERENCES Client(client_id) ON DELETE CASCADE,
                UNIQUE(project_name, client_id)
            )
            """,

            # Table for Invoices
            'command_3': """CREATE TABLE IF NOT EXISTS Invoice (
                invoice_id INTEGER PRIMARY KEY,
                project_id INTEGER UNIQUE,
                amount DECIMAL(10, 2),
                due_date DATETIME,
                paid BOOLEAN,
                FOREIGN KEY(project_id) REFERENCES Project(project_id) ON DELETE CASCADE
            )
            """,
        }
        for name, sql in commands.items():
            try:
                self.cursor.execute(sql)
            except sqlite3.Error as e:
                print(f"Failed to create {name}: {e}")

#region Create
    def create_client(self, client_name, client_email, client_company):
        # Check if the Client already exists in the database
        if self.check_if_client_exists(client_name):
            return False
        else:
            # Insert a new Client record
            self.cursor.execute(
                """INSERT INTO Client (client_name, client_email, client_company) VALUES (?, ?, ?)""",
                (client_name, client_email, client_company,)
            )
            self.conn.commit()
            return True

    def create_project(self, client_name, project_title, start_date, due_date, status):
        print(f"Db received info: {client_name, project_title, start_date, due_date, status}")
        # Fetch and return the existing Client's ID
        result = pd.read_sql_query(
            """SELECT client_id FROM Client WHERE client_name = ? LIMIT 1""",
            self.conn,
            params=(client_name,)
        )
        if not result.empty:
            client_id = int(result.iloc[0]['client_id'])
            print(f'adding info with client id: {client_id}')
            # Insert a new Project record
            self.cursor.execute(
                """INSERT INTO Project (project_name, client_id, start_date, due_date, status) VALUES (?, ?, ?, ?, ?)""",
                (project_title, client_id, start_date, due_date, status)
            )
            self.conn.commit()
            return True
        else:
            print(f'Client error, cant find client in db matching name: {client_name}')
            return False

    def create_invoice(self, project_name, amount, due_date, radio_var):
        print(f"Db received info: {project_name, amount, due_date, radio_var}")
        # Fetch and return the existing Project's ID
        result = pd.read_sql_query(
            """SELECT project_id FROM Project WHERE project_name = ? LIMIT 1""",
            self.conn,
            params=(project_name,)
        )
        if not result.empty:
            project_id = int(result.iloc[0]['project_id'])
            print(f'adding info with project id: {project_id}')
            if self.check_if_invoice_exists(project_id):
                print('project invoice exists')
                return False
            else:
                # Insert a new Project record
                self.cursor.execute(
                    """INSERT INTO Invoice (project_id, amount, due_date, paid) VALUES (?, ?, ?, ?)""",
                    (project_id, amount, due_date, radio_var)
                )
                self.conn.commit()
                return True
        else:
            print(f'Project error, cant find project in db matching name: {project_name}')
            return False

#endregion


    def check_if_client_exists(self, client_name):
        self.cursor.execute(
            "SELECT 1 FROM Client WHERE client_name = ? LIMIT 1",
            (client_name,)
        )
        return self.cursor.fetchone() is not None

    def check_if_invoice_exists(self, project_id):
        self.cursor.execute(
            "SELECT 1 FROM Invoice WHERE project_id = ? LIMIT 1",
            (project_id,)
        )
        return self.cursor.fetchone() is not None

    def get_list_of_clients(self):
        result = pd.read_sql_query("""SELECT * FROM Client""", self.conn)
        if not result.empty:
            client_list = [client for client in result['client_name']]
            return client_list
        else:
            return ['']

    def get_list_of_projects(self):
        result = pd.read_sql_query("""SELECT * FROM Project""", self.conn)
        if not result.empty:
            project_list = [project for project in result['project_name']]
            return project_list
        else:
            return ['']


db = TestDB()

db.get_list_of_clients()
