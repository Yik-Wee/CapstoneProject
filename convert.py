from typing import Any, Dict, Iterable, List, Optional
import data
import model
import myhtml as html
from werkzeug.datastructures import ImmutableMultiDict as __ImmutableMultiDict


# ------------------------------
# Functions to convert data to html
# ------------------------------


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
    headers = list(records[0].keys())
    table = html.RecordTable(headers=headers)
    for record in records:
        table.add_row(record)
    return table


def records_to_selectable_table(
    records: List[dict],
    action: str = '',
    method: str = 'get',
    search_by: Optional[str] = None
) -> html.SelectableRecordTable:
    headers = list(records[0].keys())
    table = html.SelectableRecordTable(
        headers=headers, action=action, method=method, search_by=search_by)
    for record in records:
        table.add_row(record)
    return table


def records_to_editable_table(
    records: List[dict],
    action: str = '',
    method: str = 'post',
    search_by: Optional[str] = None
) -> html.EditableRecordTable:
    headers = list(records[0].keys())
    table = html.EditableRecordTable(
        headers=headers, action=action, method=method, search_by=search_by)
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


# ------------------------------
# Functions/Utils to convert data to non-html
# ------------------------------


def __field_to_input_type(field: data.Field) -> str:
    if isinstance(field, data.Date):
        return 'date'
    elif isinstance(field, data.Email):
        return 'email'
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


class InvalidPostDataError(Exception):
    pass


def req_form_to_records(
    req_form: Dict[str, List[str]],
    accepted_methods: Iterable[str],
    entity: model.Entity,
) -> List[Dict[str, Any]]:
    """
    Convert the post data `req_form` to records in the format:
    ```json
    [
        {
            "old": {
                "name": ...,
                "...": ...,
            },
            "new": {
                "name": ...,
                "...": ...,
            },
            "method": "UPDATE" | "DELETE"
        },
        {
            "old": {...},
            "new": {...},
            "method": "UPDATE" | "DELETE"
        },
        ...
    ]
    ```

    `entity`: `Entity`
    - Used to cast fields into the appropriate types (e.g. "year" field: str -> int)

    Raises
    ------
    `InvalidPostDataError`
    - if any "method" field in `req_form` is not in `accepted_methods`
    - if there is an inconsistent number of records in the post data
      e.g. each key's list of values has a different length in `req_form`

    Return
    ------
    """

    methods = req_form.get("method")
    records = []

    for method in methods:
        if method not in accepted_methods:
            raise InvalidPostDataError(
                'field `method` must be string literal "UPDATE" or "DELETE" 🤡')

        records.append({
            "old": {},
            "new": {},
            "method": method,
        })

    for key in req_form:
        values = req_form.get(key)
        if len(values) != len(records):
            raise InvalidPostDataError('Inconsistent number of records 🤡')

        _key = key[4:]
        for idx, value in enumerate(values):
            if key.startswith('old:'):
                records[idx]['old'][_key] = value
            elif key.startswith('new:'):
                records[idx]['new'][_key] = value

    # 💀 its 10:07 PM and im tired pls help :(
    for field in entity.fields:
        print(field)
        for rec_data in records:
            value_old = rec_data['old'].get(field.name)
            value_new = rec_data['new'].get(field.name)

            if isinstance(field, data.Number):
                print(f'\t{value_old}, {value_new}, {field.name}')
                print(f'\t{rec_data}')
                if value_old is not None:
                    rec_data['old'][field.name] = int(value_old)
                if value_new is not None:
                    rec_data['new'][field.name] = int(value_new)

    return records
