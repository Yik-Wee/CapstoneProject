"""
Convert data to html
"""

from typing import Any, Dict, List
import data
import model
import myhtml as html


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
    form.submit_input('Search')
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
    headers = entity.fields
    table = html.RecordTable(headers=headers)
    table.add_row(record)
    return table


def records_to_table(records: List[dict], headers: List[data.Field]) -> html.RecordTable:
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
    table = html.RecordTable(headers=headers)
    for record in records:
        table.add_row(record)
    return table


def records_to_editable_table(
    records: List[dict],
    headers: List[data.Field],
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
    table = html.EditableRecordTable(headers=headers, **kwargs)
    for record in records:
        table.add_row(record)
    return table
