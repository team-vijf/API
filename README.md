# API
REST API for writing/reading data from TimescaleDB



## Dependencies
The easiest way to try it out is to pull a TimescaleDB container with the following command:
```
docker run -d --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=project timescale/timescaledb:latest-pg11
```
Then set the appropriate IP, port etc. in core/api_vars. These values can also be set by environment variables.