"""
Utils that encapsulate inserting, updating and deleting "expanded**" junction table records into
the junction table collection, using the low level control provided by the collections in storage.py

** expanded refers to a record that includes the foreign table fields instead of just it's id.

e.g. instead of
```
{
    'student_id': 6,             # <- belongs to student
    'club_id': 1,                # <- belongs to club
    'role': 'member'             # <- belongs to student-club
}
```
the expanded record looks something like
```
{
    'student_name': 'OBAMA',     # <- belongs to student
    'age': 69,                   # <- belongs to student
    'year_enrolled': 2008,       # <- belongs to student
    'graduating_year': 2016,     # <- belongs to student
    'club_name': 'WHITE HOUSE',  # <- belongs to club
    'role': 'member'             # <- belongs to student-club
}
```
"""

import sqlite3  # for errors
from . import colls


class DBUtilsResult:
    def __init__(self, msg: str, is_ok: bool) -> None:
        self.msg = msg
        self.is_ok = is_ok

    @classmethod
    def error(cls, msg: str) -> None:
        return cls(msg, is_ok=False)

    @classmethod
    def success(cls, msg: str = '') -> None:
        return cls(msg, is_ok=True)

    def __str__(self) -> str:
        return self.msg

    def __repr__(self) -> str:
        return f'DBUtilsResult(msg="{self.msg}", is_ok={self.is_ok})'


def insert_into_jt_coll(jt_coll_name: str, new_record: dict) -> DBUtilsResult:
    """Insert `new_record` into the junction table collection specified by `coll_name`"""
    if jt_coll_name == 'membership':
        table_1 = 'club'
        table_2 = 'student'
        coll_1_id_name = 'club_id'
        coll_2_id_name = 'student_id'
    elif jt_coll_name == 'participation':
        table_1 = 'activity'
        table_2 = 'student'
        coll_1_id_name = 'activity_id'
        coll_2_id_name = 'student_id'
    else:
        return DBUtilsResult.error(f'Invalid jt_coll_name `{jt_coll_name}`')

    coll_1 = colls[table_1]  # e.g. club coll
    coll_2 = colls[table_2]  # e.g. student coll

    coll_1_to_find = {}  # e.g. club to find
    coll_2_to_find = {}  # e.g. student to find

    # The following comments will consider the case where jt_coll_name = 'membership'
    # Find the coll_1_id (e.g. club_id) based on the club's details in new_record
    for column_name in coll_1.column_names:
        value = new_record.get(column_name)
        if value is None:
            continue
        coll_1_to_find[column_name] = value

    coll_1_records = coll_1.find(coll_1_to_find)
    if len(coll_1_records) > 1:  # handle more than 1 club found
        return DBUtilsResult.error(
            f'ERROR WHILE INSERTING: More than 1 {table_1} records found. \
                Matching against: {coll_1_to_find}')
    elif len(coll_1_records) == 0:  # handle club not found
        return DBUtilsResult.error(
            f'ERROR WHILE INSERTING: No {table_1} records found. \
                Matching against: {coll_1_to_find}')
    coll_1_id = coll_1_records[0]['id']

    # Find the student_id based on the student's details in new_record
    for column_name in coll_2.column_names:
        value = new_record.get(column_name)
        if value is None:
            continue
        coll_2_to_find[column_name] = value

    coll_2_records = coll_2.find(coll_2_to_find)
    if len(coll_2_records) > 1:  # handle more than 1 student found
        return DBUtilsResult.error(
            f'ERROR WHILE INSERTING: More than 1 {table_2} records found. \
                Matching against {coll_2_to_find}')
    elif len(coll_2_records) == 0:  # handle student not found
        return DBUtilsResult.error(
            f'ERROR WHILE INSERTING: No {table_2} records found. \
                Matching against {coll_2_to_find}')
    coll_2_id = coll_2_records[0]['id']
    print(coll_2_records, coll_2_id)

    # Find the other info to insert (e.g. 'role' field in membership table)
    record_to_insert = {
        coll_1_id_name: coll_1_id,  # e.g. club_id
        coll_2_id_name: coll_2_id,  # e.g. student_id
    }
    jt_coll = colls[jt_coll_name]
    for column_name in jt_coll.column_names:
        value = new_record.get(column_name, '')
        if value == '':
            continue
        record_to_insert[column_name] = value

    # Insert the record containing the appropriate fields in membership table
    print(record_to_insert)
    try:
        jt_coll.insert(record_to_insert)
        return DBUtilsResult.success()
    except sqlite3.IntegrityError as err:
        return DBUtilsResult.error(str(err))


