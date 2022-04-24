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