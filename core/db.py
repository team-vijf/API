import psycopg2
from core import api_vars
import sys

class Database():

    def __init__(self):
        structureExists = self.query('''SELECT EXISTS (SELECT * FROM information_schema.tables where table_name='buildings' );''')
        if not structureExists[0][0]:
            self.query(open('project.sql', 'r').read())

    def connect(self):

        # Connect to the database using the variables set in core/api_vars.py
        self.connection = psycopg2.connect(host=api_vars.DB_IP, 
                                           port=api_vars.DB_PORT, 
                                           user=api_vars.DB_USER, 
                                           password=api_vars.DB_PASSWORD, 
                                           dbname=api_vars.DB_NAME)
        self.connection.autocommit = True

    def addBuilding(self, name, streetName, buildingNumber):

        try:
            self.connect()
            cur = self.connection.cursor()

            cur.execute('''INSERT INTO buildings ( name, streetname, buildingnumber) VALUES ( '{}', '{}', '{}' )'''.format(name,
                                                                                                                           streetName,
                                                                                                                           buildingNumber))
        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))
            return False

    def addFloor(self, floorNumber, buildingId):

        try:
            self.connect()
            cur = self.connection.cursor()

            cur.execute('''INSERT INTO floors ( floornumber, id_buildings) VALUES ( '{}', '{}' );'''.format(floorNumber, buildingId))

        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))
            return False

    def addClassroom(self, classCode, floorId):

        try:
            self.connect()
            cur = self.connection.cursor()

            cur.execute('''INSERT INTO classrooms ( classcode, id_floors) VALUES ( '{}', '{}' );'''.format(classCode, floorId))

        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))
            return False

    def addFloorplan(self, floorPlan, floorId):

        try:
            self.connect()
            cur = self.connection.cursor()

            cur.execute('''INSERT INTO floorplans ( floorplan, id_floors) VALUES ( XMLPARSE({}), '{}' );'''.format(floorPlan, floorId))

        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))
            return False

    def query(self, query):

        try:
            self.connect()
            cur = self.connection.cursor()

            cur.execute(query)
            try:
                result = cur.fetchall()
                return result
            except:
                return True

        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))
            return False

    def setLocation(self, token, location):

        try:
            self.connect()
            cur = self.connection.cursor()

            # Get UID from token
            cur.execute('''SELECT uid FROM tokens WHERE token = '{}';'''.format(token))
            uid = cur.fetchone()[0]

            cur.execute('''UPDATE configs SET location = '{}', last_updated = Now() WHERE uid = '{}';'''.format(location, uid))

        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))
            return False



    def writeToken(self, uid, type, token):

        try:
            self.connect()
            cur = self.connection.cursor()


            # Create the table to write the token to, if it didn't exist already
            cur.execute('''CREATE TABLE IF NOT EXISTS tokens ( uid varchar(255) NOT NULL UNIQUE,
                                                               type varchar(255) NOT NULL,
                                                               token varchar(255) NOT NULL,
                                                               time TIMESTAMP NOT NULL );''')
            
            # Check if token already exists, if it exists overwrite it
            cur.execute('''SELECT * FROM tokens WHERE uid = '{}';'''.format(uid))
            tokenExists = cur.fetchall()
            if len(tokenExists) > 0:
                cur.execute('''UPDATE tokens SET token = '{}', time = Now() WHERE uid = '{}';'''.format(token, uid))
                return True

            # If it didn't already exists: Insert the uid, type, token and timestamp in the database
            cur.execute('''INSERT INTO tokens ( uid, type, token, time ) VALUES ('{}','{}','{}', Now());'''.format(uid, type, token))

            # If it succeeded
            return True

        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))
            return False

    def readToken(self, token, namespace):

        try:
            self.connect()
            cur = self.connection.cursor()

            if namespace == 'public':
                cur.execute('''SELECT * FROM tokens WHERE token = '{}';'''.format(token))
                return cur.fetchall()
            elif namespace == 'private':
                cur.execute('''SELECT * FROM tokens WHERE token = '{}' AND type = 'device' OR type = 'app';'''.format(token))
                return cur.fetchall()

        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))
            return False

    def readConfig(self, token):

        try:
            self.connect()
            cur = self.connection.cursor()

            # Create the table to write the token to, if it didn't exist already
            cur.execute('''CREATE TABLE IF NOT EXISTS configs ( uid varchar(255) NOT NULL UNIQUE,
                                                                location varchar(255),
                                                                config JSON,
                                                                last_updated TIMESTAMP NOT NULL );''')

            # Get UID from token
            cur.execute('''SELECT uid FROM tokens WHERE token = '{}';'''.format(token))
            uid = cur.fetchone()[0]

            # Check if device has a device-specific config
            cur.execute('''SELECT * FROM configs WHERE uid = '{}';'''.format(uid))
            configExists = cur.fetchall()

            # If it already exists, return the config
            if len(configExists) > 0:
                return {'location': configExists[0][1], 'configs': configExists[0][2]}
                
            # If it didn't exist, create a config
            cur.execute('''INSERT INTO configs ( uid, config, last_updated ) values ( '{}', Null, Now() ) ;'''.format(uid))
            
            cur.execute('''SELECT * FROM configs WHERE uid = '{}';'''.format(uid))
            config = cur.fetchall()

            return {'location': config[0][1], 'configs': config[0][2]}


        except Exception as err:
            sys.stderr.write('Database Error: {}'.format(err))
            return False