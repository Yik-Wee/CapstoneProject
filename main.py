from functools import wraps
from typing import Callable, Dict, Iterable

from flask import Flask, redirect, render_template, request

import convert
import data
import myhtml as html
from model import Activity, ActivityParticipant, Class, Club, Entity, ClubMember, Student
from storage import Activities, ActivityParticipants, Classes, ClubMembers, Clubs, Collection, Membership, Participation, Students

app = Flask(__name__)


colls: Dict[str, Collection] = {
    'student': Students(key='student_id'),
    'club': Clubs(key='club_id'),
    'class': Classes(key='class_id'),
    'activity': Activities(key='activity_id'),
    'member': ClubMembers(key='student_id'),
    'participant': ActivityParticipants(key='student_id'),
    'membership': Membership(key=None),
    'participation': Participation(key=None),
}


# ------------------------------
# Error handling utils
# ------------------------------

DASHBOARD_ACTIONS = ('add', 'view', 'edit')

DEFAULT_404_ERR_MSG = (
    '404 Not Found: The requested URL was not found on the server. '
    'If you entered the URL manually please check your spelling and try again.'
)


@app.errorhandler(404)
def not_found(e=DEFAULT_404_ERR_MSG):
    return render_template('errors.html', title='Page Not Found', error=e), 404


def for_existing_pages(pages: Iterable):
    def decorator(callback: Callable):
        @wraps(callback)
        def wrapper(page_name: str):
            if page_name in pages:
                return callback(page_name)
            return not_found()
        return wrapper
    return decorator


# ------------------------------
# Routes
# ------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard/index.html')


@app.route('/dashboard/<action>')
def dashboard_action(action: str):
    if action not in DASHBOARD_ACTIONS:
        return not_found()
    return render_template(f'dashboard/{action}/index.html')


# ------------------------------
# Add new Club/Activity
# ------------------------------
entities_add: Dict[str, Entity] = {
    'club': Club,
    'activity': Activity,
}


