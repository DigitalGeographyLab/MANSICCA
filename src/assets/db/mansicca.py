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
import secrets
import string


__all__ = ["MansiccaBackend"]


# config is a dict of dicts, its key is the “API-KEY” configured in the client javascript
# its values are dicts in the form of `{ "connectionString": "", "tableName": }` (also see default example)

config = {
    "YKWsd6QW5sxSNInbwiMmmDhugwS6PpVJ": {
        "connectionString": "dbname=mansicca user=mansicca",
        "tableName":        "instagram_southafrica_5000"
    }
}


class MansiccaBackend:
    """ main class """

    def __init__(self, connectionString, tableName, username):
        """
        MansiccaBackend

        Args:
            connectionString (str): PostgreSQL connection string
            tableName (str):        table with data to be annotated
            username (str):         username (to access level of agreement)

        """
        self.connectionString = connectionString
        self.tableName = tableName
        self.username = self._sanitise(username)
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
                """ + self.tableName + """
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
                "url": ""
            }
        else:
            row = {
                "id": row["id"],
                "caption": row["caption"],
                "photo": row["photo"],
                "url": row["url"],
                "token": self._generateToken()
            }

            self.cursor.execute(
                """
                    UPDATE
                        """ + self.tableName + """
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
                    """ + self.tableName + """
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
            username
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
