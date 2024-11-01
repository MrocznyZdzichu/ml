import oracledb


class DBManager:
    def __init__(self, dev_db=False):
        port = 4040 if not dev_db else 4041
        
        self.__username = 'MLAPP'
        self.__password = 'ASDFqwer!@34'
        self.__dsn = 'localhost:' + str(port) + '/xe'

    def __yield_connection(self):
        return oracledb.connect(user=self.__username, password=self.__password, dsn=self.__dsn)

    def run_query(self, query, query_details=None):
        with self.__yield_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, query_details)
            return cursor.fetchall()

    def execute_insert(self, query, data_dict):
        with self.__yield_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(query, data_dict)
            connection.commit()
