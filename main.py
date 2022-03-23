from functools import wraps
from typing import Callable, Dict, Iterable

from flask import Flask, redirect, render_template, request

import convert
import data
import myhtml as html
from model import Activity, Class, Club, Student
from storage import Activities, Classes, Clubs, Collection, Students

app = Flask(__name__)


coll: Dict[str, Collection] = {
    'students': Students(key='student_id'),
    'clubs': Clubs(key='club_id'),
    'classes': Classes(key='class_id'),
    'activities': Activities(key='activity_id'),
}


# ------------------------------
# Error handling utils
# ------------------------------

DASHBOARD_ACTIONS = ('add', 'view', 'edit')

DEFAULT_404_ERR_MSG = (
    "404 Not Found: The requested URL was not found on the server. "
    "If you entered the URL manually please check your spelling and try again."
)


@app.errorhandler(404)
def not_found(e=DEFAULT_404_ERR_MSG):
    return render_template('not_found.html', error=e), 404


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
entities_add = {
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
                error=err,
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
            error=err,
        ), 400
    else:
        coll['students'].insert(entity.as_dict())
        table = convert.entity_to_table(entity)
        return render_template(
            'dashboard/add/success.html',
            entity=entity.entity,
            table=table.html(),
        )


# ------------------------------
# view existing Student/Class/Club/Activity
# ------------------------------
entities_view = {
    'student': Student,
    'class': Class,
    'club': Club,
    'activity': Activity,
}


@app.route('/dashboard/view/<page_name>', methods=['GET'])
@for_existing_pages(entities_view)
def view_entity(page_name: str):
    _Entity = entities_view[page_name]
    # ...
    # view entity based on `request.args`
    return render_template(
        'dashboard/view/view_entity.html',
        entity=_Entity.entity,
    )


# ------------------------------
# edit Membership(Student-Club)/Participation(Student-Activity)
# ------------------------------
pages_edit = {
    'membership': None,
    'participation': None,
}


@app.route('/dashboard/edit/<page_name>', methods=['GET', 'POST'])
@for_existing_pages(pages_edit)
def edit_entity(page_name: str):
    # ...
    # stuff to edit the Club Membership / Activity Participation
    return render_template(
        'dashboard/edit/edit_entity.html',
        entity=page_name,
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
    app.run('0.0.0.0')

    # for dev server:
    # app.run('localhost', port=3000, debug=True)
