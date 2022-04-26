from functools import wraps
from typing import Callable, Iterable

from flask import Flask, render_template, request

import frontend

app = Flask(__name__)


# ------------------------------
# Error handling utils
# ------------------------------
DEFAULT_404_ERR_MSG = (
    '404 Not Found: The requested URL was not found on the server. '
    'If you entered the URL manually please check your spelling and try again.'
)


@app.errorhandler(404)
def not_found(e=DEFAULT_404_ERR_MSG):
    return frontend.not_found(e)


@app.errorhandler(409)
def invalid_post_data(e):
    return frontend.invalid_post_data(e)


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
    return frontend.add(page_name)


@app.route('/dashboard/add/<page_name>/result', methods=['POST'])
@for_existing_pages(DASHBOARD_ADD_EXISTING_PAGES)
def add_entity_result(page_name: str):
    return frontend.add_res(page_name)


# ------------------------------
# view existing Student/Class/Club/Activity
# ------------------------------
DASHBOARD_VIEW_EXISTING_PAGES = ('student', 'class', 'club', 'activity')


@app.route('/dashboard/view/<page_name>', methods=['GET'])
@for_existing_pages(DASHBOARD_VIEW_EXISTING_PAGES)
def view_entity(page_name: str):
    return frontend.view(page_name)


# ------------------------------
# edit Membership(Student-Club)/Participation(Student-Activity)
# ------------------------------
ACCEPTED_METHODS = ('UPDATE', 'DELETE', 'INSERT')


@app.route('/dashboard/edit/<page_name>', methods=['GET', 'POST'])
@for_existing_pages(('membership', 'participation'))
def edit_relationship(page_name: str):
    if 'confirm' in request.args:
        return frontend.edit_confirm(page_name)
    return frontend.edit(page_name)


@app.route('/dashboard/edit/<page_name>/result', methods=['POST'])
def edit_relationship_result(page_name: str):
    return frontend.edit_res(page_name)


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
