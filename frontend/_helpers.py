"""
Utils to remove empty keys from the search filter

AND

Utils to handle record changes (`RecordDeltas`)
The http post data in `request.form` contains the old records to be changed
and the new records to be changed to. `post_data_to_records()` does this
conversion and returns a list of records represented as dicts containing
this information. These are aliased as `RecordDeltas` for convenience.
"""


from typing import Any, Dict, Iterable, List, Tuple, TypedDict
import myhtml as html
import model
import data


def remove_empty_keys_from_filter(record_filter: dict) -> None:
    keys_to_pop = []
    for key, value in record_filter.items():
        if value in ('', None):
            keys_to_pop.append(key)
    for key in keys_to_pop:
        record_filter.pop(key)


class InvalidPostDataError(Exception):
    pass


class RecordDelta(TypedDict):
    """
    Represents a record change/diff in the format:
    ```
    {
        "old": {...},
        "new": {...},
        "method": "UPDATE" | "DELETE" | "INSERT"
    }
    ```
    """
    old: Dict[str, Any]
    new: Dict[str, Any]
    method: str


RecordDeltas = List[RecordDelta]


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
    - Used to cast fields into the appropriate types e.g. "year" field: str -> int

    Raises
    ------
    `InvalidPostDataError`
    - if any "method" field in `req_form` is not in `accepted_methods`
    - if there is an inconsistent number of records in the post data
      e.g. each key's list of values has a different length in `req_form`

    Return
    ------
    `RecordDeltas` (list of record changes with keys "old", "new" & "method")
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

    for field in entity.fields:
        for rec_delta in record_deltas:
            value_old = rec_delta['old'].get(field.name)
            value_new = rec_delta['new'].get(field.name)
            method = rec_delta['method']

            if isinstance(field, data.Number) and not isinstance(field, data.OptionalNumber):
                # numeric values submitted in post_data must be valid numbers
                if not value_old.isdecimal() and method != 'INSERT':
                    raise InvalidPostDataError(
                        f'field `{field.name}`: `{value_old}` is not a number.')
                if not value_new.isdecimal():
                    raise InvalidPostDataError(
                        f'field `{field.name}`: `{value_new}` is not a number.')

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
    A tuple in the format: `(record_table, record_delta_table)`
    """
    table_old = html.RecordTable(headers=headers)
    table_new_submit = html.RecordDeltaTable(headers=headers, **kwargs)

    for rec_delta in record_deltas:
        old_record = rec_delta['old']
        new_record = rec_delta['new']
        method = rec_delta['method']

        # validate the records & convert empty fields to NULL (None)
        if method != 'INSERT':
            old_record = entity.from_dict(old_record).as_dict()
        new_record = entity.from_dict(new_record).as_dict()

        if method == 'UPDATE' and new_record == old_record:
            continue
        # only add records with changes
        table_old.add_row(old_record)
        table_new_submit.add_row(rec_delta)

    return table_old, table_new_submit
