# Database

These installation and configuration instructions have been tested with PostgreSQL 9.6, 10.0 and 10.1, in combination with PostGIS 2.4. It is reasonable to assume that they work with a much larger range of versions of either software.

## Preparation

- Create a database and database user
- As a database superuser (e.g. `postgres`), run [prepare-database.sql](./prepare-database.sql).

# Populate the database with data

- Create a table with (at least) the following columns:
    - `id INT` (can be your data’s original id column)
    - `caption TEXT` (image caption)
    - `photo TEXT` (file path to image, either relative to [assets/data/](../src/assets/data/) or starting with `http[s]:`
- Be sure the table does NOT contain any columns named `sentiment`, `ambigous`, `annotater`, or `token`. These columns will be created on first access.
- Add the database connection string and the table name to the `config` dict in [assets/db/mansicca.py](../src/assets/db/mansicca.py). The key of your entry can be appended to the page URL (separated by a # hash sign) to access this particular configuration.

An example SQL exporting a random sample from a database as created by the [Social Media Data Collection Scripts](https://gitlab.com/DigitalGeographyLab/SocialMediaDataCollection) is found in [export-sample.sql](export-sample.sql).
