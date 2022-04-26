"""
Storage classes to interface with the db.
"""

import sqlite3
from typing import List
import schema as s

class Collection:
    """
    Storage base class to interface with the db

    Attributes
    ----------
    column_names: List[str]
    - The names of the columns in the table

    db_path: str
    - The path to the db file

    table_name: str
    - The name of the table

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

    column_names: List[str] = NotImplemented
    table_name: str = NotImplemented

    def __init__(self, db_path: str) -> None:
        """Initialise a Collection which interfaces with the db specified by `db_path`"""
        self.db_path = db_path

    def check_column(self, to_check: dict) -> None:
        # Check that filter keys are valid column names
        for key, value in to_check.items():
            if key not in self.column_names:
                raise KeyError(f"{key} is not a valid column name")

    def execute(self, sql: str, values: list) -> List[dict]:  # execute sql
        with sqlite3.connect(self.db_path) as conn:
            # make returned stuff from c.fetch a dict instead of tuple
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(sql, values)
            results = c.fetchall()
            conn.commit()
            # conn.close() is automatic

            # results is empty (e.g. if doing SELECT ... and nothing found, [] returned)
            if results == []:
                return []
            else:  # not empty, something returned
                actually_dict = []  # initialise list of dicts
                for record in results:  # convert each sqlite3.Row in the results to a dict
                    actually_dict.append(dict(record))
                return actually_dict

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
        
        self.check_column(record)

        existing_records = self.find(record) # to check if the record alr exists
        if len(existing_records) > 0:  # integrity error as records must be unique
            raise sqlite3.IntegrityError(f'Record already exists')

        q_marks = ''
        columns = []
        values = []
        for key, value in record.items():  # to figure out number of question marks
            columns.append(key)
            values.append(value)
            q_marks += '?, '
        q_marks = q_marks[:-2]

        columns = ', '.join(columns)
        self.execute(
            f"""INSERT INTO {self.table_name} ({columns})
            VALUES ({q_marks})""", values)

    def find(self, filter: dict) -> List[dict]:
        """
        Return all rows matching the `filter` specifications.
        Return all columns from each record in the format
        {
            'column_1': ...,
            'column_2': ...,
        }
        """

        # Check that filter keys are valid column names
        self.check_column(filter)

        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "  # for the WHERE part
        sql = sql[:-4]  # remove the final AND

        sql = f"""SELECT * 
                  FROM {self.table_name}
                  WHERE {sql} """

        return self.execute(sql, list(values))

    def update(self, filter: dict, new_record: dict) -> None:
        """
        Update the old record(s) specified by `filter` with the `new_record`.
        """

        #check the columns in both filter and new_record
        self.check_column(filter)
        self.check_column(new_record)

        #sql for the SET part
        keys = new_record.keys()
        new_values = new_record.values()
        new_sql = ''

        for key in keys:
            new_sql += f"{key} = ?, "
        new_sql = new_sql[:-2]  # remove the final ', '

        #sql for the WHERE part
        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "

        sql = sql[:-4]  # remove the final AND
        both = list(new_values) + list(values)

        sql = f"""UPDATE {self.table_name} 
                  SET {new_sql}
                  WHERE {sql} """

        return self.execute(sql, list(both))

    def delete(self, filter: dict) -> None:
        """
        Delete the records from the table matching the `filter`.
        """

        #check that keys in filter match the column names
        self.check_column(filter)

        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "
        sql = sql[:-5]  # remove the final AND

        self.execute(
            f"""DELETE FROM {self.table_name} WHERE {sql}""", list(values))

class Students(Collection):
    table_name = 'Student'
    column_names = ['id', 'student_name', 'age',
                    'year_enrolled', 'graduating_year', 'class_id']
    # super.__init__(db_path)
    # self.execute(s.student_sql, ())

    def __init__(self, db_path):
        self.db_path = db_path
        self.execute(s.student_sql, ())
  
class Subjects(Collection):
    table_name = 'Subject'
    column_names = ['id', 'subject_name', 'subject_level']

    def __init__(self, db_path):
        self.db_path = db_path
        self.execute(s.subject_sql, ())


class Clubs(Collection):
    table_name = 'Club'
    column_names = ['id', 'club_name']

    def __init__(self, db_path):
        self.db_path = db_path
        self.execute(s.club_sql, ())


class Activities(Collection):
    table_name = 'Activity'
    column_names = ['id', 'start_date', 'end_date', 'desc']

    def __init__(self, db_path):
        self.db_path = db_path
        self.execute(s.activity_sql, ())


class Classes(Collection):
    table_name = 'Class'
    column_names = ['id', 'class_name', 'level']

    def __init__(self, db_path):
        self.db_path = db_path
        self.execute(s.class_sql, ())


# ------------------------------
# JUNCTION TABLES
# (insert, update and delete should be the same)
# ------------------------------

class Membership(Collection):
    """Junction table for Student-Club membership many-to-many relationship"""

    table_name = 'Student_club'
    column_names = ['student_id', 'club_id', 'role']
    joined_column_names = [
        *Students.column_names,
        *Clubs.column_names,
        *column_names
    ]

    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.execute(s.student_club_sql, ())

    def find(self, filter: dict) -> dict:
        """
        Find all records in the membership/student-club table matching filter, returning
        records in student, club and student-club tables (LEFT JOIN-ed)

        e.g. consider the student OBAMA who is a member of WHITE HOUSE and OBAMA FOUNDATION
        """

        # get join conditions from filter (the WHERE part)
        # self.check_column(filter)
        for key in filter:  # check column names
            if key not in self.joined_column_names:
                raise KeyError(f'Invalid key {key}')

        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "  # for the WHERE part
        sql = sql[:-4]  # remove the final AND

        # execute sqlite left join e.g.
        sql = f"""SELECT *
                FROM Student
                LEFT JOIN Student_club
                ON Student.id = Student_club.student_id
                LEFT JOIN Club
                ON Club.id = Student_club.club_id
                WHERE {sql};"""
               
        return self.execute(sql, list(values))

class StudentSubject(Collection):  # not that impt
    """Junction table for Student-Subject many-to-many relationship"""

    table_name = 'Student_subject'
    column_names = ['student_id', 'subject_id']
    joined_column_names = [
        *Students.column_names,
        *Subjects.column_names,
        *column_names
    ]

    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.execute(s.student_subject_sql, ())

    def find(self, filter: dict) -> dict:
        """
        Find all records in the student-subject table matching filter, returning
        records in student, subject and student-subject tables (LEFT JOIN-ed) (see Membership)
        """

        # get join conditions from filter (the WHERE part)
        # self.check_column(filter) #check column names
        for key in filter:  # check column names
            if key not in self.joined_column_names:
                raise KeyError(f'Invalid key {key}')


        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "  # for the WHERE part
        sql = sql[:-4]  # remove the final AND


        # execute sqlite left join e.g.
        sql = f"""SELECT *
                    FROM Student
                    LEFT JOIN Student_subject
                    ON Student.id = Student_subject.student_id
                    LEFT JOIN Subject
                    ON Subject.id = Student_subject.subject_id
                    WHERE {sql}"""

        return self.execute(sql, list(values))

class Participation(Collection):
    """Junction table for Student-Activity participation many-to-many relationship"""

    table_name = 'Student_activity'
    column_names = ['student_id', 'subject_id', 'category', 'role', 'award', 'hours']
    joined_column_names = [
        *Students.column_names,
        *Activities.column_names,
        *column_names
    ]

    def __init__(self, db_path: str):
        super().__init__(db_path)
        self.execute(s.student_activity_sql, ())

    def find(self, filter: dict) -> dict:
        """
        Find all records in the student-subject table matching filter, returning
        records in student, subject and student-subject tables (LEFT JOIN-ed) (see Membership)
        """

        # get join conditions from filter (the WHERE part)
        # self.check_column(filter) #check column names
        for key in filter:  # check column names
            if key not in self.joined_column_names:
                raise KeyError(f'Invalid key {key}')

        conditions = filter.keys()
        values = filter.values()
        sql = ''

        for condition in conditions:
            sql += f"{condition} = ? AND "  # for the WHERE part
        sql = sql[:-4]  # remove the final AND


        # execute sqlite left join e.g.
        sql = f"""SELECT *
                    FROM Student
                    LEFT JOIN Student_activity
                    ON Student.id = Student_activity.student_id
                    LEFT JOIN Activity
                    ON Activity.id = Student_activity.activity_id
                    WHERE {sql}"""

# if __name__ == '__main__':
#     student = Students('test.db')
#     student.insert({
#         'id': 1,
#         'student_name': 'OBAMA',
#         'age': 10,
#         'year_enrolled': 2008,
#         'graduating_year': 2016,
#     })
#     student.insert({
#         'student_name': 'JOEBAMA',
#         'age': 9,
#         'year_enrolled': 2021,
#         'graduating_year': 2024,
#     })
#     club = Clubs('test.db')
#     club.insert({
#         'id': 1,
#         'club_name': 'OBAMA FOUNDATION',
#     })
#     club.insert({
#         'club_name': 'WHITE HOUSE',
#     })
#     membership = Membership('test.db')
#     membership.insert({
#         'student_id': 1,
#         'club_id': 1,
#         'role': 'leader',
#     })
#     membership.insert({
#         'student_id': 1,
#         'club_id': 2,
#         'role': 'member',
#     })
#     membership.insert({
#         'student_id': 2,
#         'club_id': 2,
#         'role': 'president'
#     })

#     obamas_clubs = membership.find({
#         'student_name': 'OBAMA'
#     })
#     print(obamas_clubs)

#     white_house_members = membership.find({
#         'club_name': 'WHITE HOUSE'
#     })
#     print(white_house_members)

#     # testing code
#     # people = Students()

#     # ren = {
#     #     'id': 1,
#     #     'name': 'cassey',
#     #     'age': 17,
#     #     'year_enrolled': 2021,
#     #     'graduating_year': 2022,
#     #     'class_id': 1
#     # }

#     # ren_pt2 = {
#     #     'id': 1,
#     #     'name': 'cassey',
#     #     'age': 18,
#     #     'year_enrolled': 2021,
#     #     'graduating_year': 2022,
#     #     'class_id': 1
#     # }
#     # people.delete(ren_pt2)
#     # people.insert(ren)
#     # print(people.find({'name': 'cassey', 'age': 17}))
#     # print('\n')
#     # people.update({'name': 'cassey'}, {'age': 18})
#     # print(people.find({'name': 'cassey', 'age': 18}))

#     # people = Subject('school')
#     # subject1 = {'id': 1, 'subject_name': 'MATH', 'subject_level': 'H2'}
#     # people.insert(subject1)
#     # print(people.find({'id': 1}))
#     # people.update({'id': 1}, {'subject_level': 'H1'})
#     # print(people.find({'id': 1}))

#     # people = Clubs('school')
#     # club1 = {'id':1, 'club_name':'AV'}
#     # people.delete(club1)
#     # people.insert(club1)
#     # print(people.find({'id':1}))
#     # people.update({'id': 1}, {'club_name':'AV'})
#     # print(people.find({'id':1}))
