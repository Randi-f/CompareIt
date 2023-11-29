This is the user profile webpage.
The basic function of it is read the information in the database, and print the data out on the screen.
The data types includes username, email address, gender, postcode, and bio.

The database to test this code was created by SQLAlchemy. Also, a very simple login page was created only for the testing.
If you would like to try this code, you can use SQLAlchemy to creat your own database locally.
The full steps of creating the database and testing the code is below.



First, run this code to install Flask-SQLAlchemy.
pip install Flask-SQLAlchemy


Then run the Flask shell by running the following command in your terminal.
flask shell


Once you are in the Flask shell you can add the data. Let's use the sample below (just type the code below into the terminal)
from app import db, User
# Add UserA
user_a = User(username='UserA', email='userA@example.com', gender='Male', postcode='SW7 2AZ', bio="A's bio")
db.session.add(user_a)
# Add UserB
user_b = User(username='UserB', email='userB@example.com', gender='Female', postcode='SW7 2AZ', bio="B's bio")
db.session.add(user_b)
# Add UserC
user_c = User(username='UserC', email='userC@example.com', gender='Female', postcode='SW7 2AZ', bio="C's bio")
db.session.add(user_c)
# Commit the changes to the database
db.session.commit()
exit()


Now you have a database with UserA, UserB and UserC. You can now run the code locally by type the code below
flask run

The you can see a URL. Copy and paste that URL into your browser and add "/login" at the end of the URL. 
Then press "Enter" and you will see a very simple login page (which is designed only for testing).
Now you can try enter the user name you added into your data base (let's try "UserA").
Then the browser should jump into the profile page and print out the information.


To modify the code so it is able to get the data from other database, change the code below 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
by changing the "sqlite:///site.db".
(you can find this line of code in the file called app.py)

If you would like to add more parameters (data types), you will need to modify app.py and profile.html.
