import csv
import sqlite3
from typing import Dict as __Dict
from .storage import *


DB_PATH = 'database/nyjc.db'
colls: __Dict[str, Collection] = {
    'student': Students(DB_PATH),
    'club': Clubs(DB_PATH),
    'class': Classes(DB_PATH),
    'activity': Activities(DB_PATH),
    'subject': Subjects(DB_PATH),
    'membership': Membership(DB_PATH),
    'participation': Participation(DB_PATH),
    'student-subject': StudentSubject(DB_PATH),
}


# funcs to init db from csvs
# pylint: disable=unspecified-encoding
__CSV_FOLDER = './database/csv_data'


def init_db_from_csvs():
    __init_class_table()
    __init_student_table()
    __init_subject_table()
    __init_club_table()
    __init_activity_table()
    __init_student_subject_table()
    __init_student_activity_table()
    __init_student_club_table()


def __init_class_table():
    coll = colls['class']
    with open(f'{__CSV_FOLDER}/class.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = dict(row)
            record['id'] = int(record['id'])
            try:
                coll.insert(record)
            except sqlite3.IntegrityError as err:
                # print(err)
                ...


def __init_student_table():
    coll = colls['student']
    with open(f'{__CSV_FOLDER}/student.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = dict(row)
            record['id'] = int(record['id'])
            record['age'] = int(record['age'])
            record['class_id'] = int(record['class_id'])
            record['year_enrolled'] = int(record['year_enrolled'])
            record['graduating_year'] = int(record['graduating_year'])
            try:
                coll.insert(record)
            except sqlite3.IntegrityError as err:
                # print(err)
                ...


def __init_subject_table():
    coll = colls['subject']
    with open(f'{__CSV_FOLDER}/subject.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = dict(row)
            record['id'] = int(record['id'])
            try:
                coll.insert(record)
            except sqlite3.IntegrityError as err:
                # print(err)
                ...


def __init_club_table():
    coll = colls['club']
    with open(f'{__CSV_FOLDER}/club.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = dict(row)
            record['id'] = int(record['id'])
            try:
                coll.insert(record)
            except sqlite3.IntegrityError as err:
                # print(err)
                ...


def __init_activity_table():
    pass  # init with the web app ui


def __init_student_subject_table():
    coll = colls['student-subject']
    with open(f'{__CSV_FOLDER}/student_subject.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = dict(row)
            record['student_id'] = int(record['student_id'])
            if record['subject_id'] != '':
                record['subject_id'] = int(record['subject_id'])
            else:
                record['subject_id'] = None

            try:
                print(record['student_id'])
                coll.insert(record)
            except sqlite3.IntegrityError as err:
                # print(err)
                ...


def __init_student_activity_table():
    pass  # init with the web app ui


def __init_student_club_table():
    pass  # init with the web app ui
