student_sql = """CREATE TABLE IF NOT EXISTS Student(
                    id INTEGER, 
                    student_name TEXT,
                    age INTEGER,
                    year_enrolled INTEGER,
                    graduating_year INTEGER,
                    class_id INTEGER,
                    PRIMARY KEY(id)
                    )"""

subject_sql = """CREATE TABLE IF NOT EXISTS Subject(
                    id INTEGER, 
                    subject_name TEXT,
                    subject_level TEXT,
                    PRIMARY KEY(id)
                    )"""

club_sql = """CREATE TABLE IF NOT EXISTS Club(
                    id INTEGER,
                    club_name TEXT,
                    PRIMARY KEY(id)
                    )"""

activity_sql = """CREATE TABLE IF NOT EXISTS Activity(
                    id INTEGER,
                    start_date TEXT,
                    end_date TEXT,
                    desc TEXT,
                    PRIMARY KEY(id)
                    )"""

class_sql = """CREATE TABLE IF NOT EXISTS Class(
                    id INTEGER,
                    name TEXT,
                    level TEXT,
                    PRIMARY KEY(id)
                    )"""

student_club_sql = """CREATE TABLE IF NOT EXISTS Student_club(
                    student_id INTEGER,
                    club_id INTEGER,
                    role TEXT,
                    PRIMARY KEY(student_id, club_id),
                    FOREIGN KEY(club_id) REFERENCES Club(id),
                    FOREIGN KEY(student_id) REFERENCES Student(id)
                    )"""

student_subject_sql = """CREATE TABLE IF NOT EXISTS Student_subject(
                    student_id INTEGER,
                    subject_id INTEGER,
                    PRIMARY KEY(student_id, subject_id),
                    FOREIGN KEY(student_id) REFERENCES(Student),
                    FOREIGN KEY(subject_id) REFERENCES(Subject)
                    )"""

student_activity_sql = """CREATE TABLE IF NOT EXISTS Student_activity(
                    student_id INTEGER, 
                    activity_id INTEGER, 
                    category TEXT,
                    role TEXT,
                    award TEXT,
                    hours TEXT,
                    PRIMARY KEY(student_id, activity_id),
                    FOREIGN KEY(student_id) REFERENCES(Student),
                    FOREIGN KEY(activity_id) REFERENCES(Activity)
                    )"""