# naming convention below considers jt_coll_name = 'membership' because brain too smol

def update_jt_coll(jt_coll_name: str, old_record: dict, new_record: dict) -> DBUtilsResult:
    """
    Update the junction table collection specified by `jt_coll_name`,
    replacing the records matching `old_record` with `new_record`.

    e.g. consider membership junction table, where OBAMA has student_id = 6,
    WHITE HOUSE club has club_id = 1 and OBAMA FOUNDATION club has club_id = 4
    ```
    old_record = {
        'student_name': 'OBAMA',
        'student_club': 'WHITE HOUSE',
    }
    new_record = {
        'student_name': 'OBAMA',
        'student_club': 'OBAMA FOUNDATION',
    }
    ```
    will execute:
    ```
    coll.update(
        {
            'student_id': 6,
            'club_id': 1,
        },
        {
            'student_id': 6,
            'club_id': 4,
        },
    )
    ```
    """
    if jt_coll_name == 'membership':
        table_1 = 'club'
        table_2 = 'student'
        coll_1_id_name = 'club_id'
        coll_2_id_name = 'student_id'
    elif jt_coll_name == 'participation':
        table_1 = 'activity'
        table_2 = 'student'
        coll_1_id_name = 'activity_id'
        coll_2_id_name = 'student_id'
    else:
        return DBUtilsResult.error(f'ERROR WHILE UPDATING: Invalid jt_coll_name `{jt_coll_name}`')

    club_coll = colls[table_1]
    student_coll = colls[table_2]

    club_to_find = {}
    club_to_update = {}
    for column_name in club_coll.column_names:
        old_value = old_record.get(column_name)
        new_value = new_record.get(column_name)
        if old_value is None:
            continue
        club_to_find[column_name] = old_value
        club_to_update[column_name] = new_value

    old_club_records = club_coll.find(club_to_find)
    if len(old_club_records) > 1:
        return DBUtilsResult.error(
            f'ERROR WHILE UPDATING: More than 1 {table_1} records found. \
                Matching against: {club_to_find}')
    elif len(old_club_records) == 0:
        return DBUtilsResult.error(
            f'ERROR WHILE UPDATING: No {table_1} records found. \
                Matching against: {club_to_find}')
    new_club_records = club_coll.find(club_to_update)
    if len(new_club_records) > 1:
        return DBUtilsResult.error(
            f'ERROR WHILE UPDATING: More than 1 {table_1} records found. \
                Matching against: {club_to_update}')
    elif len(new_club_records) == 0:
        return DBUtilsResult.error(
            f'ERROR WHILE UPDATING: No {table_1} records found. \
                Matching against: {club_to_update}')
    old_club_id = old_club_records[0]['id']
    new_club_id = new_club_records[0]['id']

    student_to_find = {}
    student_to_update = {}
    for column_name in student_coll.column_names:
        old_value = old_record.get(column_name)
        new_value = new_record.get(column_name)
        if old_value is None:
            continue
        student_to_find[column_name] = old_value
        student_to_update[column_name] = new_value

    old_student_records = student_coll.find(student_to_find)
    if len(old_student_records) > 1:
        return DBUtilsResult.error(
            f'ERROR WHILE UPDATING: More than 1 {table_2} records found. \
                Matching against: {student_to_find}')
    elif len(old_student_records) == 0:
        return DBUtilsResult.error(
            f'ERROR WHILE UPDATING: No {table_2} records found. \
                Matching against: {student_to_find}')
    new_student_records = student_coll.find(student_to_update)
    if len(new_student_records) > 1:
        return DBUtilsResult.error(
            f'ERROR WHILE UPDATING: More than 1 {table_2} records found. \
                Matching against: {student_to_update}')
    elif len(new_student_records) == 0:
        return DBUtilsResult.error(
            f'ERROR WHILE UPDATING: No {table_2} records found. \
                Matching against: {student_to_update}')
    old_student_id = old_student_records[0]['id']
    new_student_id = new_student_records[0]['id']

    old_jt_records = {
        coll_1_id_name: old_club_id,
        coll_2_id_name: old_student_id,
    }
    new_jt_records = {
        coll_1_id_name: new_club_id,
        coll_2_id_name: new_student_id,
    }

    jt_coll = colls[jt_coll_name]
    for column_name in jt_coll.column_names:
        old_value = old_record.get(column_name, '')
        new_value = new_record.get(column_name, '')
        if old_value == '':
            continue
        old_jt_records[column_name] = old_value
        if new_value == '':
            continue
        new_jt_records[column_name] = new_value

    print(old_jt_records)
    print(new_jt_records)
    try:
        jt_coll.update(old_jt_records, new_jt_records)
        return DBUtilsResult.success()
    except sqlite3.IntegrityError as err:
        return DBUtilsResult.error(str(err))


