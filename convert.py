from typing import List
from wsgiref import headers
import data
import model
import myhtml as html


def __add_input_by_field(
    form: html.RecordForm,
    field: data.Field,
    value: str = ''
) -> None:
    if isinstance(field, data.Date):
        form.date_input(field.label, field.name, value=value)
    elif isinstance(field, data.Email):
        form.email_input(field.label, field.name, value=value)
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
    on fields in entity.

    Return:
    - form
    """
    for field in entity.fields:
        __add_input_by_field(form, field)
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
    Converts the list of records (`records`) into a `RecordTable`,
    assuming each record: `dict` has the same keys and `records` is
    not empty.
    Uses keys from `records[0]` as headers for the `RecordTable`.
    """
    headers = records[0].keys()
    table = html.RecordTable(headers=headers)
    for record in records:
        table.add_row(record)
    return table


def filter_to_form(filter: dict, entity: model.Entity, form: html.RecordForm) -> html.RecordForm:
    # a bit scuffed 🗿
    for field in entity.fields:
        value = filter.get(field.name)
        __add_input_by_field(form, field, value=value or '')
    form.submit_input()
    return form
