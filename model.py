from typing import List
from data import Field, Number, ValidationFailedError, String, Date, Year


class Entity:
    """
    Base class that all Entity subclasses must inherit from.

    Subclasses must have a `fields` attribute consisting of
    a list of fields.
    """
    entity: str = NotImplemented
    fields: List[Field] = NotImplemented

    def __init__(self, **kwargs):
        for field in self.fields:
            value = kwargs[field.name]
            if field.validate(value):
                setattr(self, field.name, value)
            else:
                raise ValidationFailedError(
                    f'Invalid field, `{field.name}`: `{value}`')

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.name}")'

    @classmethod
    def blank(cls):
        """Instantiates an empty Entity"""
        blank_rec = {}
        for field in cls.fields:
            blank_rec[field.name] = None
        return cls(**blank_rec)

    @classmethod
    def from_dict(cls, dict_):
        """Instantiates Entity from a dict"""
        return cls(**dict_)

    def as_dict(self):
        """Returns the record as a dict."""
        rec = {}
        for field in self.fields:
            rec[field.name] = getattr(self, field.name)
        return rec

    def get(self, key):
        return getattr(self, key)


class Student(Entity):
    """
    Fields:
    - Name: str
    - Age: int
    - Year Enrolled: int
    - Graduating Year: int
    """
    entity = 'Student'
    fields = [
        String('student_name', 'Name (as in NRIC)'),
        Number('age', 'Age'),
        Year('year_enrolled', 'Year Enrolled'),
        Year('graduating_year', 'Graduating Year'),
    ]


class Class(Entity):
    """
    Fields:
    - Name: str
    - Level: str {JC1, JC2}
    """
    entity = 'Class'
    fields = [
        String('class_name', 'Name'),
        String('level', 'Level'),  # {JC1, JC2}
    ]


class Club(Entity):
    """
    Fields:
    - Name: str
    """
    entity = 'Club'
    fields = [
        String('club_name', 'Name of club'),
    ]


class Activity(Entity):
    entity = 'Activity'
    fields = [
        Date('start_date', 'Start Date'),
        Date('end_date', 'End Date'),  # optional
        String('description', 'Description'),
    ]


class MembershipRecord(Entity):
    entity = 'Member'
    fields = [
        *Student.fields,
        *Club.fields,
        # String('name', 'Name (as in NRIC)'),
        String('role', 'Role'),  # default 'member'
    ]


class ParticipationRecord(Entity):
    entity = 'Participant'
    fields = [
        *Student.fields,
        *Activity.fields,
        # String('name', 'Name (as in NRIC)'),
        String('category', 'Category'),  # {Achievement, Enrichment, Leadership, Service}
        String('role', 'Role'),  # default 'participant'
        String('award', 'Award'),  # optional
        Number('hours', 'Hours'),  # optional
    ]
