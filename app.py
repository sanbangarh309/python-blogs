from flask import Flask, render_template, json, request, session, redirect, jsonify
from flaskext.mysql import MySQL
from flask_socketio import SocketIO
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, \
     check_password_hash

mysql = MySQL()
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
socketio = SocketIO(app)
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin'
app.config['MYSQL_DATABASE_DB'] = 'sandeep'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()
# ******************

@app.route("/")
def main():
    return render_template('index.html',page = 'Home')

@app.route("/about")
def about():
    return render_template('about.html',page = 'About')

@app.route("/portfolio")
def portfolio():
    return render_template('portfolio.html',page = 'Portfolio')

@app.route("/portfolio-detail")
def portfolio_detail():
    return render_template('portfolio-details.html',page = 'Portfolio Detail')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

# admin section
@app.route("/admin/", methods=["GET"])
def admin():
    if 'userid' in session:
        return render_template('/admin/dashboard.html',page = 'dashboard')
    return redirect("/admin/login/", code = '302')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@app.route('/admin/chat/')
def chat():
    return render_template('admin/chat.html')

@app.route("/admin/login/", methods = ['GET', 'POST'])
def login():
    # session['secret_key'] = 'sandeep@bangarh'
    if request.method == 'POST':
        result = request.form
        # print(result)
        # return jsonify(result['email'])
        conn = mysql.connect()
        cursor = conn.cursor()
        results = []
        query = "SELECT * from users WHERE email = %s"
        param = (result['email'])
        cursor.execute(query,param)
        columns = [desc[0] for desc in cursor.description]
        print(columns);
        for row in cursor:
            fin_row = dict(zip(columns, row))
            if check_password_hash(fin_row['password'],result['password']):
                session['userid'] = fin_row['id']
                session['name'] = fin_row['name']
                session['email'] = fin_row['email']
                print('logged in')
                return redirect("/admin/", code = '302')
            else:
                print('wrong email or password')
                return redirect("/admin/login/", code = '302')

    else:
        return render_template('/admin/login.html',page = 'login')

# print(generate_password_hash('bangarh309@#'))

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _name = request.form['inputName']
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        # validate the received values
        if _name and _email and _password:

            # All Good, let's call MySQL

            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close()
conn.close()

if __name__ == "__main__":
    app.run(threaded=True)
