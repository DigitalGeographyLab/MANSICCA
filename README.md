# MANual SentIment ClassifiCAtion 

Mansicca is a web frontend, written in Python and relying a PostgreSQL/PostGIS backend, to facilitate an efficient manual sentiment classification.

## Python module dependencies
- psycopg2

## Deploy
Adapt the build script at [tools/build.sh](./tools/build.sh) and run `tools/build.sh -t` to test, compress and upload the markup content to a web server.

## Database
See [database-preparation](./database-preparation/) for instructions on how to create, configure and populate the database.
