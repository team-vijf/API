# API
REST API for writing/reading data from TimescaleDB



## Dependencies
The easiest way to try it out is to pull a TimescaleDB container with the following command:
```
docker run -d --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=project timescale/timescaledb:latest-pg11
```
Then set the appropriate IP, port etc. in core/api_vars. These values can also be set by environment variables.

### Environment Variables
The following environment variables can be set:
#### API_PORT
This setting will adjust the port the API is listening for requests.
Default is '80'
#### API_IP
This setting will bind the API's listener to a specific IP
Default is '0.0.0.0' (Bind to all)
#### API_DEBUG
If this setting is true, Flask will output more logs in stdout and stderr.
Default is 'True'

#### DB_IP
This setting will define where to look for the TimescaleDB database.
Default is '192.168.135.134' (Will change to localhost once development is over)
#### DB_PORT
This setting will define on what port the database is listening for requests
Default is '5432'
#### DB_USER
This setting will define what user will be used to log in on the database.
Default is 'postgres'
#### DB_PASSWORD
This setting will define what password will be used for DB_USER to log in on the database.
Default is 'password'
#### DB_NAME
This setting will define what database will be used.
Default is 'project'

## SwaggerUI
Once the API has launched you can visit the Swagger Documentation at the root (E.g. http://localhost/).