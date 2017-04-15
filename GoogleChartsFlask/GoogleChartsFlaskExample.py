"""
Example of using Google Charts with Python Flask.
Flask is able to simply start WWW server with no more code than required.
Impressive!
"""

from flask import Flask
from flask import render_template
from random import randint

app = Flask(__name__)
temp = [['Label', 'Value'],
        ['Output', 0],
        ['Temp', 0],
        ['Return', 0]]


@app.route('/')
@app.route('/index')
def index():
    global temp
    pageTitle = "Chart Example"
    for clock in range(1, 4):
        temp[clock][1] = randint(0, 100)
    return render_template('index.html', pageTitle=pageTitle, temp=temp)


app.run(port=80, debug=False)
