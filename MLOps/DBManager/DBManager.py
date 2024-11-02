import oracledb

class DBManager:
    def __init__(self, dev_db=False, in_docker=False):
        """
        Initializes the database manager with the correct connection parameters.

        Args:
            dev_db (bool): Determines if the connection should be to the development database.
            in_docker (bool): Specifies if the application is running in a Docker container.
        """
        # Determine port based on whether this is a dev or production database
        port = 4040 if not dev_db else 4041

        # Choose DSN based on environment (local or Docker)
        if in_docker:
            # Use container hostname for Docker setup
            hostname = 'mlops-db-prod-1' if not dev_db else 'mlops-db-dev-1'
            port = 1521
        else:
            # Use localhost for local development
            hostname = 'localhost'

        self.__username = 'MLAPP'
        self.__password = 'ASDFqwer!@34'
        self.__dsn = f'{hostname}:{port}/xe'

    def __yield_connection(self):
        """
        Yields a connection to the Oracle database.
        
        Returns:
            oracledb.Connection: A connection to the Oracle database.
        """
        return oracledb.connect(user=self.__username, password=self.__password, dsn=self.__dsn)

    def run_query(self, query, query_details=None):
        """
        Executes a query and returns the results.

        Args:
            query (str): SQL query to execute.
            query_details (dict, optional): Parameters for the SQL query.

        Returns:
            list: The results of the query.
        """
        with self.__yield_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, query_details)
            return cursor.fetchall()

    def execute_insert(self, query, data_dict):
        """
        Executes an insert query and commits the changes.

        Args:
            query (str): SQL insert statement.
            data_dict (dict): Data to insert.

        Returns:
            None
        """
        with self.__yield_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, data_dict)
            connection.commit()
