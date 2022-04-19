"""
Storage classes to interface with the db.
"""

"""
HALPPP
- for find method need to do sth for when not found ?
- i dont need the * for delete ah??
"""
import sqlite3


class Collection:
    """
    Storage base class to interface with the db

    Attributes
    ----------
    column_names: List[str]
    - The names of the columns in the table

    db_path: str
    - The path to the db file

    Methods
    -------
    insert(record: dict) -> None
    - Inserts a record into the table

    find(filter: dict) -> dict
    - Returns the records matching the filter in the table

    update(filter: dict, new_record: dict) -> None
    - Update the old record(s) matching `filter` to the `new_record` in the table

    delete(filter: dict) -> None
    - Deletes all records matching `filter` from the table
    """

    column_names = NotImplemented

    def __init__(self, db_path: str):
        """Initialise a Collection which interfaces with the db specified by `db_path`"""
        pass

    def insert(self, record: dict) -> None:
        """
        Insert a record into the db.
        Record DOES NOT need to include the primary key if it is auto-incremented.
        e.g. for club records
        ```
        record: {
            'name': 'CLUB NAME'
        }
        ```
        and
        ```
        record: {
            'id': 10,
            'name': 'CLUB NAME'
        }
        ```
        are both accepted as the id for table `club` is AUTOINCREMENT-ed
        """
        pass

    def find(self, filter: dict) -> dict:
        """
        Return all rows matching the `filter` specifications.
        Return all columns from each record in the format
        {
            'column_1': ...,
            'column_2': ...,
        }
        """
        pass

    def update(self, filter: dict, new_record: dict) -> None:
        """
        Update the old record(s) specified by `filter` with the `new_record`.
        """
        pass

    def delete(self, filter: dict) -> None:
        """
        Delete the records from the table matching the `filter`.
        """
        pass


class Students(Collection):
    # PLEASE BE CONSISTENT IS IT student_id OR id ?????????
    # WHERE IS class_id YOU WROTE IT IN THE DATA SCHEMA AND ITS NOT HERE
    column_names = ['student_id', 'name', 'age', 'year_enrolled', 'graduating_year']

    def __init__(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS student(
                    student_id INTEGER, 
                    name TEXT,
                    age INTEGER,
                    year_enrolled INTEGER,
                    graduating_year INTEGER,
                    PRIMARY KEY(student_id)
                     )""")
            conn.commit()

    def insert(self, record: dict) -> None:
        # TODO allow omission of `id` from record.
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO student VALUES (?, ?, ?, ?, ?)""",
                      list(record.values()))
            conn.commit()

    def find(self, filter: dict) -> dict:
        """
        Return all rows matching the filter specifications.
        Return all columns from each record.
        """
        # Check that filter keys are valid column names
        for key, value in filter.items():
            if key not in self.column_names:
                raise KeyError(f"{key} is not a valid column name")

        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "

        sql = sql[:-4] #remove the final AND 

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(f"""SELECT * FROM student
                      WHERE {sql} """, list(values))
            record = c.fetchone()
            return record 

    def update(self, filter, new_record) -> None:
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""UPDATE student SET """)
            conn.commit()
        pass

    def delete(self, filter):
        #check that keys in filter match the column names
        for key, value in filter.items():
            if key not in self.column_names:
                raise KeyError(f"{key} is not a valid column name")

        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "

        sql = sql[:-4] #remove the final AND 

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(f"""DELETE FROM student WHERE {sql}""", list(values))
            conn.commit()
        pass


class Subject(Collection):
    def __init__(self, db_path):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS subject(
                    id INTEGER, 
                    name TEXT,
                    level TEXT,
                    PRIMARY KEY(id)
                    )""")
            conn.commit()
    
    pass


class Clubs(Collection):
    pass


class Activities(Collection):
    pass


class Classes(Collection):
    pass


if __name__ == '__main__':
    # testing code
    print('eorjgpoerg')
    people = Students('school')
    ren = {
        'student_id': 1,
        'name': 'cassey',
        'age': 17,
        'year_enrolled': 2021,
        'graduating_year': 2022
    }

    people.insert(ren)
    print(people.find({'name': 'cassey', 'age': 17}))
