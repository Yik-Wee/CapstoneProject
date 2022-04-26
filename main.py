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
    Student,
    StudentSubjectRecord
)
from frontend import (
    add
)

from db_utils import colls, delete_from_jt_coll, insert_into_jt_coll, update_jt_coll


app = Flask(__name__)


ENTITIES: Dict[str, Entity] = {
    'student': Student,
    'class': Class,
    'club': Club,
    'activity': Activity,
    'student-subject': StudentSubjectRecord,
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


@app.route('/dashboard/add/<page_name>/result', methods=['POST'])
@for_existing_pages(DASHBOARD_ADD_EXISTING_PAGES)
def add_entity_result(page_name: str):
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


# ------------------------------
# view existing Student/Class/Club/Activity
# ------------------------------
DASHBOARD_VIEW_EXISTING_PAGES = ('student', 'class', 'club', 'activity')


@app.route('/dashboard/view/<page_name>', methods=['GET'])
@for_existing_pages(DASHBOARD_VIEW_EXISTING_PAGES)
def view_entity(page_name: str):
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


# ------------------------------
# edit Membership(Student-Club)/Participation(Student-Activity)
# ------------------------------
ACCEPTED_METHODS = ('UPDATE', 'DELETE', 'INSERT')


@app.route('/dashboard/edit/<page_name>', methods=['GET', 'POST'])
@for_existing_pages(('membership', 'participation'))
def edit_relationship(page_name: str):
    if 'confirm' in request.args:
        return edit_relationship_confirm(page_name)

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


def edit_relationship_confirm(page_name: str):
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


@app.route('/dashboard/edit/<page_name>/result', methods=['POST'])
def edit_relationship_result(page_name: str):
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
