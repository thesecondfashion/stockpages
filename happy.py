from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)


class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'


users = []
users.append(User(id=1, username='Anthony', password='password'))
users.append(User(id=2, username='Becca', password='secret'))
users.append(User(id=3, username='Carlos', password='somethingsimple'))

app = Flask(__name__,template_folder='template')
app.secret_key = 'somesecretkeythatonlyishouldknow'


@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user_list = [x for x in users if x.id == session['user_id']]
        if user_list:
            g.user = user_list[0]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user_list = [x for x in users if x.username == username]
        if user_list:
            user = user_list[0]
            if user.password == password:
                session['user_id'] = user.id
                return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/profile')
def profile():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        user_id = len(users) + 1
        new_user = User(id=user_id, username=username, password=password)
        users.append(new_user)

            # Redirect to login page
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/home')
def home():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('home.html')
