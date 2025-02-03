from flask import Flask, render_template, request, jsonify, session
from flask_login import current_user, login_required, login_user, logout_user, UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Things to set up first
app = Flask(__name__)
app.secret_key = "wash9eytwqh9uc&&%!^*!BYvx2be6298642*^#!*27358^(*59)"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # redirect to the login page if unauthorized

SPORTS = ['BasketBall', 'Soccer', 'Table Tennis', 'Hockey', 'Rugby', 'Chess', 'Swimming']
YEARS = ['Year 1', 'Year 2', 'Year 3', 'Year 4']


# DATABASE MODELS
class User(db.Model, UserMixin):
    """
    A user model representing registered users to access the specified databases.
    takes only a username and a password, the id(primary key) is generated by the system
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f'User {self.username}'

class Registrant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    year = db.Column(db.String(10), nullable=False)
    sport = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'{self.name} of {self.year}: {self.sport}'


# tells flask how to load a user from the database
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes for authentication
# LOGIN VIEWS
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        uname = request.form.get("username").strip().rstrip()
        passwd = request.form.get("password").rstrip().strip()
        confirm_password = request.form.get("confirm_password")

        # validation
        if len(uname) < 4 or len(uname) > 10:
            return jsonify({"status":"error", "message":"Username must be between 4 and 10 characters!!"}), 400
        if len(passwd) < 4 or len(passwd) > 20:
            return jsonify({"status":"error", "message":"Password must be between 4 and 20 characters!!"}), 400
        if passwd != confirm_password:
            return jsonify({"status":"error", "message":"Passwords donot match!!"})
        if User.query.filter_by(username=uname).first():
            return jsonify({"status":"error", "message":"Username already exists!!"}), 400
        # hash the password
        pass_hash: str = generate_password_hash(passwd)
        try:
            new_user = User(username=uname, password_hash=pass_hash)
        except Exception as e:
            print(e)

        # record into the database
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"status":"success", "message":"Registration successful"}), 200
        except Exception:
            db.session.rollback()
            return jsonify({"status":"error", "message":"There was an error during registration"}), 400
    return render_template('register.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        uname = request.form.get("username").rstrip().strip()
        passwd = request.form.get("password").strip().rstrip()

        user = User.query.filter_by(username=uname).first()
        if user and check_password_hash(user.password_hash, passwd):
            login_user(user=user)
            return jsonify({"status":"success", "message":"Login successful"}), 200
        return jsonify({"status":"error", "message":"Invalid credentials!"}), 400
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"status":"info", "message":"You have been logged out!!"}), 200


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route("/")
def home():
    return render_template("home.html")


# SPORTS REGISTRATION VIEWS
@app.route('/home')
def home_sport():
    return render_template('index.html', sports=SPORTS, years=YEARS)


@app.route("/register_sport", methods=["POST"])
@login_required
def register_sport():
    name = request.form.get("name")
    if not name:
        return jsonify({"status":"error", "message":"No name specified"})
    year = request.form.get('year')
    if not year:
        return jsonify({"status":"error", "message":"No year of study specified"})
    sport = request.form.get('sport')
    if not sport:
        return jsonify({"status":"error", "message":"No sport selected"})
    if sport not in SPORTS:
        return jsonify({"status":"error", "message": "Invalid sport selected"})

    n = Registrant.query.filter_by(name=name).first()
    if n:
        return jsonify({"status": "error", "message":"Name already exists!!"})

    # add registrant to the database
    to_be_registered = Registrant(name=name, year=year, sport=sport)

    # add session and commit to the database
    db.session.add(to_be_registered)
    db.session.commit()

    # confirm registration
    return jsonify({"status":"success", "message":"Registration successful"})


@app.route("/registrants")
@login_required
def registrant():
    records = Registrant.query.all()
    return render_template("registrants.html", registrants=records, username=current_user.username)


if __name__ == "__main__":
    app.run(debug=True)
