from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin, logout_user

import folium
from folium import plugins

import os
import json
import sqlite3
import secrets


def create_table():
    # Connect to the SQLite database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create the "users" table with the "fullname" column
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    # Commit the changes and close the database connection
    conn.commit()
    conn.close()
create_table()


app = Flask(__name__, static_folder='static')

# Generate a random 24-character secret key
secret_key = secrets.token_hex(24)
app.secret_key = secret_key  # Change this to a random secret key
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User class for login management
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)



class navigator:
    def __init__(self):
        self.geoResources = {}
        self.hospitalLocation =(19.01662689782006, 73.10362338086016)
        self.position = 'Eng'
        self.destination = 'Place1'

        for root, dirs, files in os.walk('GeoResources'):
            for file in files:
                self.geoResources[file.split('.')[0]] = root+'/'+file

    def changeStartPoint(self, newStartPoint):
        self.position = newStartPoint
        print(f'Selected Start: {self.position}; Selected Target: {self.destination}')
        self.redrawMap()

    def changeDestination(self,newDestination):
        self.destination = newDestination
        self.redrawMap()


    def drawStartBuilding(self,hospitalMap):

      if self.position == 'Canteen':
        self.position = 'Place1'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Canteen'

      if self.position == 'Ground':
        self.position = 'Place2'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Ground'

      if self.position == 'Civil':
        self.position = 'Place3'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Civil'

      if self.position == 'Dental':
        self.position = 'Place4'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Dental'

      if self.position == 'Hospital':
        self.position = 'Place5'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Hospital'

      if self.position == 'Medical':
        self.position = 'Place6'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Medical'

      if self.position == 'Parking':
        self.position = 'Place7'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Parking'

      if self.position == 'Poshan':
        self.position = 'Place8'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Poshan'

      if self.position == 'Pros':
        self.position = 'Place9'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Pros'

      if self.position == 'Quarter':
        self.position = 'Place10'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Quarter'

      if self.position == 'Eng':
        self.position = 'Place11'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Eng'

      if self.position == 'Gate':
        self.position = 'Place12'
        hauseOutline = self.geoResources[self.position]
        folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)
        self.position = 'Gate'


    def drawPathWay(self,hospitalMap):

      def switchPosition(coordinate):
        temp = coordinate[0]
        coordinate[0] = coordinate[1]
        coordinate[1] = temp
        return coordinate

      searchString = self.position + self.destination.split('Place')[1]
      with open(self.geoResources[searchString]) as f:
           testWay = json.load(f)

      for feature in testWay['features']:
        path = feature['geometry']['coordinates']

      finalPath = list(map(switchPosition,path))
      folium.plugins.AntPath(finalPath).add_to(hospitalMap)

    def drawBuilding(self,hospitalMap):
      hauseOutline = self.geoResources[self.destination]
      folium.GeoJson(hauseOutline, name="geojson").add_to(hospitalMap)



    def redrawMap(self):
        print(f'position {self.position}, destination {self.destination}')
        hospitalMap = folium.Map(location = self.hospitalLocation, width = "100%", zoom_start = 17)
        self.drawStartBuilding(hospitalMap)
        self.drawPathWay(hospitalMap)
        self.drawBuilding(hospitalMap)
        return hospitalMap._repr_html_()
        #display(hospitalMap)

myNavigator = navigator()

@app.route('/')
@login_required
def index():
    return render_template("index.html")


def username_or_email_exists(username, email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
    user = cursor.fetchone()

    conn.close()

    return user is not None

def create_user(fullname, username, email, hashed_password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO users (fullname, username, email, password) VALUES (?, ?, ?, ?)',
                   (fullname, username, email, hashed_password))
    conn.commit()

    conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password using Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Check if the username or email is already in use
        if username_or_email_exists(username, email):
            flash('Registration failed. Username or email is already in use.', 'danger')
            return redirect(url_for('register'))

        # Insert the new user into the database
        create_user(fullname, username, email, hashed_password)

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    conn.close()
    if user:
      user_dict = {
            'id': user[0],
            'fullname': user[1],
            'username': user[2],
            'email': user[3],
            'password': user[4]
      }
      return user_dict
    else:
      return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Retrieve the user's hashed password from the database
        user = get_user(username)

        if user and bcrypt.check_password_hash(user['password'], password):
            # Passwords match, set a session to indicate the user is logged in
            session['user_id'] = user['id']
            session['fullname'] = user['fullname']

            # Log in the user using Flask-Login
            login_user(User(user['id'])) 

            flash('Login successful.', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Passwords do not match, indicate login failure
            flash('Login failed. Check your credentials.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Check if the user is logged in
    if current_user.is_authenticated:
        # Get the user's full name from the session
        fullname = session.get('fullname', '') 

        return render_template('dashboard.html', fullname=fullname)

    return redirect(url_for('login'))

# Define a route to log out the user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/map', methods=['POST'])
def show_map():
    selected_start = request.form['start']
    selected_target = request.form['target']

    if selected_start =='Gate' and selected_target =='Place12':
        message = "You are already at the Gate !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Eng' and selected_target =='Place11':
        message = "You are already in the Engineering Building !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Canteen' and selected_target =='Place1':
        message = "You are already at the Canteen !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Ground' and selected_target =='Place2':
        message = "You are already at the Ground !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Civil' and selected_target =='Place3':
        message = "You are already in Civil Building !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Dental' and selected_target =='Place4':
        message = "You are already in Dental Building !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Hospital' and selected_target =='Place5':
        message = "You are already in Hospital !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Medical' and selected_target =='Place6':
        message = "You are already in Medical Building !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Parking' and selected_target =='Place7':
        message = "You are already at the Parking Area !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Quarter' and selected_target =='Place10':
        message = "You are already at the Staff Quarter Area !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Poshan' and selected_target =='Place8':
        message = "You are already at the Poshan Area !!!"
        return render_template("map.html", message=message)
    elif selected_start =='Pros' and selected_target =='Place9':
        message = "You are already at the Prosthetics And Orthotics Building !!!"
        return render_template("map.html", message=message)
    else:
        myNavigator.changeStartPoint(selected_start)
        myNavigator.changeDestination(selected_target)
        hospitalMap = myNavigator.redrawMap()
        message = None
        return render_template("map.html", map=hospitalMap, message=message)
 

if __name__ == '__main__':
    app.run(debug=True)

