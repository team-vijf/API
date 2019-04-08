import psycopg2
import sys
from core import api_vars


class Database():

    # Try to connect to the database
    def connect(self):
        try:
            self.conn = psycopg2.connect(host=api_vars.DB_IP, 
                                        port=api_vars.DB_PORT,
                                        user=api_vars.DB_USER,
                                        password=api_vars.DB_PASSWORD,
                                        dbname=api_vars.DB_NAME)
            self.conn.autocommit = True

        except Exception as err:
            sys.stderr('Could not connect to DB, error: {}'.format(err))

    # Try to gracefully close the connection
    def close(self):
        try:
            if self.conn:
                self.conn.close()
        except:
            pass

    # Try to query the database
    def query(self, query):
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(query)

            try:
                result = self.cursor.fetchall()
                return result
            except:
                pass

        except Exception as err:
            try:
                if self.conn:
                    self.conn.rollback()
            except:
                pass
            finally:
                sys.stderr('Could not execute query, error: {}'.format(err))
