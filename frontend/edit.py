import convert
import data
from flask import render_template, request
from model import ENTITIES
from db_utils import colls, delete_from_jt_coll, insert_into_jt_coll, update_jt_coll
import myhtml as html

from .errors import invalid_post_data

ACCEPTED_METHODS = ('UPDATE', 'DELETE', 'INSERT')


def edit(page_name: str):
    record_filter = request.args.to_dict()  # conditions for left join
    coll = colls[page_name]  # e.g. membership coll for /membership

    # construct form to search for records
    # entity representing the many-to-many relationship
    entity = ENTITIES[page_name]
    form = html.RecordForm(action='', method='get')
    form = convert.entity_to_form_with_values(
        entity, form, record_filter).html()

    # find record(s) corresponding to the filter specifying JOIN condition
    try:  # handle error when filter has invalid keys
        records_to_edit = coll.find(record_filter)
    except KeyError:
        records_to_edit = []

    if len(records_to_edit) == 0:
        table = '<div class="outline">🦧 Found nothing</div>'
    else:
        # display table of members of the club. gives user the entire
        # INNER/LEFT JOIN student-club junction table to edit for simplicity
        table = convert.records_to_editable_table(
            records_to_edit, action='?confirm', method='post')
        header_types = convert.entity_to_header_types(entity=entity)
        table.set_header_types(header_types)
        table = f'''<div class="outline">
            <h3>✍️ Edit {entity.entity}s</h3>
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
        record_deltas = convert.post_data_to_record_deltas(
            post_data, ACCEPTED_METHODS, entity)
    except convert.InvalidPostDataError as err:
        return invalid_post_data(str(err))

    headers = list(record_deltas[0]['old'].keys())

    # confirming changes, display changes in old and new table
    try:
        action = f'/dashboard/edit/{page_name}/result'
        table_old, table_new = convert.record_deltas_to_tables(
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
        record_deltas = convert.post_data_to_record_deltas(
            post_data, ACCEPTED_METHODS, entity)
    except convert.InvalidPostDataError as err:
        return invalid_post_data(str(err))

    headers = list(record_deltas[0]['old'].keys())

    try:  # html table conversion includes data validation
        table_old, table_new = convert.record_deltas_to_tables(
            record_deltas, entity, headers)
    except data.ValidationFailedError as err:
        return render_template(
            'dashboard/edit/failure.html', entity=page_name.title(), error=str(err)), 400

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

        if not res.is_ok:
            return render_template(
                'dashboard/edit/failure.html', entity=page_name.title(), error=res.msg), 500

    return render_template(
        'dashboard/edit/success.html',
        entity=page_name.title(),
        table_old=table_old.html(),
        table_new=table_new.html()
    )
