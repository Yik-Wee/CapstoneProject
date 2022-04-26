from flask import render_template


def not_found(e: str):
    return render_template('errors.html', title='Page Not Found', error=e), 404


def invalid_post_data(e: str) -> str:
    return render_template('errors.html', title='Invalid Post Data', error=e), 409
