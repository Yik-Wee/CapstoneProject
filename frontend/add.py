from flask import render_template, request

from model import ENTITIES
import myhtml as html
import data
import convert
from db_utils import colls


def add(page_name: str) -> str:
    confirm = False
    table = None
    _entity = ENTITIES[page_name]

    if 'confirm' in request.args:
        try:
            entity = _entity.from_dict(request.form.to_dict())
        except data.ValidationFailedError as err:
            return render_template(
                'dashboard/add/failure.html',
                entity=_entity.entity,
                error=str(err),
            ), 400
        else:
            form = html.RecordForm(
                f'/dashboard/add/{page_name}/result', 'post')
            form = convert.entity_to_hidden_form(entity, form)
            table = convert.entity_to_table(entity)
            confirm = True
    else:
        form = html.RecordForm(f'/dashboard/add/{page_name}?confirm', 'post')
        form = convert.entity_to_new_form(_entity, form)

    form = f'<div class="center-form">{form.html()}</div>'
    table = f'<div class="outline">{table.html()}</div>' if table else ''

    return render_template(
        'dashboard/add/add_entity.html',
        entity=_entity.entity,
        form=form,
        table=table,
        confirm=confirm,
    )


def add_res(page_name: str):
    _entity = ENTITIES[page_name]

    try:
        entity = _entity.from_dict(request.form.to_dict())
    except data.ValidationFailedError as err:
        return render_template(
            'dashboard/add/failure.html',
            entity=_entity.entity,
            error=str(err),
        ), 400
    else:
        colls[page_name].insert(entity.as_dict())  # TODO handle insert errors?
        table = convert.entity_to_table(entity)
        table = table = f'<div class="outline">{table.html()}</div>'
        return render_template(
            'dashboard/add/success.html',
            entity=entity.entity,
            table=table,
        )
