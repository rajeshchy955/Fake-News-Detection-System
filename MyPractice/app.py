from flask import Flask, request, render_template, flash, session, redirect, url_for
from flask_login import current_user, LoginManager
from flask_sqlalchemy import SQLAlchemy
import pickle
from flask import jsonify
from nltk.stem import WordNetLemmatizer
import re
from nltk.corpus import stopwords
from PreprocessingPipeline import Preprocessing
from title import titles


vector = pickle.load(open("vectorizer.pkl", 'rb'))
model = pickle.load(open("finalized_model.pkl", 'rb'))

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

# Login authentication
app.secret_key = "Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/fakenews'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Define the path for image uploads
UPLOAD_FOLDER = 'static/Images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

# user loader for session
@login_manager.user_loader
def load_user(user_id):
    # Load and return the user object from the database based on user_id
    return User.query.get(int(user_id))

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10))
    phone_num = db.Column(db.String(200))  # Provide a default value
    profile = db.Column(db.String(100))

    def __init__(self, username, email, password ,role,phone_num,profile):
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.phone_num=phone_num
        self.profile=profile

# Define the Admin model
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10))
    phone_num = db.Column(db.String(200))  # Corrected column type
    profile = db.Column(db.String(100))

    def __init__(self, username, email, password, role, phone_num, profile):
        self.username = username
        self.email = email
        self.password = password
        self.role = role
        self.phone_num = phone_num
        self.profile = profile


# Define the News model
class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    text = db.Column(db.String(100))
    category = db.Column(db.String(100))
    date = db.Column(db.Date)
    image_path = db.Column(db.String(100))
    label = db.Column(db.Boolean)

    def __init__ (self, title, text, category, date, image_path, label):
        self.title = title
        self.text = text
        self.category = category
        self.date = date
        self.image_path = image_path
        self.label = label

# default route
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    
    # Check if username or email already exists
    existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

    # Check if username or email already exists
    existing_admin = Admin.query.filter((Admin.username == username) | (Admin.email == email)).first()
    
    if existing_user or existing_admin:
        return render_template('login.html', error='user_exists')

    
    new_user = User(username=username, password=password, email=email, role='user',phone_num=0,profile='profile.webp')
    db.session.add(new_user)
    db.session.commit()
    
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login(): 
    username = request.form['username']
    password = request.form['password']
    
    # Check if the user exists in the admin table
    admin = Admin.query.filter_by(username=username, password=password, role='admin').first()

    # Check if the user exists in the user table
    user = User.query.filter_by(username=username, password=password, role='user').first()

    if user:
        # Store the username in the session
        session['user_id'] = user.id
        
        # Fetch data from the 'news' table
        news_data = News.query.all()
        return render_template("index.html", news=news_data)  # Redirect to index.html for users
    elif admin:
        # Store the username in the session
        session['user_id'] = admin.id
        
        # Fetch data from the 'news' table
        news_data = News.query.all()
        # Render the template 'Admin.html' and pass the news data to it
        return render_template('Admin.html', news=news_data)
    else:
        return render_template('login.html', error='password')  # Redirect back to login page with an error parameter

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        Category = request.form['Category']
        date = request.form['date']
        img = request.form['img']
        # Convert 'label' string to boolean
        label = request.form['label'].lower() == 'true'

        # Check if the news already exists in the database
        existing_news = News.query.filter_by(title=title).first()

        if existing_news:
            flash("News with this title already exists. Please choose a different title.")
        else:
            my_data = News(title, text, Category, date, img, label)
            db.session.add(my_data)
            db.session.commit()
            flash("News inserted successfully.")

    # Fetch data from the 'news' table after inserting news
    news_data = News.query.all()
    # Render the template 'Admin.html' and pass the news data to it
    return render_template("Admin.html", news=news_data)

#update the content
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        news_id = request.form['id']
        my_data = db.session.get(News, news_id)

        if my_data:
            my_data.title = request.form['title']
            my_data.text = request.form['text']
            my_data.category = request.form['category']
            my_data.date = request.form['date']
            my_data.image_path = request.form['image_path']
            # Convert 'label' string to boolean
            my_data.label = request.form['label'].lower() == 'true'

            db.session.commit()
            flash("News Updated Successfully.")
        else:
            flash("News with ID {} not found.".format(news_id))

        # Fetch data from the 'news' table
        news_data = News.query.all()
        return render_template('Admin.html',news=news_data)  

#delete method 
@app.route('/delete/<id>', methods=['POST','GET'])
def delete(id):
    my_data=News.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash ("News Deleted Successfully.")

    # Fetch data from the 'news' table
    news_data = News.query.all()
    return render_template('Admin.html',news=news_data)  


