from typing import Any, Dict, Iterable, List, Optional, Tuple
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
    search_by: Optional[str] = None,
    filter: Optional[dict] = None
) -> html.EditableRecordTable:
    headers = list(records[0].keys())
    table = html.EditableRecordTable(
        headers=headers, action=action, method=method, search_by=search_by, filter=filter)
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


Records = List[Dict[str, Any]]


def post_data_to_records(
    post_data: Dict[str, List[str]],
    accepted_methods: Iterable[str],
    entity: model.Entity,
) -> Records:
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
            "method": "UPDATE" | "DELETE" | "INSERT"
        },
        {
            "old": {...},
            "new": {...},
            "method": "UPDATE" | "DELETE" | "INSERT"
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

    methods = post_data.get("method", [])
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

    for key in post_data:
        values = post_data.get(key)
        if len(values) != len(records):
            raise InvalidPostDataError(
                f'''Inconsistent number of records 🤡. length `{values}` != length `{records}`''')

        _key = key[4:]
        for idx, value in enumerate(values):
            if key.startswith('old:'):
                records[idx]['old'][_key] = value
            elif key.startswith('new:'):
                records[idx]['new'][_key] = value

    # 💀 its 10:07 PM and im tired pls help :(
    for field in entity.fields:
        for rec_data in records:
            value_old = rec_data['old'].get(field.name)
            value_new = rec_data['new'].get(field.name)

            if isinstance(field, data.Number):
                # numeric values submitted in post_data must be valid numbers
                if not value_old.isdecimal() and method != 'INSERT':
                    raise InvalidPostDataError(f'field `{field.name}`: `{value_old}` is not a number.')
                if not value_new.isdecimal():
                    raise InvalidPostDataError(f'field `{field.name}`: `{value_new}` is not a number.')

                if rec_data['method'] != 'INSERT':
                    rec_data['old'][field.name] = int(value_old)
                rec_data['new'][field.name] = int(value_new)

    return records


def old_new_records_to_submittable_tables(
    records: Records,
    entity: model.Entity,
    headers: List[str],
    **kwargs,
) -> Tuple[html.RecordTable, html.SubmittableRecordTable]:
    table_old = html.RecordTable(headers=headers)
    table_new_submit = html.SubmittableRecordTable(headers=headers, **kwargs)

    for recs in records:
        old_record = recs['old']
        new_record = recs['new']
        _method = recs['method']

        # validate the records
        if _method != 'INSERT':
            entity.from_dict(old_record)
        entity.from_dict(new_record)

        if _method == 'UPDATE' and new_record == old_record:
            continue
        # only add records with changes
        table_old.add_row(old_record)
        table_new_submit.add_row(old_record, new_record, _method)

    return table_old, table_new_submit


def old_new_records_to_tables(
    records: Records,
    entity: model.Entity,
    headers: List[str],
) -> Tuple[html.RecordTable, html.RecordTable]:
    table_old = html.RecordTable(headers=headers)
    table_new = html.RecordTable(headers=headers)

    for recs in records:
        old_record = recs['old']
        new_record = recs['new']
        method = recs['method']
        # validate records
        if method != 'INSERT':
            entity.from_dict(old_record)
        entity.from_dict(new_record)

        if method == 'DELETE':
            new_record = {k: f'🗑️<s>{v}</s>' for k, v in new_record.items()}
        table_old.add_row(old_record)
        table_new.add_row(new_record)

    return table_old, table_new
