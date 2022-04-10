from functools import wraps
import json
from typing import Callable, Dict, Iterable

from flask import Flask, redirect, render_template, request

import convert
import data
import myhtml as html
from model import Activity, ActivityParticipant, Class, Club, Entity, ClubMember, Student
from storage import Activities, ActivityParticipants, Classes, ClubMembers, Clubs, Collection, Membership, Participation, Students

app = Flask(__name__)
app.url_map.strict_slashes = False


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


@app.errorhandler(409)
def invalid_post_data(e):
    return render_template('errors.html', title='Invalid Post Data', error=e), 409


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
ACCEPTED_METHODS = ('UPDATE', 'DELETE')
ENTITIES: Dict[str, Entity] = {
    'student': Student,
    'member': ClubMember,
    'participant': ActivityParticipant,
    'club': Club,
    'activity': Activity,
}
edit_pages_er: Dict[str, Dict[str, Entity]] = {
    # search_by: to_edit
    'membership': {
        'student': 'club',
        'club': 'member',
    },
    'participation': {
        'student': 'activity',
        'activity': 'participant',
    }
}
edit_pages_dropdown_options: Dict[str, Dict[str, str]] = {
    'membership': {
        'student': 'Student (edit student\'s club(s))',
        'club': 'Club (edit club\'s members)',
    },
    'participation': {
        'student': 'Student (edit student\'s club(s))',
        'activity': 'Activity (edit activity\'s participant(s))'
    },
}


@app.route('/dashboard/edit/<page_name>', methods=['GET', 'POST'])
@for_existing_pages(edit_pages_er)
def edit_relationship(page_name: str):
    # stuff to edit the Club Membership / Activity Participation
    table = None
    form = None
    relationship = edit_pages_er[page_name]

    # e.g. search_by == 'student' -> find all clubs the student is in
    default_search_by = 'student'
    to_edit = 'club'
    search_by = request.args.get('search_by', default_search_by)
    if search_by not in relationship:
        search_by = default_search_by
    to_edit = relationship[search_by]

    search_by_coll = colls[search_by]
    to_edit_coll = colls[to_edit]

    if 'confirm' in request.args:
        return edit_relationship_confirm(page_name)

    # get record filter from request params
    filter = request.args.to_dict()
    print(filter)
    filter.pop('search_by', None)

    # construct form to search for records to edit which puts filter in get request params (request.args)
    options = edit_pages_dropdown_options[page_name]
    options = { search_by: options[search_by], **options }

    search_by_form = html.RecordForm(action='', method='get')
    search_by_form.dropdown_input('Search By', 'search_by', options)
    search_by_form.submit_input('👈 Choose')

    form = html.RecordForm(action='', method='get')
    form.hidden_input('search_by', search_by)
    form = convert.filter_to_form(filter, ENTITIES[search_by], form)
    form = search_by_form.html() + form.html()

    # find record(s) corresponding to the filter
    records = search_by_coll.find(filter)

    if len(records) > 1:
        # more than 1 record -> render selectable table (can select record from table)
        # e.g. if many students with same name but diff year_enrolled, age, ...
        table = convert.records_to_selectable_table(records, action='', search_by=search_by)
        table = '<h3>Choose One</h3>' + table.html()
    elif len(records) == 1:
        # exactly 1 (e.g. entity == 'student') record found -> return all clubs the student is in
        table_found = convert.records_to_table(records)
        table_found = f'<h3>೭੧(❛▿❛✿)੭೨ Found {search_by}</h3>' + table_found.html()

        records = to_edit_coll.find(filter)

        table_edit = convert.records_to_editable_table(
            records, action='?confirm', method='post', search_by=search_by, filter=filter)
        header_types = convert.entity_to_header_types(entity=ENTITIES[to_edit])
        table_edit.set_header_types(header_types)
        table_edit = f'<h3>✍️ Edit {to_edit}</h3>' + table_edit.html()

        table = table_found + table_edit
    else:  # no records found
        table = '🦧can\'t find anything'

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=page_name.title(),
        form=form,
        table=table,
    )


def get_search_by_and_filter(post_data: dict):
    search_by = post_data.pop('search_by', [None])[0]
    filter = {}
    for key in post_data:
        if key.startswith('filter:'):
            _key = key[7:]
            filter[_key] = post_data.get(key)[0]

    for key in filter:
        post_data.pop(f'filter:{key}')

    _entity = ENTITIES[search_by]
    for field in _entity.fields:
        value = filter.get(field.name)
        if value == '':
            filter.pop(field.name)
        elif value is not None and isinstance(field, data.Number):
            filter[field.name] = int(value)

    return search_by, filter


def edit_relationship_confirm(page_name: str):
    relationship = edit_pages_er[page_name]
    post_data = request.form.to_dict(flat=False)
    search_by, filter = get_search_by_and_filter(post_data)

    if search_by is None or search_by not in relationship:
        return invalid_post_data(f'field search_by: `{search_by}` is invalid')
    to_edit = relationship[search_by]
    entity = ENTITIES[to_edit]

    try:
        records = convert.post_data_to_records(post_data, ACCEPTED_METHODS, entity)
    except convert.InvalidPostDataError as err:
        return invalid_post_data(str(err))
    
    headers = list(records[0]['old'].keys())
    try:
        table_old, table_new = convert.old_new_records_to_submittable_tables(
            records, entity, headers,
            action=f'/dashboard/edit/{page_name}/result', method='post', search_by=search_by, filter=filter)
    except data.ValidationFailedError as err:
        return render_template('dashboard/edit/failure.html', error=str(err)), 400

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=entity.entity,
        confirm=True,
        table_old=table_old.html(),
        table_new=table_new.html(),
    )


@app.route('/dashboard/edit/<page_name>/result', methods=['POST'])
def edit_relationship_result(page_name: str):
    relationship = edit_pages_er[page_name]
    post_data = request.form.to_dict(flat=False)
    search_by, filter = get_search_by_and_filter(post_data)

    if search_by is None or search_by not in relationship:
        return invalid_post_data(f'field search_by: `{search_by}` is invalid')
    to_edit = relationship[search_by]
    entity = ENTITIES[to_edit]

    coll = colls[page_name]

    try:
        records = convert.post_data_to_records(post_data, ACCEPTED_METHODS, entity)
    except convert.InvalidPostDataError as err:
        return invalid_post_data(err)

    headers = list(records[0]['old'].keys())
    try:
        table_old, table_new = convert.old_new_records_to_tables(
            records, entity, headers)
    except data.ValidationFailedError as err:
        return render_template('dashboard/edit/failure.html', error=str(err)), 400

    table_search_by = convert.records_to_table([filter])

    for rec in records:
        method = rec['method']
        if method == 'DELETE':
            # coll.delete(filter, rec['old'])
            coll.delete(rec['old'])
        elif method == 'UPDATE':
            # coll.update(filter, rec['old'], rec['new'])
            coll.update(rec['old'], rec['new'])

    return render_template(
        'dashboard/edit/success.html',
        entity=entity.entity,
        search_by=filter.get('name') or ENTITIES[search_by].entity,
        to_edit=to_edit,
        table_search_by=table_search_by.html(),
        table_old=table_old.html(),
        table_new=table_new.html()
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
