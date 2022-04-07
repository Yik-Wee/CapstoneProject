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
    pass


class Clubs(Collection):
    def find(self, filter):
        return [  # TETSING CODE
            {
                'name': 'HAPPY FUN CLUB',
            },
        ]
        pass

    pass


class ClubMembers(Collection):
    def find(self, filter):
        return [  # TESTING CODE
            {
                'name': 'STUDENT 1',
                'age': '200',
                'year_enrolled': '1997',
                'graduating_year': '2008',
                'role': 'member',
            },
            {
                'name': 'STUDENT 2',
                'age': '18',
                'year_enrolled': '2021',
                'graduating_year': '2023',
                'role': 'president',
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


class Membership(Collection):
    def find(self, filter):
        return [  # TESTING CODE
            {
                'name': 'Simp',
                'role': 'member',
            },
            {
                'name': 'Obama',
                'role': 'president',
            },
        ]
        pass


class ActivityParticipants(Collection):
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
