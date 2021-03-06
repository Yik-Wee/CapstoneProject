from flask import render_template, request
from model import ENTITIES
from database import colls
import myhtml as html
import convert
from ._helpers import remove_empty_keys_from_filter


def view(page_name: str):
    coll_name = page_name
    if page_name == 'student':  # only for student, view student and their subjects
        coll_name = 'student-subject'
    entity = ENTITIES[coll_name]
    coll = colls[coll_name]

    record_filter = request.args.to_dict()
    remove_empty_keys_from_filter(record_filter)
    records = coll.find(record_filter)
    table = '<div class="outline">🦧can\'t find anything</div>'

    form = html.RecordForm(f'/dashboard/view/{page_name}')
    form = convert.entity_to_form_with_values(entity, form, record_filter)
    form = f'<div class="center-form">{form.html()}</div>'

    # LEFT JOIN-ed with student-subject, but SOME PPL didnt put subject_id
    # so subject_id becomes None (NULL) cause not in table
    for rec in records:
        id_ = rec.get('id')
        if 'student_id' in rec.keys():
            rec['student_id'] = id_

    if records:
        table = convert.records_to_table(records, headers=entity.fields)
        table = f'<div class="outline">{table.html()}</div>'

    return render_template(
        'dashboard/view/view_entity.html',
        entity=page_name.title(),
        form=form,
        table=table,
    )
