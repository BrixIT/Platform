from flask import redirect, url_for, request, render_template, render_template_string, jsonify
from platform_flask import app
from platform_flask.components.packages import get_packages


@app.route('/packages')
def packages():
    packages = get_packages()
    return render_template('packages.html', packages=packages)
