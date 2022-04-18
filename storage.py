import sqlite3

class Collection:
    def __init__(self, db_name):

            
        pass

    def insert(self, record):
        pass

    def find(self, filter):
        pass

    def update(self, filter, new_record):
        pass

    def delete(self, filter):
        pass


class Students(Collection):
    def __init__(self, db_name):
        self.db_name = db_name
        with sqlite3.connect(self.db_name) as conn:
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

    def insert(self, record: "dict") -> None:
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO student VALUES (?, ?, ?, ?, ?)""", record.values())
            c.commit()

    def find(self, filter: "dict") -> "dict":
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""SELECT * FROM student
                      WHERE """)

    def update(self, filter, new_record) -> None:
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""""")

            
    def delete(self, filter):
        pass

            
class Subject(Collection):
    pass

    
class Clubs(Collection):
    pass


class Activities(Collection):
    pass


class Classes(Collection):
    pass