@app.route('/dashboard/add/<page_name>', methods=['GET', 'POST'])
@for_existing_pages(entities_add)
def add_entity(page_name: str):
    confirm = False
    table = None
    _Entity = entities_add[page_name]

    if 'confirm' in request.args:
        try:
            entity = _Entity.from_dict(request.form.to_dict())
        except data.ValidationFailedError as err:
            return render_template(
                'dashboard/add/failure.html',
                entity=_Entity.entity,
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
        form = convert.entity_to_new_form(_Entity, form)

    return render_template(
        'dashboard/add/add_entity.html',
        entity=_Entity.entity,
        form=form.html(),
        table=table.html() if table else '',
        confirm=confirm,
    )


@app.route('/dashboard/add/<page_name>/result', methods=['POST'])
@for_existing_pages(entities_add)
def add_entity_result(page_name: str):
    _Entity = entities_add[page_name]

    try:
        entity = _Entity.from_dict(request.form.to_dict())
    except data.ValidationFailedError as err:
        return render_template(
            'dashboard/add/failure.html',
            entity=_Entity.entity,
            error=str(err),
        ), 400
    else:
        colls[page_name].insert(entity.as_dict())
        table = convert.entity_to_table(entity)
        return render_template(
            'dashboard/add/success.html',
            entity=entity.entity,
            table=table.html(),
        )


# ------------------------------
# view existing Student/Class/Club/Activity
# ------------------------------
entities_view: Dict[str, Entity] = {
    'student': Student,
    'class': Class,
    'club': Club,
    'activity': Activity,
}


@app.route('/dashboard/view/<page_name>', methods=['GET'])
@for_existing_pages(entities_view)
def view_entity(page_name: str):
    entity = entities_view[page_name]
    coll = colls[page_name]

    filter = request.args.to_dict()
    records = coll.find(filter)
    table = '🦧can\'t find anything'

    form = html.RecordForm(f'/dashboard/view/{page_name}')
    form = convert.filter_to_form(filter, entity, form)

    if records:
        table = convert.records_to_table(records)
        table = table.html()

    return render_template(
        'dashboard/view/view_entity.html',
        entity=entity.entity,
        form=form.html(),
        table=table,
    )


# ------------------------------
# edit Membership(Student-Club)/Participation(Student-Activity)
# ------------------------------
pages_edit_er_models: Dict[str, Dict[str, Entity]] = {
    'membership': {
        'member': ClubMember,  # TODO change 'student' to 'member'; Student to Member
        'club': Club,
    },
    'participation': {
        'participant': ActivityParticipant,
        'activity': Activity,
    },
}


@app.route('/dashboard/edit/<page_name>', methods=['GET', 'POST'])
@for_existing_pages(pages_edit_er_models)
def edit_relationship(page_name: str):
    # stuff to edit the Club Membership / Activity Participation
    coll = colls[page_name]
    table = None
    form = None
    relationship = pages_edit_er_models[page_name]

    # e.g. search_by == 'student' -> find all clubs the student is in
    # default_search_by = 'member' if page_name == 'membership'
    default_search_by = list(relationship.keys())[0]
    search_by = request.args.get('search_by', default_search_by)
    if search_by not in relationship:
        search_by = default_search_by

    search_by_coll = colls[search_by]

    if 'confirm' in request.args:
        return edit_relationship_confirm(page_name, search_by)  # handle confirm


    # get record filter from request params
    filter = request.args.to_dict()

    # construct form to search for records to edit which puts filter in get request params (request.args)
    _Entity = relationship[search_by]
    form = html.RecordForm(action='', method='get')
    options = {name: entity.entity for name, entity in relationship.items()}
    options = {search_by: _Entity.entity, **options}
    form.dropdown_input('Search By', 'search_by', options)
    form.submit_input('👈 Choose')
    form = convert.filter_to_form(filter, relationship[search_by], form)
    form = form.html()

    # find record(s) corresponding to the filter
    records = search_by_coll.find(filter)

    if len(records) > 1:
        # more than 1 record -> render selectable table (can select record from table)
        # e.g. if many students with same name but diff year_enrolled, age, ...
        table = convert.records_to_selectable_table(records, action='', search_by=search_by)
        table = '<h3>Choose One</h3>' + table.html()
    elif len(records) == 1:
        # exactly 1 (e.g. entity == 'student') record found -> return all clubs the student is in
        records = coll.find(filter)
        table = convert.records_to_editable_table(records, action='?confirm', method='post', search_by=search_by)

        _entities = list(relationship.keys())
        _idx = _entities.index(search_by)
        _entity_key = _entities[_idx ^ 1]
        entity = relationship[_entity_key]

        header_types = convert.entity_to_header_types(entity)
        print(search_by, entity, header_types)
        table.set_header_types(header_types)
        table = table.html()
    else:  # no records found
        table = '🦧can\'t find anything'

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=page_name,
        form=form,
        table=table,
    )


ACCEPTED_METHODS = ('UPDATE', 'DELETE')


def edit_relationship_confirm(page_name: str, search_by: str) -> str:
    relationship = pages_edit_er_models[page_name]
    entity = relationship[search_by]

    try:
        records = convert.req_form_to_records(request.form, ACCEPTED_METHODS, entity)
        import json
        print(json.dumps(records, indent=2))
    except convert.InvalidPostDataError as err:
        return render_template(
            'errors.html',
            title='Invalid Post Data',
            error=str(err)
        ), 409
    
    headers = list(records[0]['old'].keys())
    # TODO submittable record table instead of static record table
    table_old = html.RecordTable(headers=headers)
    table_new = html.RecordTable(headers=headers)

    for recs in records:  # put info is a bad name but wtv
        old_record = recs['old']
        new_record = recs['new']
        try:  # validate the records
            entity.from_dict(old_record)
            entity.from_dict(new_record)
        except data.ValidationFailedError as err:
            return render_template(
                'dashboard/edit/failure.html',
                error=str(err),
            ), 400
        else:
            table_old.add_row(old_record)  # TODO cancel out deleted rows
            table_new.add_row(new_record)

        # if method == 'UPDATE':
        #     coll.update(old_record, new_record)
        # elif method == 'DELETE':
        #     coll.delete(old_record)

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=entity.entity,
        confirm=True,
        table_old=table_old.html(),
        table_new=table_new.html(),
    )


@app.route('/login')
def login():
    return 'Under Construction'


@app.route('/profile')
def profile():
    return 'Under Construction'


@app.route('/admin')
def admin():
    return 'Under Construction'


if __name__ == '__main__':
    # for production server:
    # app.run('0.0.0.0')

    # for dev server:
    app.run('localhost', port=3000, debug=True)
