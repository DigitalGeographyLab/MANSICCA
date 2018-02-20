#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MansiccaBackend: fetches records from a PostgreSQL database
"""

import cgi
import datetime
import json
import psycopg2
import psycopg2.extras
import psycopg2.sql
import secrets
import string


__all__ = ["MansiccaBackend"]


# config is a dict of dicts, its key is the “API-KEY” configured
# in the client javascript
#
# its values are dicts in the form of
# `{ "connectionString": "", "tableName": }`
# (also see default example)

config = {
    "YKWsd6QW5sxSNInbwiMmmDhugwS6PpVJ": {
        "connectionString": "dbname=mansicca user=mansicca",
        "tableName":        "instagram_southafrica_5000",
        "stylesheet":       "instagram"
    },
    "9ju2G5FL30tiDd1ERqU35Du6uu9GKF7S": {
        "connectionString": "dbname=mansicca user=mansicca",
        "tableName":        "instagram_sa_visitorhistory_1000",
        "stylesheet":       "instagram"
    },
    "PallasYllas": {
        "connectionString": "dbname=mansicca user=mansicca",
        "tableName":        "py-instagram",
        "stylesheet":       "instagram"
    },
    "Rhino1": {
        "connectionString": "dbname=mansicca user=mansicca",
        "tableName":        "rhino1",
        "stylesheet":       "twitter"
    }
}


class MansiccaBackend:
    """ main class """

    def __init__(self, connectionString, tableName, username, stylesheet="instagram"):
        """
        MansiccaBackend

        Args:
            connectionString (str): PostgreSQL connection string
            tableName (str):        table with data to be annotated
            username (str):         username (to access level of agreement)
            stylesheet (str):       which class to assign to <content> in the frontend

        """
        self.connectionString = connectionString
        self.tableName = tableName
        self.table = psycopg2.sql.Identifier(tableName)
        self.username = self._sanitise(username)
        self.stylesheet = stylesheet
        self._connectToDb()
        pass

    def _connectToDb(self):
        """ (private) establishes a database connection """
        self.connection = psycopg2.connect(
            self.connectionString
        )
        self.connection.set_session(autocommit=True)
        self.cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )
        self._createColumnsIfNeeded()

    def _createColumnsIfNeeded(self):
        self.cursor.execute(
            psycopg2.sql.SQL(
                """
                    ALTER TABLE
                        {table}
                        ADD COLUMN IF NOT EXISTS
                            sentiment sentiment[] DEFAULT {emptyArray}::sentiment[],
                        ADD COLUMN IF NOT EXISTS
                            ambiguous BOOLEAN[] DEFAULT {emptyArray}::BOOLEAN[],
                        ADD COLUMN IF NOT EXISTS
                            annotater TEXT[] DEFAULT {emptyArray}::TEXT[],
                        ADD COLUMN IF NOT EXISTS
                            token TEXT[] DEFAULT {emptyArray}::TEXT[],
                        ADD COLUMN IF NOT EXISTS
                            url TEXT DEFAULT '#';

                    CREATE INDEX IF NOT EXISTS
                            {table_id_idx}
                        ON {table}
                        USING
                            btree(id);
                    CREATE INDEX IF NOT EXISTS
                            {table_sentiment_idx}
                        ON {table}
                        USING
                            gin(sentiment);
                    CREATE INDEX IF NOT EXISTS
                            {table_ambiguous_idx}
                        ON {table}
                        USING
                            gin(ambiguous);
                    CREATE INDEX IF NOT EXISTS
                            {table_annotater_idx}
                        ON {table}
                        USING
                            gin(annotater);
                    CREATE INDEX IF NOT EXISTS
                            {table_token_idx}
                        ON {table}
                        USING
                            gin(token);
                """
            ).format(
                table=self.table,
                table_id_idx=psycopg2.sql.Identifier(
                    "{}_id_idx".format((self.tableName,))
                ),
                table_sentiment_idx=psycopg2.sql.Identifier(
                    "{}_sentiment_idx".format((self.tableName,))
                ),
                table_ambiguous_idx=psycopg2.sql.Identifier(
                    "{}_ambiguous_idx".format((self.tableName,))
                ),
                table_annotater_idx=psycopg2.sql.Identifier(
                    "{}_annotater_idx".format((self.tableName,))
                ),
                table_token_idx=psycopg2.sql.Identifier(
                    "{}_token_idx".format((self.tableName,))
                ),
                emptyArray=psycopg2.sql.Literal([])
            )
        )

    def _generateToken(self):
        return "{date:%Y%m%d}_{token}".format(
                date=datetime.datetime.now(),
                token=secrets.token_hex(8)
        )

    def _sanitise(self, text):
        validchars = frozenset("%s%s" % (string.ascii_letters, string.digits))
        return str("".join(c for c in text if c in validchars)[:128])

    def fetchItem(self):
        """ fetchItem

        Args:
            None

        Returns:
            (object)
        """
        today = "{:%Y%m%d}".format(datetime.datetime.now())
        self.cursor.execute("""
            SELECT
                id,
                caption,
                url,
                photo
            FROM
                """ + '"' + self.tableName + '"' + """
            WHERE
                photo <> ''
            AND
                NOT EXISTS (
                    SELECT
                        1
                    FROM
                        (SELECT unnest(token) as token ) t
                    WHERE
                        t.token like '""" + today + """_%'
                )
            ORDER BY
                CASE
                    WHEN array_length(sentiment,1) IS NULL
                    THEN 0
                    ELSE array_length(sentiment,1)
                END ASC,
                (select sum(s) from unnest(ambiguous::int[]) s) ASC,
                ('{""" + self.username + """}' <@ annotater) ASC
            LIMIT 1;
        """)

        row = self.cursor.fetchone()
        if not row:
            row = {
                "id": False,
                "caption": "",
                "photo": "",
                "url": "",
                "stylesheet": self.stylesheet
            }
        else:
            row = {
                "id": row["id"],
                "caption": row["caption"],
                "photo": row["photo"],
                "url": row["url"],
                "stylesheet": self.stylesheet,
                "token": self._generateToken()
            }

            self.cursor.execute(
                """
                    UPDATE
                        """ + '"' + self.tableName + '"' + """
                    SET
                        token = array_append(token, %s)
                    WHERE
                        id=%s;
                """,
                (
                    row["token"],
                    row["id"]
                )
            )

        return row

    def saveItem(self, sentiment, ambiguous, token):
        # does this need additional security checks?
        self.cursor.execute(
            """
                UPDATE
                    """ + '"' + self.tableName + '"' + """
                SET
                    sentiment = array_append(sentiment, %s),
                    ambiguous = array_append(ambiguous, %s),
                    annotater = array_append(annotater, %s),
                    token = array_remove(token, %s)
                WHERE
                    %s <@ token;
            """,
            (
                sentiment,
                ambiguous,
                self.username,
                token,
                [token]
            )
        )

        rowcount = str(self.cursor.rowcount)

        # use the opportunity to clean up a bit:
        # (delete all (unused) tokens from yesterday or earlier)
        today = "{:%Y%m%d}".format(datetime.datetime.now())
        self.cursor.execute(
            """
                SELECT
                    token
                FROM
                    (
                        SELECT
                            unnest(token) as token
                        FROM
                            instagram_southafrica_5000
                    ) t
                WHERE
                    substring(t.token for 8)::int < %s;
            """,
            (int(today),)
        )

        try:
            expiredTokens = \
                    [row["token"] for row in self.cursor.fetchall()]
            for token in expiredTokens:
                self.cursor.execute(
                    """
                        UPDATE
                            instagram_southafrica_5000
                        SET
                            token = array_remove(token, %s)
                        WHERE
                            %s <@ token;
                    """,
                    (
                        token,
                        [token]
                    )
                )
        except Exception as e:
            pass

        return f'Successfully saved sentiment "{sentiment:s}" \
                ({"" if ambiguous else "not ":s}ambiguous) \
                for post [{token}] __{rowcount}'


def main():
    returnValue = {"status": "not-yet-run"}

    args = cgi.FieldStorage()
    try:
        action = args["action"].value
    except KeyError:
        action = False

    try:
        apiKey = args["key"].value if args["key"].value in config else False
    except KeyError:
        apiKey = False

    try:
        username = args["username"].value
    except KeyError:
        username = False

    if apiKey and action and username:

        m = MansiccaBackend(
            config[apiKey]["connectionString"],
            config[apiKey]["tableName"],
            username,
            config[apiKey]["stylesheet"]
        )

        if action == "get":
            returnValue.update(
                {
                    "status": "fetched-item",
                    "item": m.fetchItem()
                }
            )

        elif action == "save":
            try:
                sentiment = args["sentiment"].value
                ambiguous = args["ambiguous"].value
                token = args["token"].value

                assert sentiment in [
                    "positive",
                    "neutral",
                    "negative",
                    "skipped"
                ]
                assert ambiguous in ["true", "false"]
                ambiguous = ambiguous == "true"

                returnValue.update(
                    {
                        "status": "saved-item",
                        "details": m.saveItem(
                            sentiment,
                            ambiguous,
                            token
                        )
                    }
                )
            except AssertionError:
                returnValue.update(
                    {
                        "status": "failed-to-save-item",
                        "details": "values for variables sentiment and/or" +
                        "ambiguous out of range"
                    }
                )
            except KeyError:
                returnValue.update(
                    {
                        "status": "failed-to-save-item",
                        "details": "values for variables sentiment and/or" +
                        "ambiguous missing"
                    }
                )
            except psycopg2.Error:
                returnValue.update(
                    {
                        "status": "failed-to-save-item",
                        "details": "database error"
                    }
                )
    else:
        returnValue.update(
            {
                "status": "missing-args",
                "details": "arguments 'key', 'action' and " +
                           "'username' are mandatory"
            }
        )

    print("Content-Type: application/json\n\n")
    print(
        json.dumps(
            returnValue
        )
    )


if __name__ == "__main__":
    main()
