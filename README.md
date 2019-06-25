# API
REST API for writing/reading data from TimescaleDB



## Installing locally
The best way to run this locally is to first clone this repo and then to build the container using the provided dockerfile (use the -t flag to tag the container with 'api')
Then start up the container and timescaledb with the following docker-compose file:
```
version: '3'

services:
  api:
    image: api
    container_name: api
    restart: unless-stopped
    network_mode: host
    environment:
      - API_PORT=80
      - API_IP=0.0.0.0
      - API_DEBUG=True
      - DB_IP=127.0.0.1
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=password
      - DB_NAME=project
      - SHARED_SECRET=secret
      - MOTION_THRESHOLD=3

  db:
    image: timescale/timescaledb:latest-pg11
    container_name: timescaledb
    restart: unless-stopped
    network_mode: host
    environment:
      - POSTGRES_DB=project
      - POSTGRES_PASSWORD=password
```


## SwaggerUI
Once the API has launched you can visit the Swagger Documentation at the root (E.g. http://localhost/).