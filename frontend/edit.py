from flask import render_template, request
import convert
import data
import myhtml as html
from database import colls
from database.db_utils import (
    delete_from_jt_coll,
    insert_into_jt_coll,
    update_jt_coll
)
from model import ENTITIES

from .errors import invalid_post_data
from ._helpers import (
    remove_empty_keys_from_filter,
    record_deltas_to_tables,
    post_data_to_record_deltas,
    InvalidPostDataError
)

ACCEPTED_METHODS = ('UPDATE', 'DELETE', 'INSERT')


def edit(page_name: str):
    record_filter = request.args.to_dict()  # conditions for left join
    remove_empty_keys_from_filter(record_filter)
    coll = colls[page_name]  # e.g. membership coll for /membership

    # construct form to search for records
    # entity representing the many-to-many relationship
    entity = ENTITIES[page_name]
    form = html.RecordForm(action='', method='get')
    form = convert.entity_to_form_with_values(
        entity, form, record_filter)
    form = f'<div class="center-form">{form.html()}</div>'

    # find record(s) corresponding to the filter specifying JOIN condition
    try:  # handle error when filter has invalid keys
        all_records_to_edit = coll.find(record_filter)
    except KeyError:
        all_records_to_edit = []

    records_to_edit = []
    for rec in all_records_to_edit:
        rec_to_edit = {}
        for field in entity.fields:
            rec_to_edit[field.name] = rec.get(field.name, '')
        records_to_edit.append(rec_to_edit)

    headers = entity.fields
    if len(records_to_edit) == 0:
        msg = '🦧 Found nothing'
    else:
        msg = f'✍️ Edit {entity.entity}s'

    # display table of members of the club
    table = convert.records_to_editable_table(
        records_to_edit, headers=headers, action='?confirm', method='post')
    table = f'''<div class="outline">
        <h3>{msg}</h3>
        {table.html()}
    </div>'''

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=page_name.title(),
        form=form,
        table=table,
    )


def edit_confirm(page_name: str):
    post_data = request.form.to_dict(flat=False)
    entity = ENTITIES[page_name]
    try:
        record_deltas = post_data_to_record_deltas(
            post_data, ACCEPTED_METHODS, entity)
    except InvalidPostDataError as err:
        return invalid_post_data(str(err))

    headers = entity.fields

    # confirming changes, display changes in old and new table
    try:
        action = f'/dashboard/edit/{page_name}/result'
        table_old, table_new = record_deltas_to_tables(
            record_deltas, entity, headers, action=action, method='post', submittable=True)
    except data.ValidationFailedError as err:
        return render_template(
            'dashboard/edit/failure.html', entity=page_name.title(), error=str(err)), 400

    if len(table_new.rows()) == 0:
        return render_template(
            'dashboard/edit/failure.html', entity=page_name.title(), error='No changes made!'), 400

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=entity.entity,
        confirm=True,
        table_old=table_old.html(),
        table_new=table_new.html(),
    )


def edit_res(page_name: str):
    post_data = request.form.to_dict(flat=False)
    entity = ENTITIES[page_name]
    try:
        record_deltas = post_data_to_record_deltas(
            post_data, ACCEPTED_METHODS, entity)
    except InvalidPostDataError as err:
        return invalid_post_data(str(err))

    headers = entity.fields

    try:  # html table conversion includes data validation
        table_old, table_new = record_deltas_to_tables(record_deltas, entity, headers)
    except data.ValidationFailedError as err:
        return render_template(
            'dashboard/edit/failure.html', entity=page_name.title(), error=str(err)), 400

    errors = []
    total_edits = 0
    for rec_delta in record_deltas:  # save changes to db
        method = rec_delta['method']
        old_rec = rec_delta['old']
        new_rec = rec_delta['new']

        if method == 'INSERT':
            res = insert_into_jt_coll(page_name, new_rec)
        elif method == 'UPDATE':
            res = update_jt_coll(page_name, old_rec, new_rec)
        elif method == 'DELETE':
            res = delete_from_jt_coll(page_name, old_rec)

        total_edits += 1
        if not res.is_ok:
            errors.append(res.msg)

    error_count = len(errors)
    if error_count > 0:
        err_msg = f'<h3>{total_edits} Edits Made With {error_count} Errors</h3>'
        err_msg += '<br>'.join(errors)
        return render_template(
            'dashboard/edit/failure.html', entity=page_name.title(), error=err_msg), 500

    return render_template(
        'dashboard/edit/success.html',
        entity=page_name.title(),
        table_old=table_old.html(),
        table_new=table_new.html()
    )
