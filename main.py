from functools import wraps
from typing import Callable, Dict, Iterable

from flask import Flask, render_template, request

import convert
import data
import myhtml as html
from model import (
    Activity,
    ParticipationRecord,
    Class,
    Club,
    Entity,
    MembershipRecord,
    Student
)
from storage import (
    Activities,
    Classes,
    Clubs,
    Collection,
    Membership,
    Participation,
    StudentSubject,
    Students,
    Subjects
)

app = Flask(__name__)


# TODO change collection initialisation when storage.py is done (too lazy do now)
colls: Dict[str, Collection] = {
    'student': Students(key='student_id'),
    'club': Clubs(key='club_id'),
    'class': Classes(key='class_id'),
    'activity': Activities(key='activity_id'),
    'subject': Subjects(key='subject_id'),
    'membership': Membership(key=None),
    'participation': Participation(key=None),
    'student-subject': StudentSubject(key=None),
}


ENTITIES: Dict[str, Entity] = {
    'student': Student,
    'class': Class,
    'club': Club,
    'activity': Activity,
    'membership': MembershipRecord,
    'participation': ParticipationRecord,
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
    """Decorator to accept generic flask routes for specific page names"""
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
    # TODO when viewing student, SELECT ... FROM student LEFT JOIN subject ON (...filter)
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
MEMBERSHIP_RELATION = ('student', 'club')


@app.route('/dashboard/edit/membership', methods=['GET', 'POST'])
def edit_membership():
    if 'confirm' in request.args:
        return edit_membership_confirm()

    filter = request.args.to_dict()
    search_by = filter.pop('search_by', None)
    if search_by not in MEMBERSHIP_RELATION:
        search_by = MEMBERSHIP_RELATION[0]
    coll = colls['membership']

    # construct form to search for records to edit which puts filter in get
    # request params (request.args)
    form = convert.edit_membership_search_form(
        filter, search_by, ENTITIES[search_by])

    # find record(s) corresponding to the filter
    # TODO IMPLEMENT ASSUMPTIONS IN storage.py? (ask cassey to do probably)
    # ! ASSUMING FIND RETURNS EVERYTHING FOR EMPTY FILTER
    # ! AND "name" FIELDS ARE DIFFERENT ("student_name", "club_name", ...)
    records_to_edit = coll.find(search_by, filter)

    # display table of members of the club. gives user the entire
    # INNER/LEFT JOIN student-club junction table to edit for simplicity
    table_edit = convert.records_to_editable_table(
        records_to_edit, action='?confirm', method='post')
    entity_to_edit = ENTITIES['membership']
    header_types = convert.entity_to_header_types(entity=entity_to_edit)
    table_edit.set_header_types(header_types)
    table_edit = f'''<div class="outline">
        <h3>✍️ Edit {entity_to_edit.entity}s</h3>
        {table_edit.html()}
    </div>'''
    table = table_edit

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity='Membership',
        form=form,
        table=table,
    )


def edit_membership_confirm():
    post_data = request.form.to_dict(flat=False)
    entity = ENTITIES['membership']
    try:
        record_deltas = convert.post_data_to_record_deltas(
            post_data, ACCEPTED_METHODS, entity)
    except convert.InvalidPostDataError as err:
        return invalid_post_data(str(err))

    headers = list(record_deltas[0]['old'].keys())

    # confirming changes, display changes in old and new table
    try:
        table_old, table_new = convert.record_deltas_to_submittable_tables(
            record_deltas, entity, headers, action='/dashboard/edit/membership/result', method='post')
    except data.ValidationFailedError as err:
        return render_template('dashboard/edit/failure.html', entity='Membership', error=str(err)), 400

    if len(table_new.rows()) == 0:
        return render_template('dashboard/edit/failure.html', entity='Membership', error='No changes made!'), 400

    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=entity.entity,
        confirm=True,
        table_old=table_old.html(),
        table_new=table_new.html(),
    )


@app.route('/dashboard/edit/membership/result', methods=['POST'])
def edit_membership_result():
    post_data = request.form.to_dict(flat=False)
    entity = ENTITIES['membership']
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
        return render_template('dashboard/edit/failure.html', entity='Membership', error=str(err)), 400

    coll = colls['membership']

    for rec_delta in record_deltas:  # save changes to db
        method = rec_delta['method']
        old_rec = rec_delta['old']
        new_rec = rec_delta['new']

        # TODO impl junction table colls in storage.py (do outline for cassey + docstrings with below expl)
        # the junction table coll should find the student_id and club_id from the old/new rec
        # e.g. old_rec = { 'student_name': 'OBAMA', ..., 'club_name': 'POG CLUB', ..., 'role': 'president' }
        #      then it should detect: student_id = 6, club_id = 9
        #      if method == 'DELETE', it should execute:
        #      DELETE FROM membership
        #      WHERE
        #          student_id = 6 AND
        #          club_id = 9 AND
        #          role = 'president';

        # TODO handle sqlite3 exceptions (?)
        if method == 'INSERT':
            coll.insert(new_rec)
        elif method == 'UPDATE':
            coll.update(old_rec, new_rec)
        elif method == 'DELETE':
            coll.delete(old_rec)

    return render_template(
        'dashboard/edit/success.html',
        entity='Membership',
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
