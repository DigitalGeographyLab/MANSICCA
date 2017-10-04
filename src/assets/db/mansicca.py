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
        self.cursor = self.connection.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        )

    def _generateToken(self):
        return "{date:%Y%m%d}_{token}".format(
                date=datetime.datetime.now(),
                token=secrets.token_hex()
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
            ORDER BY
                array_length(sentiment,1) ASC,
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
                token
            )
        )


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
            returnValue.update(
                {
                    "status": "saved-item",
                    "details": m.saveItem()
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
