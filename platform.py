from flask import Flask
from flask.ext.mako import MakoTemplates, render_template

app = Flask(__name__)
mako = MakoTemplates(app)


@app.route('/')
def hello_world():
    return render_template('hello.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
