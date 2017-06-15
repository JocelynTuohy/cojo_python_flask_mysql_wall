import re
from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnection
from flask_bcrypt import Bcrypt
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'i4w2oDf&EN7V3rBaIdpA&6N&Fr3idV0vzKBdWV#lNGusk2L3scs%b5fhnPi!g'
mysql = MySQLConnection(app, 'wall')
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    print 'hello'
    return render_template('index.html')




app.run(debug=True)