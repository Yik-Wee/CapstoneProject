from functools import wraps
from typing import Callable, Dict, Iterable

from flask import Flask, render_template, request

import convert
import data
import myhtml as html
from model import Activity, ActivityParticipant, Class, Club, Entity, ClubMember, Student
from storage import Activities, ActivityParticipants, Classes, ClubMembers, Clubs, Collection, Membership, Participation, Students

app = Flask(__name__)
# app.url_map.strict_slashes = False


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


ENTITIES: Dict[str, Entity] = {
    'student': Student,
    'class': Class,
    'club': Club,
    'activity': Activity,
    'member': ClubMember,
    'participant': ActivityParticipant,
}


# ------------------------------
# Error handling utils
# ------------------------------
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
    """Decorator to accept generic flask routes for specific page names - `pages`"""
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
DASHBOARD_ACTIONS = ('add', 'view', 'edit')


@app.route('/')
def index():
    """Splash page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard containing the allowed actions (e.g. Add, View, etc.)"""
    return render_template('dashboard/index.html')


@app.route('/dashboard/<action>')
def dashboard_action(action: str):
    if action not in DASHBOARD_ACTIONS:
        return not_found()
    return render_template(f'dashboard/{action}/index.html')


# ------------------------------
# Add new Club/Activity
# ------------------------------
DASHBOARD_ADD_EXISTING_PAGES = ('club', 'activity')


@app.route('/dashboard/add/<page_name>', methods=['GET', 'POST'])
@for_existing_pages(DASHBOARD_ADD_EXISTING_PAGES)
def add_entity(page_name: str):
    confirm = False
    table = None
    _Entity = ENTITIES[page_name]

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
@for_existing_pages(DASHBOARD_ADD_EXISTING_PAGES)
def add_entity_result(page_name: str):
    _Entity = ENTITIES[page_name]

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
DASHBOARD_VIEW_EXISTING_PAGES = ('student', 'class', 'club', 'activity')


@app.route('/dashboard/view/<page_name>', methods=['GET'])
@for_existing_pages(DASHBOARD_VIEW_EXISTING_PAGES)
def view_entity(page_name: str):
    # entity = entities_view[page_name]
    entity = ENTITIES[page_name]
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
ACCEPTED_METHODS = ('UPDATE', 'DELETE', 'INSERT')
DASHBOARD_EDIT_ER: Dict[str, Dict[str, Entity]] = {
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
DASHBOARD_EDIT_DROPDOWN_OPTIONS: Dict[str, Dict[str, str]] = {
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
@for_existing_pages(DASHBOARD_EDIT_ER)
def edit_relationship(page_name: str):
    # stuff to edit the Club Membership / Activity Participation
    table = None
    form = None
    relationship = DASHBOARD_EDIT_ER[page_name]

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
    options = DASHBOARD_EDIT_DROPDOWN_OPTIONS[page_name]
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
        entity_to_edit = ENTITIES[to_edit]
        header_types = convert.entity_to_header_types(entity=entity_to_edit)
        table_edit.set_header_types(header_types)
        table_edit = f'<div class="outline"><h3>✍️ Edit {entity_to_edit.entity}s</h3>{table_edit.html()}</div>'

        table = table_found + table_edit
    else:  # no records found
        table = '🦧can\'t find anything'

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=page_name.title(),
        form=form,
        table=table,
    )


def get_filter(post_data: dict, entity: Entity) -> dict:
    filter = {}
    for key in post_data:
        if key.startswith('filter:'):
            _key = key[7:]
            filter[_key] = post_data.get(key)[0]

    for key in filter:
        post_data.pop(f'filter:{key}')

    for field in entity.fields:
        value = filter.get(field.name)
        if value == '':
            filter.pop(field.name)
        elif value is not None and isinstance(field, data.Number):
            filter[field.name] = int(value)

    return filter


def edit_relationship_confirm(page_name: str, save_changes=False):
    relationship = DASHBOARD_EDIT_ER[page_name]
    post_data = request.form.to_dict(flat=False)
    search_by = post_data.pop('search_by', [None])[0]
    if search_by is None or search_by not in relationship:
        return invalid_post_data(f'field `search_by`: `{search_by}` is invalid')

    filter = get_filter(post_data, ENTITIES[search_by])
    to_edit = relationship[search_by]
    entity = ENTITIES[to_edit]

    try:
        records = convert.post_data_to_record_deltas(post_data, ACCEPTED_METHODS, entity)
    except convert.InvalidPostDataError as err:
        return invalid_post_data(str(err))
    
    headers = list(records[0]['old'].keys())

    if save_changes:  # not confirming anymore, edit database
        try:
            table_old, table_new = convert.record_deltas_to_tables(records, entity, headers)
        except data.ValidationFailedError as err:
            return render_template('dashboard/edit/failure.html', entity=page_name.title(), error=str(err)), 400

        table_search_by = convert.records_to_table([filter])
        coll = colls[page_name]

        for rec in records:  # update db to reflect changes
            method = rec['method']
            if method == 'DELETE':
                # coll.delete(filter, rec['old'])
                coll.delete(rec['old'])
            elif method == 'UPDATE':
                # coll.update(filter, rec['old'], rec['new'])
                coll.update(rec['old'], rec['new'])
            elif method == 'INSERT':
                # coll.insert(filter, rec['new'])
                coll.insert(rec['new'])

        return render_template(
            'dashboard/edit/success.html',
            entity=entity.entity,
            search_by=filter.get('name') or ENTITIES[search_by].entity,
            to_edit=to_edit,
            table_search_by=table_search_by.html(),
            table_old=table_old.html(),
            table_new=table_new.html()
        )

    # confirming changes, display changes in old and new table
    try:
        table_old, table_new = convert.record_deltas_to_submittable_tables(
            records,
            entity,
            headers,
            action=f'/dashboard/edit/{page_name}/result',
            method='post',
            search_by=search_by,
            filter=filter,
        )
    except data.ValidationFailedError as err:
        return render_template('dashboard/edit/failure.html', entity=page_name.title(), error=str(err)), 400

    if len(table_new.rows()) == 0:
        return render_template('dashboard/edit/failure.html', entity=page_name.title(), error='No changes made!'), 400

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=entity.entity,
        confirm=True,
        table_old=table_old.html(),
        table_new=table_new.html(),
    )


@app.route('/dashboard/edit/<page_name>/result', methods=['POST'])
def edit_relationship_result(page_name: str):
    return edit_relationship_confirm(page_name, save_changes=True)


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
    app.run('0.0.0.0')

    # for dev server:
    #app.run('localhost', port=3000, debug=True)
