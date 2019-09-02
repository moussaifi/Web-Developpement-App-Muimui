from flask import render_template
from app import app


@app.errorhandler(403)
def forbidden(e):
    ''' Handle error 403 '''
    return render_template('error.html', message='403 forbidden'), 403


@app.errorhandler(404)
def page_not_found(e):
    ''' Handle error 404 '''
    return render_template('error.html', message='404 not found'), 404


@app.errorhandler(410)
def gone(e):
    ''' Handle error 410 '''
    return render_template('error.html', message='410 gone'), 410


@app.errorhandler(500)
def internal_error(e):
    ''' Handle error 500 '''
    return render_template('error.html', message='500 internal error'), 500
