"""
Storage classes to interface with the db.
"""

"""
HALPPP
- for find method need to do sth for when not found ?
- if nth for find return empty list
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

    def __init__(self, db_path):
        self.db_path = db_path
        self.column_names = ['student_id', 'name', 'age', 'year_enrolled', 'graduating_year', 'class_id']
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS student(
                    student_id INTEGER, 
                    name TEXT,
                    age INTEGER,
                    year_enrolled INTEGER,
                    graduating_year INTEGER,
                    class_id INTEGER,
                    PRIMARY KEY(student_id)
                     )""")
            conn.commit()

    def check_column(self, to_check: dict):
        # Check that filter keys are valid column names
        for key, value in to_check.items():
            if key not in self.column_names:
                raise KeyError(f"{key} is not a valid column name")

    def execute(self, sql, values={}):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(sql, values)
            results = c.fetchall()
            conn.commit()
            # conn.close() is automatic
            
            if results == []:
                return []
            else:
                actually_dict = []
                for record in results:
                    actually_dict.append(dict(record))
                return actually_dict

    def insert(self, record: dict) -> None:
        # TODO allow omission of `id` from record.
        self.execute("""INSERT INTO student VALUES (?, ?, ?, ?, ?, ?)""", list(record.values()))

            

    def find(self, filter: dict) -> dict:
        """
        Return all rows matching the filter specifications.
        Return all columns from each record.
        """
        # Check that filter keys are valid column names
        self.check_column(filter)

        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "

        sql = sql[:-4] #remove the final AND
        sql = f"""SELECT * 
                  FROM student
                  WHERE {sql} """
        return self.execute(sql, list(values))

    def update(self, filter, new_record) -> None:
        #check the columns in both filter and new_record
        self.check_column(filter)
        self.check_column(new_record)

        #sql for the SET part
        keys = new_record.keys()
        new_values = new_record.values()
        new_sql = ''

        for key in keys:
            new_sql += f"{key} = ?, "

        new_sql = new_sql[:-2] #remove the final ','

        #sql for the WHERE part
        conditions = filter.keys()
        values = filter.values()
        sql = ''
        
        for condition in conditions:
            sql += f"{condition} = ? AND "

        sql = sql[:-4] #remove the final AND
        both = list(new_values) + list(values)
        sql = f"""UPDATE student 
                  SET {new_sql}
                  WHERE {sql} """
        return self.execute(sql, list(both))

    def delete(self, filter):
        #check that keys in filter match the column names
        self.check_column(filter)

        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "
        
        sql = sql[:-5] #remove the final AND 
        self.execute(f"""DELETE FROM student WHERE {sql}""", list(values))
            

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
    people = Students('school')
    
    ren = {
        'student_id': 1,
        'name': 'cassey',
        'age': 17,
        'year_enrolled': 2021,
        'graduating_year': 2022,
        'class_id': 1
    }

    ren_pt2 = {
        'student_id': 1,
        'name': 'cassey',
        'age': 18,
        'year_enrolled': 2021,
        'graduating_year': 2022,
        'class_id': 1
    }
    people.delete(ren_pt2)
    people.insert(ren)
    people.find({'name': 'cassey', 'age': 17})
    people.update({'name': 'cassey'}, {'age': 18})
    print(people.find({'name': 'cassey', 'age': 18}))
    found = people.find({'class_id': 1})
    for student in found:
        print(dict(student))
        print(student['name'])

