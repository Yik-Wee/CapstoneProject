from typing import Callable
import validate as valid


class ValidationFailedError(Exception):
    pass


class Field:
    """
    Base class which all subclasses must inherit.
    Fields are used by ER models, and by forms.

    Each field needs:
    - name
    - label
    - validator
    
    Each field generates:
    - formatted string
    - html <input> element
    """
    validate: Callable = NotImplemented

    def __init__(self, name: str, label: str):
        self.name = name
        self.label = label

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'name="{self.name}", '
            f'label="{self.label}"'
            ')'
        )


class Number(Field):
    """
    A field of numerical type.

    Arguments
    - name: str
    - label: str
    """
    validate: Callable = staticmethod(valid.number)

    def __init__(self, name: str, label: str):
        super().__init__(name, label)
        self.__value = None


class String(Field):
    """
    A field of string type.

    Arguments
    - name: str
    - label: str
    - (optional) validate: function
      Used to validate input values
    """
    validate: Callable = staticmethod(valid.string)

    def __init__(self, name: str, label: str):
        self.name = name
        self.label = label


class Email(String):
    """
    A field of string type constituting a valid email address.

    Arguments
    - name: str
    - label: str
    - (optional) validate: function
      Used to validate input values
    """
    validate: Callable = staticmethod(valid.email)

    def __init__(self, name: str, label: str):
        super().__init__(name, label)
        self.__value = None


class ContactNumber(String):
    """
    A field of string type constituting a valid contact number.

    Arguments
    - name: str
    - label: str
    - (optional) validate: function
      Used to validate input values
    """
    validate: Callable = staticmethod(valid.contact_number)

    def __init__(self, name: str, label: str):
        super().__init__(name, label)
        self.__value = None


class Date(String):
    """
    A field of date type.

    Arguments
    - name: str
    - label: str
    - (optional) validate: function
      Used to validate input values
    """
    validate: Callable = staticmethod(valid.date)

    def __init__(self, name: str, label: str):
        self.name = name
        self.label = label


class Year(Number):
    """
    A field of number type representing a year value.

    Arguments
    - name: str
    - label: str
    - (optional) validate: function
      Used to validate input values
    """
    validate: Callable = staticmethod(valid.year)

    def __init__(self, name: str, label: str):
        super().__init__(name, label)
        self.__value = None
