import re
import time
from datetime import datetime
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
    # print 'hello'
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check():
    # if registering:
    if 'reg_submit' in request.form:
        # print request.form
        # first name: letters only, at least 2 characters, was submitted
        if len(request.form['reg_first_name']) < 2:
            flash('First name must include at least two characters.', 'reg')
        if not request.form['reg_first_name'].isalpha():
            flash('First name may only include alphabetic characters.', 'reg')
        # last name: letters only, at least 2 characters, was submitted
        if len(request.form['reg_last_name']) < 2:
            flash('Last name must include at least two characters.', 'reg')
        if not request.form['reg_last_name'].isalpha():
            flash('Last name may only include alphabetic characters.', 'reg')
        # email: valid format, was submitted
        if not EMAIL_REGEX.match(request.form['reg_email']):
            flash('Please provide a valid email.', 'reg')
        # password: minimum 8 characters, submitted, NOT "password"
        if len(request.form['reg_password']) < 8:
            flash('Password must include no fewer than eight characters.', 'reg')
        if request.form['reg_password'].upper == 'PASSWORD':
            flash('Never, ever, ever, ever use "password" as your password.', 'reg')
        # password confirmation: matches password
        if not request.form['reg_confirm'] == request.form['reg_password']:
            flash('Password confirmation does not match password.', 'reg')
        # if valid: hashes+salts password using bcrypt
        if not '_flashes' in session:
            query = ("INSERT INTO users (first_name, last_name, email, " +
                     "password, created_at, updated_at) VALUES " +
                     "(:first_name, :last_name, :email, :password, NOW(), NOW())")
            # print query
            data = {
                'first_name': request.form['reg_first_name'],
                'last_name': request.form['reg_last_name'],
                'email': request.form['reg_email'],
                'password': bcrypt.generate_password_hash(request.form['reg_password'])
                }
            # print data
            session['user_id'] = mysql.query_db(query, data)
            # print session['user_id']
            session['user_first_name'] = request.form['reg_first_name']
            return redirect('/wall')
        # if logging in:
    elif 'log_submit' in request.form:
        # print request.form
        query = ('SELECT * FROM users WHERE users.email = ' +
                 ':log_email LIMIT 1')
        data = {
            'log_email' : request.form['log_email'],
        }
        grab_hash = mysql.query_db(query, data)
        if bcrypt.check_password_hash(grab_hash[0]['password'],
                                      request.form['log_password']):
            session['user_id'] = grab_hash[0]['id']
            # print session['user_id']
            session['user_first_name'] = grab_hash[0]['first_name']
            return redirect('/wall')
        else:
            flash('Invalid login attempt.', 'log')
    return redirect('/')

@app.route('/wall')
def wall():
    # print 'you know nothing john snow'
    # grab messages
    query = (
        'SELECT * FROM messages JOIN users ON messages.user_id = ' +
        'users.id ORDER BY messages.created_at DESC'
    )
    all_messages = mysql.query_db(query)
    # print all_messages
    # 1800 seconds in a half hour
    # for each in all_messages:
    #     time_since_creation = (
    #         time.mktime(datetime.strptime(datetime.utcnow(),
    #                                       "%d/%m/%Y %H:%M:%S").timetuple())
    #     )
    #     print each['created_at']
    #     print datetime.utcnow()
    #     # print time_since_creation.total_seconds()
    #     if time_since_creation < 1800:
    #         deletable = True
    #     else:
    #         deletable = False
        # print deletable (add deletable=deletable once you figure out time logic)
    return render_template(
        'wall.html', all_messages=all_messages
        )

@app.route('/logoff')
def logoff():
    session.clear()
    return render_template('loggedoff.html')

@app.route('/post_message', methods=['POST'])
def post_messsage():
    # post this message for this user's wall
    print "It's a nice day for a white wedding"
    query = (
        'INSERT INTO messages (user_id, message, created_at, updated_at)' +
        'VALUES (:user_id, :message, :message_time, :message_time)'
    )
    data = {
        'user_id': session['user_id'],
        'message': request.form['message_box'],
        'message_time': datetime.datetime.utcnow()
    }
    mysql.query_db(query, data)
    return redirect('/wall')

@app.route('/post_comment')
def post_comment():
    # post this comment on this message
    return redirect('/wall')

app.run(debug=True)