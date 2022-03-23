from data import ValidationFailedError, String, Date


class Entity:
    """
    Base class that all Entity subclasses must inherit from.

    Subclasses must have a `fields` attribute consisting of
    a list of fields.
    """
    entity = NotImplemented
    fields = NotImplemented
    def __init__(self, **kwargs):
        for field in self.fields:
            value = kwargs[field.name]
            if field.validate(value):
                setattr(self, field.name, value)
            else:
                raise ValidationFailedError(f'Invalid field, `{field.name}`: `{value}`')

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
    - YearEnrolled: int
    - GraduatingYear: int
    """
    entity = 'Student'
    fields = [
        String('name', 'Name (as in NRIC)'),
        String('class', 'Class'),
        Date('dob', 'Date of birth'),
    ]


class Class(Entity):
    entity = 'Class'
    field = []  # ...


class Club(Entity):
    """
    Fields:
    - Name: str
    """
    entity = 'Club'
    fields = [
        # ...
        String('name', 'Name of club'),
    ]


class Activity(Entity):
    entity = 'Activity'
    fields = [
        # ...
    ]
