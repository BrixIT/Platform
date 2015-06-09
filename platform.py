from flask import Flask, session, redirect, url_for, escape, request

from flask.ext.mako import MakoTemplates, render_template

app = Flask(__name__)
mako = MakoTemplates(app)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
