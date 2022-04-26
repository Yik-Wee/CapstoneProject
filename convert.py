"""
Convert data to html or to other data
"""

from typing import Any, Dict, List, Union
import data
import model
import myhtml as html

# ------------------------------
# Functions to convert data to html
# ------------------------------


def __add_input_by_field(
    form: html.RecordForm,
    field: data.Field,
    value: str = ''
) -> None:
    """
    Add an input of specific type to the `form` based on the `field` type
    """
    if isinstance(field, data.Date):
        form.date_input(field.label, field.name, value=value)
    elif isinstance(field, data.Email):
        form.email_input(field.label, field.name, value=value)
    elif isinstance(field, data.ConstrainedString):
        options = field.constraints.copy()
        options.insert(0, '')  # <- empty field
        if value in options:
            options.remove(value)
            options.insert(0, value)
        form.dropdown_input(field.label, field.name, options)
    elif isinstance(field, data.String):
        form.text_input(field.label, field.name, value=value)
    elif isinstance(field, data.Number):
        form.number_input(field.label, field.name, value=value)
    else:  # fallback input type
        form.text_input(field.label, field.name, value=value)


def entity_to_new_form(
    entity: model.Entity,
    form: html.RecordForm,
) -> html.RecordForm:
    """
    Takes in two arguments, an entity and a form.
    Populates the form with appropriate inputs, based
    on search_fields in entity.

    Return:
    - form
    """
    for field in entity.fields:
        __add_input_by_field(form, field)
    form.submit_input()
    return form


def entity_to_form_with_values(
    entity: model.Entity,
    form: html.RecordForm,
    values: Dict[str, Any],
) -> html.RecordForm:
    for field in entity.search_fields:
        value = values.get(field.name, '')
        __add_input_by_field(form, field, value)
    form.submit_input()
    return form


def entity_to_hidden_form(
    entity: model.Entity,
    form: html.RecordForm,
) -> html.RecordForm:
    """
    Takes in two arguments, an entity and a form.
    Populates the form with hidden inputs, based
    on fields in entity.

    Return:
    - form
    """
    for field in entity.fields:
        form.hidden_input(field.name, getattr(entity, field.name))
    form.submit_input("Yes")
    return form


def entity_to_table(entity: model.Entity) -> html.RecordTable:
    """
    Takes in an entity argument.
    Returns a table object populated with data in entity.

    Return:
    - table
    """
    record = entity.as_dict()
    table = html.RecordTable(headers=record.keys())
    table.add_row(record)
    return table


def records_to_table(records: List[dict]) -> html.RecordTable:
    """
    IMPORTANT
    ---------
    Skips data validation. Only use if `records` don't need validation
    (e.g. `records` are obtained from the database itself)

    ---------
    Converts the list of records (`records`) into a `RecordTable`,
    assuming each record: `dict` has the same keys and `records` is
    not empty.
    Uses keys from `records[0]` as headers for the `RecordTable`.
    """
    headers = list(records[0].keys())
    table = html.RecordTable(headers=headers)
    for record in records:
        table.add_row(record)
    return table


def records_to_editable_table(
    records: List[dict],
    **kwargs
) -> html.EditableRecordTable:
    """
    IMPORTANT
    ---------
    Skips data validation. Only use if `records` don't need validation
    (e.g. `records` are obtained from the database itself)

    ---------
    Converts the `records` to `EditableRecordTable` using `**kwargs`
    """
    headers = list(records[0].keys())
    table = html.EditableRecordTable(headers=headers, **kwargs)
    for record in records:
        table.add_row(record)
    return table


# ------------------------------
# Functions/Utils to convert data to non-html
# ------------------------------


def __field_to_input_type(field: data.Field) -> Union[str, List[str]]:
    """
    Returns the type of the html input tag based on the `field` instance
    """
    if isinstance(field, data.Date):
        return 'date'
    elif isinstance(field, data.Email):
        return 'email'
    elif isinstance(field, data.ConstrainedString):
        return field.constraints
    elif isinstance(field, data.String):
        return 'text'
    elif isinstance(field, data.Number):
        return 'number'
    return 'text'  # fallback input type


def entity_to_header_types(entity: model.Entity) -> Dict[str, str]:
    """
    Get the input types of the fields of the `entity`.
    e.g. For `entity`: `Student` with fields
        String('name', 'Name (as in NRIC)'),
        Number('age', 'Age'),
        Year('year_enrolled', 'Year Enrolled'),
        Year('graduating_year', 'Graduating Year'),
    the input/header types are
        {
            'name': 'text',
            'age': 'number',
            'year_enrolled': 'year',
            'graduating_year': 'year',
        }
    """
    header_types = {}
    for field in entity.fields:
        input_type = __field_to_input_type(field)
        header_types[field.name] = input_type
    return header_types
