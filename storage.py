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

class Students():
    def __init__(self, db_name):
        self.db_name = db_name
        self.column_names = ['student_id', 'name', 'age', 'year_enrolled', 'graduating_year']
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
            c.execute("""INSERT INTO student VALUES (?, ?, ?, ?, ?)""", list(record.values()))
            conn.commit()

    def find(self, filter: "dict") -> "dict":
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

        sql = sql[:-4]
        
        with sqlite3.connect(self.db_name) as conn:
            
            c = conn.cursor()
            c.execute(f"""SELECT * FROM student
                      WHERE {sql} """, list(values))
            record = c.fetchone()
            return record
            conn.commit()

        

    def update(self, filter, new_record) -> None:
        # with sqlite3.connect(self.db_name) as conn:
        #     c = conn.cursor()
        
        #     c.execute("""""")
        pass    
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

print('eorjgpoerg')
people = Students('school')
ren = {'student_id' : 1, 'name' : 'cassey', 'age' : 17, 'year_enrolled' : 2021, 'graduating_year' : 2022}

people.insert(ren)
print(people.find({'name' : 'cassey', 'age' : 17}))