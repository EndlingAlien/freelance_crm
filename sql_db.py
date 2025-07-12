import sqlite3
from datetime import datetime, timedelta
import pandas as pd


class CRM_db:
    def __init__(self):
        """Initialize the CRM database connection and create necessary tables."""
        self.db_name = 'crm_database.db'  # Database file name
        self.conn = sqlite3.connect(self.db_name)  # Establish connection to SQLite database
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraint enforcement
        self.cursor = self.conn.cursor()  # Create a cursor object for database operations
        self.create_tables()  # Initialize tables if they do not exist

    def create_tables(self):
        """Create all tables (Client, Project, Invoice) if they don't already exist."""
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
        # Execute each SQL command to create tables, with error handling
        for name, sql in commands.items():
            try:
                self.cursor.execute(sql)
            except sqlite3.Error as e:
                print(f"Failed to create {name}: {e}")

    # region Create
    def create_client(self, client_name, client_email, client_company):
        """
        Create a new client in the Client table.

        Args:
            client_name (str): Name of the client.
            client_email (str): Email address of the client.
            client_company (str): Company name associated with the client.

        Returns:
            bool: True if client was created, False if client already exists.
        """
        # Check if the Client already exists in the database
        if self.check_if_client_exists(client_name):
            return False
        else:
            # Insert a new Client record
            self.cursor.execute(
                """INSERT INTO Client (client_name, client_email, client_company) VALUES (?, ?, ?)""",
                (client_name, client_email, client_company,)
            )
            self.conn.commit()  # Commit transaction to save changes
            return True

    def create_project(self, client_name, project_title, start_date, due_date, status):
        """
        Create a new project linked to an existing client.

        Args:
            client_name (str): Name of the client to link the project.
            project_title (str): Title of the project.
            start_date (datetime): Project start date.
            due_date (datetime): Project due date.
            status (str): Current status of the project.

        Returns:
            bool: True if project was created, False if client was not found.
        """
        # Fetch and return the existing Client's ID
        result = pd.read_sql_query(
            """SELECT client_id FROM Client WHERE client_name = ? LIMIT 1""",
            self.conn,
            params=[client_name, ]
        )
        if not result.empty:
            client_id = int(result.iloc[0]['client_id'])  # Extract client ID from query result
            # Insert a new Project record
            self.cursor.execute(
                """INSERT INTO Project (project_name, client_id, start_date, due_date, status) VALUES (?, ?, ?, ?, ?)""",
                (project_title, client_id, start_date, due_date, status)
            )
            self.conn.commit()  # Commit transaction to save changes
            return True
        else:
            # Client not found in the database
            return False

    def create_invoice(self, project_name, amount, due_date, radio_var):
        """
        Create a new invoice for a project.

        Args:
            project_name (str): Name of the project associated with the invoice.
            amount (float): Invoice amount.
            due_date (datetime): Due date for the invoice.
            radio_var (bool): Paid status of the invoice.

        Returns:
            bool: True if invoice was created, False if project was not found or invoice already exists.
        """
        # Fetch and return the existing Project's ID
        result = pd.read_sql_query(
            """SELECT project_id FROM Project WHERE project_name = ? LIMIT 1""",
            self.conn,
            params=[project_name]
        )
        if not result.empty:
            project_id = int(result.iloc[0]['project_id'])  # Extract project ID from query result
            print(f'adding info with project id: {project_id}')
            # Check if an invoice already exists for this project
            if self.check_if_invoice_exists(project_id):
                print('project invoice exists')
                return False
            else:
                # Insert a new Invoice record
                self.cursor.execute(
                    """INSERT INTO Invoice (project_id, amount, due_date, paid) VALUES (?, ?, ?, ?)""",
                    (project_id, amount, due_date, radio_var)
                )
                self.conn.commit()  # Commit transaction to save changes
                return True
        else:
            # Project not found in the database
            print(f'Project error, cant find project in db matching name: {project_name}')
            return False

    # endregion

    # region View Tables

    def create_overdue_projects(self):
        """
        Create or refresh the 'Overdue Projects' SQL view showing projects past due and not finished.

        Returns:
            list: A list of lists with due_date, project_name, client_name, and status of overdue projects.
        """
        # Drop the view if it exists to refresh with latest data
        self.cursor.execute(
            """
            DROP VIEW IF EXISTS [Overdue Projects];
            """
        )
        # Create the view selecting projects due today or earlier and not finished
        self.cursor.execute(
            """CREATE VIEW IF NOT EXISTS [Overdue Projects] AS
                SELECT 
                    p.due_date,
                    p.status,
                    p.project_name,
                    c.client_name
                FROM Project p
                JOIN Client c ON p.client_id = c.client_id
                WHERE p.due_date <= DATE('now') AND p.status != 'Finished';
            """
        )
        # Query the view to return current overdue projects
        result = pd.read_sql_query(
            """SELECT due_date, project_name, client_name, status FROM [Overdue Projects]""",
            self.conn
        )
        self.conn.commit()  # Commit any changes (view creation)
        return result.values.tolist()  # Convert result to list of rows

    def create_overdue_invoices(self):
        """
        Create or refresh the 'Overdue Invoices' SQL view showing unpaid invoices past due.

        Returns:
            list: A list of lists with due_date, client_name, project_name, and amount of overdue invoices.
        """
        # Drop the view if it exists to refresh with latest data
        self.cursor.execute(
            """
            DROP VIEW IF EXISTS [Overdue Invoices];
            """
        )
        # Create the view selecting invoices due today or earlier and not paid
        self.cursor.execute(
            """CREATE VIEW IF NOT EXISTS [Overdue Invoices] AS
                SELECT 
                    i.due_date,
                    i.amount,
                    p.project_name,
                    c.client_name
                FROM Invoice i
                JOIN Project p ON i.project_id = p.project_id
                JOIN Client c ON p.client_id = c.client_id
                WHERE i.due_date <= DATE('now') AND i.paid != 1;
            """
        )
        # Query the view to return current overdue invoices
        result = pd.read_sql_query(
            """SELECT due_date, client_name, project_name, amount FROM [Overdue Invoices]""",
            self.conn
        )
        self.conn.commit()  # Commit any changes (view creation)
        return result.values.tolist()  # Convert result to list of rows

    def create_upcoming_projects(self):
        """
        Create or refresh the 'Upcoming Projects' SQL view showing projects due within the next 3 days and not finished.

        Returns:
            list: A list of lists with due_date, project_name, client_name, and status of upcoming projects.
        """
        # Drop the view if it exists to refresh with latest data
        self.cursor.execute(
            """
            DROP VIEW IF EXISTS [Upcoming Projects];
            """
        )
        # Create the view selecting projects due in the next 3 days and not finished
        self.cursor.execute(
            """CREATE VIEW IF NOT EXISTS [Upcoming Projects] AS
                SELECT 
                    p.due_date,
                    p.status,
                    p.project_name,
                    c.client_name
                FROM Project p
                JOIN Client c ON p.client_id = c.client_id
                WHERE p.due_date > DATE('now') AND p.due_date <= DATE('now', '+3 days') AND p.status != 'Finished';
            """
        )
        # Query the view to return projects that are upcoming soon
        result = pd.read_sql_query(
            """SELECT due_date, project_name, client_name, status FROM [Upcoming Projects]""",
            self.conn
        )
        self.conn.commit()  # Commit any changes (view creation)
        return result.values.tolist()  # Convert result to list of rows

    def create_upcoming_invoices(self):
        """
        Create or refresh the 'Upcoming Invoices' SQL view showing unpaid invoices due within the next 3 days.

        Returns:
            list: A list of lists with due_date, client_name, project_name, and amount of upcoming invoices.
        """
        # Drop the view if it exists to refresh with latest data
        self.cursor.execute(
            """
            DROP VIEW IF EXISTS [Upcoming Invoices];
            """
        )
        # Create the view selecting invoices due in the next 3 days and not paid
        self.cursor.execute(
            """CREATE VIEW IF NOT EXISTS [Upcoming Invoices] AS
                SELECT 
                    i.due_date,
                    i.amount,
                    p.project_name,
                    c.client_name
                FROM Invoice i
                JOIN Project p ON i.project_id = p.project_id
                JOIN Client c ON p.client_id = c.client_id
                WHERE i.due_date > DATE('now') AND i.due_date <= DATE('now', '+3 days') AND i.paid != 1;
            """
        )
        # Query the view to return invoices upcoming soon
        result = pd.read_sql_query(
            """SELECT due_date, client_name, project_name, amount FROM [Upcoming Invoices]""",
            self.conn
        )
        self.conn.commit()  # Commit any changes (view creation)
        return result.values.tolist()  # Convert result to list of rows

    # endregion

    # region Read Projects

    def get_projects(self):
        """
        Retrieve all projects along with their associated client names, start dates, due dates, and status.

        Returns:
            list: List of projects, each as [project_name, client_name, start_date, due_date, status].
        """
        result = pd.read_sql_query(
            """SELECT 
            p.project_name, 
            c.client_name,
            p.start_date,
            p.due_date,
            p.status
            FROM Project p
            JOIN Client c ON p.client_id = c.client_id""",
            self.conn
        )
        return result.values.tolist()

    def get_filtered_projects(self, filters):
        """
        Retrieve projects filtered by client name, status, month, and/or week date range.

        Args:
            filters (dict): Dictionary containing optional filter keys: 'client', 'status', 'month', 'week_date'.

        Returns:
            list: Filtered list of projects matching criteria.
        """
        base_query = """
                SELECT 
                    p.project_name, 
                    c.client_name,
                    p.start_date,
                    p.due_date,
                    p.status
                FROM Project p
                JOIN Client c ON p.client_id = c.client_id
                WHERE 1=1
            """
        params = []

        # Filter by client name if specified
        if filters.get("client"):
            base_query += " AND c.client_name = ?"
            params.append(filters["client"])

        # Filter by project status if specified
        if filters.get("status"):
            base_query += " AND status = ?"
            params.append(filters["status"])

        # Filter by month (due_date month) if specified
        if filters.get("month"):
            month_name_to_num = {
                "January": 1, "February": 2, "March": 3, "April": 4,
                "May": 5, "June": 6, "July": 7, "August": 8,
                "September": 9, "October": 10, "November": 11, "December": 12
            }
            month_num = month_name_to_num.get(filters["month"])
            if month_num:
                base_query += " AND strftime('%m', p.due_date) = ?"
                params.append(f"{month_num:02d}")  # Format month as zero-padded two-digit string

        # Filter by week date range if specified (7-day window)
        if filters.get("week_date"):
            start = datetime.strptime(filters["week_date"], "%Y-%m-%d")
            end = start + timedelta(days=6)

            base_query += " AND DATE(p.due_date) BETWEEN ? AND ?"
            params.append(start.strftime("%Y-%m-%d"))
            params.append(end.strftime("%Y-%m-%d"))

        # Execute the constructed query with parameters
        result = pd.read_sql_query(base_query, self.conn, params=params)
        print(f'filtered result: {result}')  # Debug print for filtered data
        return result.values.tolist()

    def get_project_id(self, project_name):
        """
        Retrieve the project_id corresponding to the given project name.

        Args:
            project_name (str): Name of the project.

        Returns:
            int or None: Project ID if found, else None.
        """
        result = self.cursor.execute(
            "SELECT project_id FROM Project WHERE project_name = ? LIMIT 1",
            (project_name,)
        ).fetchone()

        return result[0] if result else None

    def get_project_to_edit(self, project_id):
        """
        Retrieve project details for editing based on project ID.

        Args:
            project_id (int): ID of the project to fetch.

        Returns:
            list: List containing project details [project_name, client_name, start_date, due_date, status].
        """
        result = pd.read_sql_query(
            """
            SELECT 
                p.project_name, 
                c.client_name,
                p.start_date,
                p.due_date,
                p.status
            FROM Project p
            JOIN Client c ON p.client_id = c.client_id 
            WHERE project_id = ? 
            LIMIT 1
            """,
            self.conn,
            params=[project_id, ]
        )
        return result.values.tolist()

    # endregion
    # region Update/Delete Project

    def update_project_name(self, project_id, project_name):
        """
        Update the name/title of a project.

        Args:
            project_id (int): ID of the project to update.
            project_name (str): New project name.
        """
        self.cursor.execute("""UPDATE Project
        SET project_name = ?
        WHERE project_id = ?
        """, [project_name, project_id])
        self.conn.commit()

    def update_project_client(self, project_id, client_name):
        """
        Update the client associated with a project.

        Args:
            project_id (int): ID of the project to update.
            client_name (str): New client name to link.
        """
        print(client_name)  # Debug print
        # Get client ID from client name
        client_df = pd.read_sql_query(
            "SELECT client_id FROM Client WHERE client_name = ?",
            self.conn,
            params=(client_name,)  # explicitly named params argument
        )
        client_id = int(client_df.iloc[0, 0])  # Extract client_id from DataFrame

        # Update project with new client_id
        self.cursor.execute("""UPDATE Project
                SET client_id = ?
                WHERE project_id = ?
                """, [client_id, project_id])
        self.conn.commit()

    def update_project_status(self, project_id, status):
        """
        Update the status of a project.

        Args:
            project_id (int): ID of the project to update.
            status (str): New status.
        """
        self.cursor.execute("""UPDATE Project
                SET status = ?
                WHERE project_id = ?
                """, [status, project_id])
        self.conn.commit()

    def update_project_date(self, project_id, value, formatted_date):
        """
        Update either the start date or due date of a project.

        Args:
            project_id (int): ID of the project to update.
            value (str): Either "Start Date" or "Due Date" to specify which date to update.
            formatted_date (str): The date string formatted for the database.
        """
        if value == "Start Date":
            self.cursor.execute("""UPDATE Project
                            SET start_date = ?
                            WHERE project_id = ?
                            """, [formatted_date, project_id])
        elif value == "Due Date":
            self.cursor.execute("""UPDATE Project
                            SET due_date = ?
                            WHERE project_id = ?
                            """, [formatted_date, project_id])
        self.conn.commit()

    def delete_project(self, project_id):
        """
        Delete a project from the database by project ID.

        Args:
            project_id (int): ID of the project to delete.
        """
        self.cursor.execute("""DELETE FROM Project
                        WHERE project_id = ?
                        """, [project_id])
        self.conn.commit()

    # endregion

    # region Read Invoices

    def get_invoices(self):
        """
        Retrieve all invoices with associated project and client details.

        Returns:
            list: List of invoices as [project_name, client_name, amount, due_date, paid].
        """
        result = pd.read_sql_query(
            """SELECT 
            p.project_name,
            c.client_name,
            i.amount,
            i.due_date,
            i.paid
            FROM Invoice i
            JOIN Project p ON i.project_id = p.project_id
            JOIN Client c ON p.client_id = c.client_id
            """,
            self.conn
        )
        return result.values.tolist()

    def get_filtered_invoices(self, filters):
        """
        Retrieve invoices filtered by client, payment status, month, and/or week date range.

        Args:
            filters (dict): Filter parameters - 'client', 'paid', 'month', 'week_date'.

        Returns:
            list: Filtered list of invoices matching the criteria.
        """
        base_query = """SELECT 
            p.project_name,
            c.client_name,
            i.amount,
            i.due_date,
            i.paid
            FROM Invoice i
            JOIN Project p ON i.project_id = p.project_id
            JOIN Client c ON p.client_id = c.client_id
            WHERE 1=1
            """
        params = []

        # Filter by client name if provided
        if filters.get("client"):
            base_query += " AND c.client_name = ?"
            params.append(filters["client"])

        # Filter by paid status if provided (expecting 0 or 1)
        if filters.get("paid"):
            base_query += " AND i.paid = ?"
            params.append(filters["paid"])

        # Filter by month of due date if provided
        if filters.get("month"):
            month_name_to_num = {
                "January": 1, "February": 2, "March": 3, "April": 4,
                "May": 5, "June": 6, "July": 7, "August": 8,
                "September": 9, "October": 10, "November": 11, "December": 12
            }
            month_num = month_name_to_num.get(filters["month"])
            if month_num:
                base_query += " AND strftime('%m', i.due_date) = ?"
                params.append(f"{month_num:02d}")  # zero-padded month number

        # Filter by week date range (7 days starting from given date)
        if filters.get("week_date"):
            start = datetime.strptime(filters["week_date"], "%Y-%m-%d")
            end = start + timedelta(days=6)

            base_query += " AND DATE(i.due_date) BETWEEN ? AND ?"
            params.append(start.strftime("%Y-%m-%d"))
            params.append(end.strftime("%Y-%m-%d"))

        # Run the filtered query with parameters
        result = pd.read_sql_query(base_query, self.conn, params=params)
        print(f'filtered result: {result}')  # Debug output for filtered invoices
        return result.values.tolist()

    def get_invoice_id(self, project_name):
        """
        Retrieve the invoice_id associated with a given project name.

        Args:
            project_name (str): The project name to look up.

        Returns:
            int or None: Invoice ID if found, else None.
        """
        result = self.cursor.execute(
            """SELECT 
            i.invoice_id 
            FROM Invoice i 
            JOIN Project p ON i.project_id = p.project_id
            WHERE p.project_name = ? 
            LIMIT 1""",
            (project_name,)
        ).fetchone()

        return result[0] if result else None

    def get_invoice_to_edit(self, invoice_id):
        """
        Retrieve invoice details for editing by invoice ID.

        Args:
            invoice_id (int): The invoice ID to fetch.

        Returns:
            list: Invoice details [project_name, client_name, amount, due_date, paid].
        """
        result = pd.read_sql_query(
            """
            SELECT 
            p.project_name,
            c.client_name,
            i.amount,
            i.due_date,
            i.paid
            FROM Invoice i
            JOIN Project p ON i.project_id = p.project_id
            JOIN Client c ON p.client_id = c.client_id
            WHERE invoice_id = ?
            LIMIT 1
            """,
            self.conn,
            params=[invoice_id, ]
        )
        return result.values.tolist()

    # endregion
    # region Update/Delete Invoices

    def update_invoice_amount(self, invoice_id, invoice_amount):
        """
        Update the amount on an invoice.

        Args:
            invoice_id (int): Invoice ID to update.
            invoice_amount (float): New amount to set.
        """
        self.cursor.execute("""UPDATE Invoice
        SET amount = ?
        WHERE invoice_id = ?
        """, [invoice_amount, invoice_id])
        self.conn.commit()

    def update_invoice_paid(self, invoice_id, paid_status):
        """
        Update the paid status of an invoice.

        Args:
            invoice_id (int): Invoice ID to update.
            paid_status (bool or int): Paid status flag.
        """
        self.cursor.execute("""UPDATE Invoice
                SET paid = ?
                WHERE invoice_id = ?
                """, [paid_status, invoice_id])
        self.conn.commit()

    def update_invoice_date(self, invoice_id, formatted_date):
        """
        Update the due date of an invoice.

        Args:
            invoice_id (int): Invoice ID to update.
            formatted_date (str): New due date as string formatted for DB.
        """
        self.cursor.execute("""UPDATE Invoice
                            SET due_date = ?
                            WHERE invoice_id = ?
                            """, [formatted_date, invoice_id])
        self.conn.commit()

    def delete_invoice(self, invoice_id):
        """
        Delete an invoice from the database by ID.

        Args:
            invoice_id (int): Invoice ID to delete.
        """
        self.cursor.execute("""DELETE FROM Invoice
                        WHERE invoice_id = ?
                        """, [invoice_id])
        self.conn.commit()

    # endregion

    # region Read Clients

    def get_clients(self):
        """
        Retrieve all clients with their company, email, and the count of associated projects.

        Returns:
            list: List of clients as [client_name, client_company, client_email, project_count].
        """
        result = pd.read_sql_query(
            """
            SELECT 
            c.client_name,
            c.client_company,
            c.client_email,
            COUNT(p.project_id) as project_count
            FROM Client c 
            LEFT JOIN Project p ON c.client_id = p.client_id
            GROUP BY c.client_id, c.client_name, c.client_company, c.client_email
            """,
            self.conn
        )
        return result.values.tolist()

    def get_filtered_clients(self, filters):
        """
        Retrieve clients filtered by name string matching and project count.

        Args:
            filters (dict): Filtering options including:
                - client_string (str): String to match client names.
                - client_radio (int): 0 for "starts with", 1 for "contains".
                - project_radio (int): 0 for no projects, 1 for any projects, 2 for more than 2 projects.

        Returns:
            list: Filtered list of clients matching criteria.
        """
        base_query = """
            SELECT 
                c.client_name,
                c.client_company,
                c.client_email,
                COUNT(p.project_id) as project_count
            FROM Client c 
            LEFT JOIN Project p ON c.client_id = p.client_id
            WHERE 1=1
        """
        params = []

        # Filter by client name with LIKE, depending on radio option
        if filters.get("client_string"):
            client_string = filters["client_string"]
            radio_value = filters.get("client_radio")

            # Starts with (default) vs contains
            if radio_value == 0:
                base_query += " AND c.client_name LIKE ?"
                params.append(f"{client_string}%")
            else:
                base_query += " AND c.client_name LIKE ?"
                params.append(f"%{client_string}%")

        # Group by client fields for accurate project counts
        base_query += """
            GROUP BY c.client_id, c.client_name, c.client_company, c.client_email
        """

        # Filter by project count with HAVING clause based on radio option
        if filters.get("project_radio") is not None:
            project_radio = filters["project_radio"]
            if project_radio == 0:
                base_query += " HAVING COUNT(p.project_id) = 0"
            elif project_radio == 1:
                base_query += " HAVING COUNT(p.project_id) > 0"
            elif project_radio == 2:
                base_query += " HAVING COUNT(p.project_id) > 2"

        # Run the filtered query with parameters
        result = pd.read_sql_query(base_query, self.conn, params=params)
        print(f'filtered result: {result}')  # Debug output for filtered clients
        return result.values.tolist()

    def get_client_id(self, client_name):
        """
        Retrieve the client ID for a given client name.

        Args:
            client_name (str): The client's name.

        Returns:
            int or None: Client ID if found, else None.
        """
        result = self.cursor.execute(
            """SELECT 
            client_id
            FROM Client
            WHERE client_name = ? 
            LIMIT 1""",
            (client_name,)
        ).fetchone()

        return result[0] if result else None

    def get_client_to_edit(self, client_id):
        """
        Retrieve client details for editing, including project count.

        Args:
            client_id (int): ID of the client to retrieve.

        Returns:
            list: Client info as [client_name, client_company, client_email, project_count].
        """
        result = pd.read_sql_query(
            """
            SELECT 
            c.client_name,
            c.client_company,
            c.client_email,
            COUNT(p.project_id) as project_count
            FROM Client c 
            LEFT JOIN Project p ON c.client_id = p.client_id
            WHERE c.client_id = ?
            GROUP BY c.client_id, c.client_name, c.client_company, c.client_email
            LIMIT 1;
            """,
            self.conn,
            params=[client_id, ]
        )
        return result.values.tolist()

    # endregion
    # region Update/Delete Clients

    def update_client_name(self, client_id, client_name):
        """
        Update a client's name.

        Args:
            client_id (int): Client ID to update.
            client_name (str): New client name.
        """
        self.cursor.execute("""UPDATE Client
        SET client_name = ?
        WHERE client_id = ?
        """, [client_name, client_id])
        self.conn.commit()

    def update_company_name(self, client_id, company_name):
        """
        Update a client's company name.

        Args:
            client_id (int): Client ID to update.
            company_name (str): New company name.
        """
        self.cursor.execute("""UPDATE Client
                SET client_company = ?
                WHERE client_id = ?
                """, [company_name, client_id])
        self.conn.commit()

    def update_client_email(self, client_id, email_string):
        """
        Update a client's email address.

        Args:
            client_id (int): Client ID to update.
            email_string (str): New email address.
        """
        self.cursor.execute("""UPDATE Client
                            SET client_email = ?
                            WHERE client_id = ?
                            """, [email_string, client_id])
        self.conn.commit()

    def delete_client(self, client_id):
        """
        Delete a client by ID from the database.

        Args:
            client_id (int): Client ID to delete.
        """
        self.cursor.execute("""DELETE FROM Client
                        WHERE client_id = ?
                        """, [client_id])
        self.conn.commit()

    # endregion

    # region Checks and Lists

    def check_if_client_exists(self, client_name):
        """
        Check if a client with the given name exists in the database.

        Args:
            client_name (str): Name of the client to check.

        Returns:
            bool: True if client exists, False otherwise.
        """
        self.cursor.execute(
            "SELECT 1 FROM Client WHERE client_name = ? LIMIT 1",
            (client_name,)
        )
        return self.cursor.fetchone() is not None

    def check_if_invoice_exists(self, project_id):
        """
        Check if an invoice exists for the specified project ID.

        Args:
            project_id (int): Project ID to check.

        Returns:
            bool: True if invoice exists for the project, False otherwise.
        """
        self.cursor.execute(
            "SELECT 1 FROM Invoice WHERE project_id = ? LIMIT 1",
            (project_id,)
        )
        return self.cursor.fetchone() is not None

    def get_list_of_clients(self):
        """
        Retrieve a list of all client names.

        Returns:
            list: List of client names, or [''] if no clients found.
        """
        result = pd.read_sql_query("""SELECT * FROM Client""", self.conn)
        if not result.empty:
            client_list = [client for client in result['client_name']]
            return client_list
        else:
            return ['']  # Return list with empty string if no clients found

    def get_list_of_projects(self):
        """
        Retrieve a list of project names that do not yet have invoices.

        Returns:
            list: List of project names without invoices, or [''] if none found.
        """
        project_result = pd.read_sql_query("""SELECT project_id, project_name FROM Project""", self.conn)
        invoice_result = pd.read_sql_query("""SELECT project_id FROM Invoice""", self.conn)

        if project_result.empty:
            return ['']  # No projects found

        # Set of project IDs which have invoices
        project_ids_with_invoices = set(invoice_result['project_id']) if not invoice_result.empty else set()

        # Filter projects to only those without invoices
        filtered_projects = [
            row['project_name']
            for _, row in project_result.iterrows()
            if row['project_id'] not in project_ids_with_invoices
        ]

        return filtered_projects if filtered_projects else ['']  # Return list or [''] if empty

    # endregion
