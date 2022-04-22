class Collection:
    def __init__(self, key):
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
    def find(self, filter):
        return [
            {
                'name': 'OBAMA',
                'age': 69,
                'year_enrolled': 2008,
                'graduating_year': 2016,
            }
        ]
    pass


class Clubs(Collection):
    def find(self, filter):
        return [  # TETSING CODE
            {
                'name': 'HAPPY FUN CLUB',
            },
            {
                'name': 'EPIC POGGERS CLUB',
            },
            {
                'name': 'ILLEGAL SUBSTANCE ABUSE CLUB',
            },
        ]
        pass

    pass


class Activities(Collection):
    def find(self, filter):
        return [  # TESTING CODE
            {
                'description': 'yes',
                'start_date': '2022-01-01',
                'end_date': '2022-01-02',
            }
        ]

    pass


class Classes(Collection):
    pass


class Subjects(Collection):
    pass


class Membership(Collection):
    # ! TESTING CODE DO NOT ACTUALLY USE !
    def find(self, search_by: str, filter: dict):
        obama = {
            'student_name': 'OBAMA',
            'age': 69,
            'year_enrolled': 2008,
            'graduating_year': 2016,

            'club_name': 'HAPPY FUN CLUB',

            'role': 'POG MAN',
        }

        joe = {
            'student_name': 'biden',
            'age': 80,
            'year_enrolled': 2020,
            'graduating_year': 2024,

            'club_name': 'n club',

            'role': 'joe',
        }

        if filter.get('name') == 'OBAMA':
            return [obama]
        elif filter.get('name') == 'biden':
            return [joe]
        else:
            return [joe, obama]


class Participation(Collection):
    def find(self, filter):
        return [  # TESTING CODE
            {
                'name': 'Simp',
                'category': 'Achievement',
                'role': 'participant',
                'award': '',
                'hours': 4,
            },
            {
                'name': 'Obama',
                'category': 'Enrichment',
                'role': 'leader',
                'award': 'epic chad award',
                'hours': 9000,
            }
        ]

    pass


class StudentSubject(Collection):
    """Probably the most unimportant table in capstone project"""
    pass
