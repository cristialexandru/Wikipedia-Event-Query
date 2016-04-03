#!/usr/local/bin/python
# -*- coding: utf-8 -*-

"""
This module uses an wikipedia api and PyMongo to store
information from wikipedia pages and save them into a database
in order to perform queries upon them
"""

import wikipedia
from threading import Thread, Semaphore
import schedule
import pymongo


MONTH_NAMES = ['January', 'February', 'March', 'April', 'May',
                     'June', 'July', 'August', 'September', 'October',
                     'November', 'December']

DAYS_IN_MONTH = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

SECTION_NO = 4

SECTION_NAMES = ['Events', 'Births', 'Deaths', 'Holidays and observances']

DB_NAMES = ['evs', 'brts', 'dths', 'holo']

MAX_THREADS = 8

SERVER_ADDR = "localhost"

SERVER_PORT = 27017

def insert_entry(month, day, semaphore):
    """
    Function that takes a month a day and
    performs an addition in the database with
    all the events in that day.

    @type month: String
    @param device_id: the name of the month

    @type day: Int
    @param day: the day in the month

    @type semaphore: Semaphore
    @param semaphore: makes sure no more than MAX_THREADS
    threads are running at the same time
    """

    with semaphore:
        page_name = month + " " + str(day)
        page = wikipedia.page(page_name)

        # Connects to the mongo
        client = pymongo.MongoClient(SERVER_ADDR, SERVER_PORT)
        for i in xrange(SECTION_NO - 1):

            # Select the database
            database = client[DB_NAMES[i]]
            collection = database[month.lower() + '_' + str(day)]
            section = page.section(SECTION_NAMES[i])
            entries = section.splitlines()

            # Go through each entry and insert it into the db
            # according to which category it belongs
            for entry in entries:
                entry_dict = entry.split(u'–', 1)

                if len(entry_dict) < 2:
                    continue
                if entry_dict[1].strip() == "":
                    continue

                post = {'year' : entry_dict[0].strip(),
                        'day'  : page_name,
                        'category' : SECTION_NAMES[i].lower(),
                        'desc' : entry_dict[1].strip()}
                collection.insert(post)

        database = client[DB_NAMES[3]]
        collection = database[month.lower() + '_' + str(day)]
        section = page.section(SECTION_NAMES[3])
        entries = section.splitlines()
        for entry in entries:
            post = {'day'  : page_name,
                    'category' : SECTION_NAMES[3].lower(),
                    'desc' : entry}
            collection.insert(post)

def job():
    """
    Does the job by instantiating threads
    and passing the necesary info for updating
    the database
    """
    # Semaphore for limiting the number of threads
    SEM = Semaphore(MAX_THREADS)

    # Delete all the information if any
    client = pymongo.MongoClient("localhost", 27017)
    for db_name in DB_NAMES:
        client.drop_database(db_name)

    # For each month
    for mnth in xrange(12):
        threads = []
        for dy in xrange(DAYS_IN_MONTH[mnth]):

            # Create thread
            t = Thread(target=insert_entry, \
                args=(MONTH_NAMES[mnth], dy + 1, SEM))
            t.start()
            threads.append(t)

        # Wait for threads to finish
        for t in threads:
            t.join()

if __name__ == "__main__":

    """
    Using schedule.
    For more info: https://github.com/dbader/schedule
    """
    schedule.every(2).hours.do(job)
    job()
    while 1:
        schedule.run_pending()


