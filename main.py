from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    
    def __init__(self, title, body, owner):
        
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def get_user_blogs(username):
    # List of blogs by a specific user
    owner = User.query.filter_by(username=username).first()
    return Blog.query.filter_by(owner=owner)

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup', 'entry']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    user_id = request.args.get('id')
    users = User.query.all()
    usernames = request.args.get('username')
    return render_template('home.html', users=users)

@app.route('/user_blog', methods=['POST', 'GET'])
def user_blog():
    blog_post_value = request.args.get('id')
    userID = request.args.get('user')
    user = User.query.filter_by(username=userID).first()
    return render_template('user.html', blogs=get_user_blogs(userID))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


    

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
       
        
        # TODO - validate user's data

        username_error = ''
        password_error = ''
        verify_error = 'passwords need to match'
        email_error = ''
        existing_user = User.query.filter_by(username=username).first()
                
        if username == '' or password == '' or verify == '':
            flash("one or more fields are invalid", "error")
        
        if len(username) < 3 or len(username) > 20:
            username_error ="That's not a valid username"
            
        elif " " in username:
            username_error ="That's not a valid username"

        if len(password) < 3 or len(password) > 20:
            password_error ="That's not a valid password"
            
        elif " " in password:
            password_error ="That's not a valid password"

        if  verify == password:
            verify_error=""
        
        if existing_user == username:
            
            flash('that username already exists', 'error')
            return render_template("signup.html")
            
        if not username_error and not password_error and not verify_error:
        
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                    
                return redirect("/newpost")
            else:
                flash("that username is used already.", "error")
                
        else:
            return render_template("signup.html",
                username=username,
                username_error=username_error,
                password_error=password_error,
                verify_error=verify_error,)
                
    return render_template('signup.html')
                
                
@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blogs = Blog.query.all()
    user_id = request.args.get('id')
    return render_template('blog.html', blogs=blogs)

@app.route('/entry', methods=['POST', 'GET'])
def entry():
    
    user_id = request.args.get('id')
    blogs = Blog.query.filter_by(id=user_id)
    return render_template('entry.html', blogs=blogs)


@app.route('/newpost')
def display_newpost():
    
    return render_template("new-blog.html")


@app.route('/newpost', methods=['POST','GET'])
def newpost():
    title = request.form['title']
    body = request.form['body']
    title_error = ''
    body_error = ''
    owner = User.query.filter_by(username=session['username']).first()
    
    if len(title) <= 0:
        title_error = 'please enter a valid title'

    elif len(body)<= 0:
        body_error = 'please enter a valid body'
    
    if request.method == 'POST' and not title_error and not body_error:
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        return render_template('post.html',
        title=title,
        body=body)
    
    else:
        return render_template("new-blog.html",
        title=title,
        body=body,
        title_error=title_error,
        body_error=body_error
        )

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')  
    

    
    

    
    
    


if __name__ == '__main__':
    app.run()