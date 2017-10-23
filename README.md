# MANual SentIment ClassifiCAtion 

Mansicca is a web frontend, written in Python and relying a PostgreSQL backend, to facilitate an efficient manual sentiment classification.

#### Python module dependencies
- psycopg2


#### deploy
Adapt the build script at [tools/build.sh](./tools/build.sh) and run `tools/build.sh -t` to test, compress and upload the markup content to a web server.

#### database connection
adapt the PostgreSQL connection string in [src/assets/db/mansicca.py](./src/assets/db/mansicca.py) (better: add a new “API-KEY” there with connection string and table name)

#### data base structure
See [notes](./notes/) for instructions on how to create and fill the database.
