# Importing all needed libraries.
from flask import Flask, request, jsonify, render_template, Blueprint, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from loona import LoonaMetaClass

# Creating the FSM using the LOONA language.
TransactionFSM = LoonaMetaClass('transaction.txt', (object, ), {})

# Creating and configuring the flask app
app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
auth = Blueprint('auth', __name__)

# Creating and configuring the Data Base manager.
migrate=Migrate(app,db)
manager = Manager(app)
manager.add_command('db',MigrateCommand)

# Defining the User Mode.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    money = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return str(self.id)

# Defining the Transfer model.
class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.Integer, nullable=False)
    to_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return str(self.id)

''' --------------------------------------- Defining the routes ------------------------------------ '''
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET'])
def login():
    print("Login")
    return render_template('login.html')


@app.route('/register', methods=['GET'])
def signup():
    print("Signup in get")
    return render_template('register.html')

@app.route('/transaction/<id>', methods=['GET', 'POST'])
def transaction(id):
    if request.method == "GET":
        # If the request is a GET one, then we just return the front-end of the page.
        return render_template('transaction.html', id=id)
    else:
        # If the request is a POST one then we are processing the transaction.
        from_id = id
        amount = request.form.get('amount')
        to_id = request.form.get('user')

        # Getting the users involved in the transaction.
        from_user = User.query.get(from_id)
        to_user = User.query.get(to_id)

        # Sending the transaction data to the FSM
        fsm = TransactionFSM()
        _ = fsm.run({'from_amount' : float(from_user.money), 'amount_transfered' : float(amount)})
        final_state = fsm.run({'from_amount' : float(from_user.money), 'amount_transfered' : float(amount)})
        if final_state == 'Completed':
            # If the transaction passed then the transaction is added to Transfer table and the money are transfered
            # from one user to another one.
            new_transfer = Transfer(from_id=from_id, to_id=to_id, amount=amount, state=final_state)
            db.session.add(new_transfer)

            db.session.query(User).filter_by(id=from_id).update({'money': from_user.money - int(amount)})
            db.session.query(User).filter_by(id=to_id).update({'money': to_user.money + int(amount)})
        else:
            # If the transaction doesn't passed then the money are not transfered from one user to another.
            # But the transaction is added to the table.
            new_transfer = Transfer(from_id=from_id, to_id=to_id, amount=amount, state=final_state)
            db.session.add(new_transfer)

        db.session.commit()

        return redirect(url_for('profile', id=id))

@app.route('/profile/<id>', methods=['GET'])
def profile(id):
    user = User.query.filter_by(id=id).first()
    transfers = Transfer.query.filter((Transfer.from_id == id) | (Transfer.to_id == id))
    return render_template('profile.html', email = user.email, money = user.money, id=str(user.id), transfers=transfers)

@app.route('/signup', methods=['POST'])
def signup_post():
    print('fuck1')
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, password=password, money=1000)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    id = User.query.filter_by(email=email).first().id
    return redirect(url_for('profile', id=id))

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user and password == user.password:
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.profile'))

db = SQLAlchemy(app)
db.create_all()

# Running the app.
manager.run()
if __name__ == '__main__':
    app.run()