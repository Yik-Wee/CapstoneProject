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
        return [  # TESTING CODE
            {
                'name': 'STUDENT 1',
                'age': '200',
                'year_enrolled': '1997',
                'graduating_year': '2008',
            },
            {
                'name': 'STUDENT 2',
                'age': '18',
                'year_enrolled': '2021',
                'graduating_year': '2023',
            },
        ]
        pass


class Clubs(Collection):
    def find(self, filter):
        return [  # TETSING CODE
            {
                'name': 'CLUB 1',
            },
        ]
        pass

    pass


class Activities(Collection):
    pass


class Classes(Collection):
    pass


class Membership(Collection):
    def find(self, filter):
        return [  # TESTING CODE
            {
                'name': 'STUDENT 1',
                'age': '200',
                'year_enrolled': '1997',
                'graduating_year': '2008',
            },
            {
                'name': 'STUDENT 2',
                'age': '18',
                'year_enrolled': '2021',
                'graduating_year': '2023',
            },
        ]
        pass


class Participation(Collection):
    pass
