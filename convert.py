from typing import Any, Dict, Iterable, List, Tuple, TypedDict, Union
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
    on fields in entity.

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
    for field in entity.fields:
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


def filter_to_form(
    record_filter: dict,
    entity: model.Entity,
    form: html.RecordForm
) -> html.RecordForm:
    """
    Convert the filter containing all or some of the `entity`'s fields to a
    form. Like `entity_to_hidden_form()` but not hidden & skips validation
    """
    for field in entity.fields:
        value = record_filter.get(field.name)
        __add_input_by_field(form, field, value=value or '')
    form.submit_input()
    return form


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


"""
Utils to handle record changes (`RecordDeltas`)
The http post data in `request.form` contains the old records to be changed
and the new records to be changed to. `post_data_to_records()` does this
conversion and returns a list of records represented as dicts containing
this information. These are aliased as `RecordDeltas` for convenience.
"""


class InvalidPostDataError(Exception):
    pass


class RecordDelta(TypedDict):
    method: str
    new: dict[str, Any]
    old: dict[str, Any]


RecordDeltas = List[RecordDelta]
"""
The list of record changes in the format:
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
"""


def post_data_to_record_deltas(
    post_data: Dict[str, List[str]],
    accepted_methods: Iterable[str],
    entity: model.Entity,
) -> RecordDeltas:
    """
    Convert the post data `req_form` to `RecordDeltas`.

    Params
    ------
    `entity`: `Entity`
    - Used to cast fields into the appropriate types
      e.g. "year" field: str -> int

    Raises
    ------
    `InvalidPostDataError`
    - if any "method" field in `req_form` is not in `accepted_methods`
    - if there is an inconsistent number of records in the post data
      e.g. each key's list of values has a different length in `req_form`

    Return
    ------
    `RecordDeltas`. See documentation for `RecordDeltas` for format of
    returned data.
    """

    methods = post_data.get("method", [])
    record_deltas: RecordDeltas = []

    for method in methods:
        if method not in accepted_methods:
            raise InvalidPostDataError(
                'field `method` must be string literal "UPDATE" or "DELETE" 🤡')

        record_deltas.append({
            "old": {},
            "new": {},
            "method": method,
        })

    for key in post_data:
        values = post_data.get(key)
        if len(values) != len(record_deltas):
            raise InvalidPostDataError(
                f'Inconsistent number of records 🤡. \
                length `{values}` != length `{record_deltas}`')

        _key = key[4:]
        for idx, value in enumerate(values):
            if key.startswith('old:'):
                record_deltas[idx]['old'][_key] = value
            elif key.startswith('new:'):
                record_deltas[idx]['new'][_key] = value

    # 💀 its 10:07 PM and im tired pls help :(
    for field in entity.fields:
        for rec_delta in record_deltas:
            value_old = rec_delta['old'].get(field.name)
            value_new = rec_delta['new'].get(field.name)
            method = rec_delta['method']

            if isinstance(field, data.Number) and not isinstance(field, data.OptionalNumber):
                # numeric values submitted in post_data must be valid numbers
                if not value_old.isdecimal() and method != 'INSERT':
                    raise InvalidPostDataError(
                        f'field `{field.name}`: `{value_old}` \
                        is not a number.')
                if not value_new.isdecimal():
                    raise InvalidPostDataError(
                        f'field `{field.name}`: `{value_new}` \
                        is not a number.')

                if rec_delta['method'] != 'INSERT':
                    rec_delta['old'][field.name] = int(value_old)
                rec_delta['new'][field.name] = int(value_new)

    return record_deltas


def record_deltas_to_tables(
    record_deltas: RecordDeltas,
    entity: model.Entity,
    headers: List[str],
    **kwargs,
) -> Tuple[html.RecordTable, html.RecordDeltaTable]:
    """
    Converts the `record_deltas` to a normal `RecordTable` and a
    `SubmittableRecordTable` which encapsulates the `RecordDeltas`
    to be submitted in a post request.

    Params
    ------
    `record_deltas`: `RecordDeltas`
    - The changes to the records to be displayed in the 2 tables, and
      encapsulated in the `SubmittableRecordTable`
    `entity`: `Entity`
    - The entity to be used for data validation of the `RecordDeltas`.
    `headers`: `List[str]`
    - The headers of the 2 tables.

    Return
    ------
    A tuple in the format: `(record_table, submittable_record_table)`
    """
    table_old = html.RecordTable(headers=headers)
    table_new_submit = html.RecordDeltaTable(headers=headers, **kwargs)

    for rec_delta in record_deltas:
        old_record = rec_delta['old']
        new_record = rec_delta['new']
        method = rec_delta['method']

        # validate the records
        if method != 'INSERT':
            entity.from_dict(old_record)
        entity.from_dict(new_record)

        if method == 'UPDATE' and new_record == old_record:
            continue
        # only add records with changes
        table_old.add_row(old_record)
        table_new_submit.add_row(rec_delta)

    return table_old, table_new_submit
