from flask import render_template, request
from model import ENTITIES
from db_utils import colls
import myhtml as html
import convert


def view(page_name: str):
    coll_name = page_name
    if page_name == 'student':
        coll_name = 'student-subject'
    entity = ENTITIES[coll_name]
    coll = colls[coll_name]

    record_filter = request.args.to_dict()
    records = coll.find(record_filter)
    table = '<div class="outline">🦧can\'t find anything</div>'

    form = html.RecordForm(f'/dashboard/view/{page_name}')
    form = convert.filter_to_form(record_filter, entity, form)
    form = f'<div class="center-form">{form.html()}</div>'

    if records:
        table = convert.records_to_table(records)
        table = f'<div class="outline">{table.html()}</div>'

    return render_template(
        'dashboard/view/view_entity.html',
        entity=page_name.title(),
        form=form,
        table=table,
    )