#home page redirect
@app.route('/home')
def home():
    # Fetch data from the 'news' table
    news_data = News.query.all()
    return render_template("index.html",news=news_data)  # Redirect to index.html for users

#contact us redirect
@app.route('/contactUs')
def contactUs():
    return render_template("contactUs.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/logout')
def logout():
    return render_template("login.html")

@app.route('/Admin')
def admin():
     # Fetch data from the 'news' table
    news_data = News.query.all()
    return render_template('Admin.html',news=news_data)  

#my profile for admin
@app.route('/adminProfile', methods=['GET', 'POST'])
def adminprofile():
    message = None  # Initialize message variable
    
    if request.method == 'POST':
        admin_id = request.form['id']
        my_data = db.session.get(Admin, admin_id)
    
        if my_data:
            my_data.username = request.form['username']
            my_data.email = request.form['email']
            my_data.password = request.form['password']
            my_data.phone_num = request.form['phone_num']
            my_data.profile = request.form['profile']

            db.session.commit()
            message = "Profile Information Updated Successfully."  # Assign message after successful update
        else:
            message = "Admin with id {} not found.".format(admin_id)  # Assign message if admin not found
        
    # Fetch admin data from the database
    admin_data = Admin.query.all()
    return render_template('adminProfile.html', admin_data=admin_data, message=message)

#my profile for user
@app.route('/userProfile', methods=['GET', 'POST'])
def userprofile():
    message = None  # Initialize message variable
    
    # Check if the user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if user:
            if request.method == 'POST':
                # Check if the session user_id matches the user's ID
                if user_id == user.id:
                    user.username = request.form['username']
                    user.email = request.form['email']
                    user.password = request.form['password']
                    user.phone_num = request.form['phone_num']
                    user.profile = request.form['profile']

                    db.session.commit()
                    message = "Profile Information Updated Successfully."  # Assign message after successful update
                else:
                    message = "You are not authorized to update this profile."
                
            return render_template('userProfile.html', user_data=[user], message=message)
        else:
            message = "User with id {} not found.".format(user_id)
    else:
        return render_template("index.html")  # Redirect to the login page if the user is not logged in



@app.route('/modelDash')
def modelDash():
    return render_template("modelDash.html")

@app.route('/detection', methods=['GET', 'POST'])
def detection():
    prediction_text = None

    if request.method == "POST":
        news = str(request.form['news'])
        processed_news = Preprocessing(news).text_preprocessing_user()

        # Save the processed news title to a file
        with open('news_title.txt', 'w', encoding='utf-8') as file:
            file.write(news)

        # Check if the news title is in the titles list
        flag = 0
        for item in titles:
            if processed_news == item:
                flag = 1
                break

        if flag == 0:
            prediction_text = "News headline is -> Unverified"
        else:
            # Transform the processed news using the vectorizer
            transformed_vector = vector.transform([processed_news])
            
            # Save the transformed vector to a text file
            with open("transformed_vector.txt", "w") as file:
                # Write the vector values as comma-separated values
                for value in transformed_vector.toarray()[0]:
                    file.write(str(value) + ",")
            
            # Use the transformed vector for prediction
            predict = model.predict(transformed_vector)[0]
            prediction_text = "News headline is -> {}".format(predict)

    show_more_detail = prediction_text is not None

    return render_template("detection.html", prediction_text=prediction_text, show_more_detail=show_more_detail)

@app.route('/info')
def info():
    # Read news title from file
    with open('news_title.txt', 'r') as file:
        news = file.read().strip()  # Read and strip any leading/trailing whitespace

    # Read vectorization data from file and parse into a list
    with open('transformed_vector.txt', 'r') as file:
        vectorization = file.read().strip().split(',')  # Read, strip, and split into a list
    
    # Ensure news is a single string
    if isinstance(news, list):
        news = ' '.join(news)

    lm = WordNetLemmatizer()
    stopwords_set = set(stopwords.words('english'))

    regularExp = re.sub(r'[^a-zA-Z0-9\s\.\,\:\-]', '', news)
    lowerCase = regularExp.lower()
    tekenization = lowerCase.split()
    stopwordsRem = [lm.lemmatize(x) for x in tekenization if x not in stopwords_set]
    review = " ".join(stopwordsRem)
    
    preprocess_data = [review]  # Store preprocessed data as a list

    return jsonify({
        'title': news,  # Include the title in the JSON response
        'regularExp': regularExp,
        'lowerCase': lowerCase,
        'tekenization': tekenization,
        'stopwordsRem': stopwordsRem,
        'preprocess_data': preprocess_data,
        'vectorization': vectorization
    })


if __name__ == '__main__':
    app.run(debug=True)