def delete_from_jt_coll(jt_coll_name: str, record: dict) -> DBUtilsResult:
    """
    Delete from junction table collection specified by `jt_coll_name`,
    deleting records matching `record`.

    e.g. consider membership coll, where OBAMA student_id = 6 and WHITE HOUSE club_id = 1
    ```
    record = {
        'student_name': 'OBAMA',
        'club_name': 'WHITE HOUSE',
        'role': 'member',
    }
    ```
    will execute
    ```
    coll.delete({
        'student_id': 6,
        'club_id': 1,
        'role': 'member',
    })
    ```
    """
    if jt_coll_name == 'membership':
        table_1 = 'club'
        table_2 = 'student'
        coll_1_id_name = 'club_id'
        coll_2_id_name = 'student_id'
    elif jt_coll_name == 'participation':
        table_1 = 'activity'
        table_2 = 'student'
        coll_1_id_name = 'activity_id'
        coll_2_id_name = 'student_id'
    else:
        return DBUtilsResult.error(f'ERROR WHILE DELETING: Invalid jt_coll_name `{jt_coll_name}`')

    club_coll = colls[table_1]
    student_coll = colls[table_2]

    club_to_find = {}
    for column_name in club_coll.column_names:
        value = record.get(column_name)
        if value is None:
            continue
        club_to_find[column_name] = value

    club_records = club_coll.find(club_to_find)
    if len(club_records) > 1:
        return DBUtilsResult.error(
            f'ERROR WHILE DELETING: More than 1 {table_1} records found. \
                Matching against: {club_to_find}')
    elif len(club_records) == 0:
        return DBUtilsResult.error(
            f'ERROR WHILE DELETING: No {table_1} records found. \
                Matching against: {club_to_find}')
    club_id = club_records[0]['id']

    student_to_find = {}
    for column_name in student_coll.column_names:
        value = record.get(column_name)
        if value is None:
            continue
        student_to_find[column_name] = value

    student_records = student_coll.find(student_to_find)
    if len(student_records) > 1:
        return DBUtilsResult.error(
            f'ERROR WHILE DELETING: More than 1 {table_2} records found. \
            Matching against: {student_to_find}')
    elif len(student_records) == 0:
        return DBUtilsResult.error(
            f'ERROR WHILE DELETING: No {table_2} records found. \
                Matching against: {student_to_find}')
    student_id = student_records[0]['id']

    jt_record_to_delete = {
        coll_1_id_name: club_id,
        coll_2_id_name: student_id,
    }
    jt_coll = colls[jt_coll_name]
    for column_name in jt_coll.column_names:
        value = record.get(column_name, '')
        if value == '':
            continue
        jt_record_to_delete[column_name] = value

    print(jt_record_to_delete)
    try:
        jt_coll.delete(jt_record_to_delete)
        return DBUtilsResult.success()
    except sqlite3.IntegrityError as err:
        return DBUtilsResult.error(str(err))
