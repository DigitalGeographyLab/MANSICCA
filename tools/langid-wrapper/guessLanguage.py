#!/bin/env python3
# -*- coding: utf-8 -*-

"""
Add a column to the database table and
fill in the best guess language code
(using langid, it’s not always correct,
but at least easy to implement)

Took  ~10s + 20s queue timeout for the
5000 row instagram_southafrica sample
(on my desktop i5/16GiB RAM)

Don’t forget to adjust the connection
string and table name in main()
"""


import multiprocessing
import psycopg2
import queue

from langid.langid import (
    LanguageIdentifier,
    model
)


class LanguageGuesser:
    def __init__(self):
        self.identifier = \
            LanguageIdentifier.from_modelstring(
                model,
                norm_probs=True
            )

    def guess(self, text):
        try:
            return self.identifier.classify(text)[0]
        except:  # noqa: E722
            return None


def languageGuesserWorker(inQueue, outQueue):
    languageGuesser = LanguageGuesser()
    while True:
        try:
            (pid, text) = inQueue.get(timeout=20)
        except queue.Empty:
            break
        language = languageGuesser.guess(text)
        outQueue.put((pid, language))


def dataFetcher(connectionString, table, inQueue):
    with psycopg2.connect(connectionString) as connection:
        with connection.cursor("foobar-serverside") as cursor:
            cursor.execute("SELECT id, caption FROM " + table)
            while True:
                posts = cursor.fetchmany(200)
                if len(posts):
                    [inQueue.put(p) for p in posts]
                else:
                    break


def dataSaver(connectionString, table, outQueue):
    counter = 0
    with psycopg2.connect(connectionString) as connection:
        with connection.cursor() as cursor:
            while True:
                try:
                    (pid, language) = outQueue.get(timeout=20)
                except queue.Empty:
                    break
                cursor.execute(
                    """
                        UPDATE
                            """ + table + """
                        SET
                            language=%s
                        WHERE
                            id=%s;
                    """,
                    (
                        language[:2] if language is not None else None,
                        pid
                    )
                )
                counter += 1
                if counter % 100 == 0:
                    connection.commit()

            connection.commit()


def main():
    connectionString = "dbname=mansicca"
    table = "instagram_southafrica_5000"

    inQueue = multiprocessing.Queue()
    outQueue = multiprocessing.Queue()

    processes = []

    p = multiprocessing.Process(
        target=dataFetcher,
        args=(
            connectionString,
            table,
            inQueue
        )
    )
    p.start()
    processes.append(p)

    p = multiprocessing.Process(
        target=dataSaver,
        args=(
            connectionString,
            table,
            outQueue
        )
    )
    p.start()
    processes.append(p)

    for _ in range(multiprocessing.cpu_count() + 1):
        p = multiprocessing.Process(
            target=languageGuesserWorker,
            args=(
                inQueue,
                outQueue
            )
        )
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == "__main__":
    main()
