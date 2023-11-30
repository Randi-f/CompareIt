import math
from flask import Flask, render_template, request
import psycopg2 as db
import uuid

# from flask_mail import Mail, Message
# from itsdangerous import URLSafeTimedSerializer

# app.config['MAIL_SERVER'] = 'your_smtp_server'  
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'your_email@example.com'
# app.config['MAIL_PASSWORD'] = 'your_email_password'

# mail = Mail(app)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = str(uuid.uuid4())
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        full_name = first_name + ' ' + last_name
        gender = request.form['gender']
        email = request.form['email']
        dob = request.form['dob']
        postcode = request.form['postcode']
        password = request.form['password']

        sqlcommand = '''
            INSERT INTO my_user (user_id, name, gender, email, dob, postcode, password) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''

        values = (user_id, full_name, gender, email, dob, postcode, password)

        server_params = {
            'dbname': 'kac23',
            'host': 'db.doc.ic.ac.uk',
            'port': '5432',
            'user': 'kac23',
            'password': '3E13Nt3,SX'
        }

        try:
            conn = db.connect(**server_params)
            curs = conn.cursor()
            curs.execute(sqlcommand, values)
            conn.commit()  # Commit to save changes
            message = "Registration successful"
        except Exception as e:
            print(f"An error occurred: {e}")  # Log the error
            message = "Registration failed due to a technical issue."
        finally:
            if 'curs' in locals():
                curs.close()
            if 'conn' in locals():
                conn.close()
        # serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        # token = serializer.dumps(email, salt='email-confirmation')

        # # Construct the verification URL
        # confirm_url = url_for('confirm_email', token=token, _external=True)

        # # Construct and send the email
        # msg = Message("Confirm your email", sender='your_email@example.com', recipients=[email])
        # msg.body = 'Please click on the link to confirm your email: ' + confirm_url
        # mail.send(msg)

        return render_template("registration_result.html", message="Please check your email to confirm your registration")
    else:
        return render_template("register.html")

# @app.route('/confirm_email/<token>')
# def confirm_email(token):
#     try:
#         serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#         email = serializer.loads(token, salt='email-confirmation', max_age=3600)
#     except:
#         return 'The confirmation link is invalid or has expired.'

#     # Database connection parameters
#     server_params = {
#         'dbname': 'kac23',
#         'host': 'db.doc.ic.ac.uk',
#         'port': '5432',
#         'user': 'kac23',
#         'password': '3E13Nt3,SX'
#     }

#     try:
#         conn = db.connect(**server_params)
#         curs = conn.cursor()

#         # Update the user's email_verified status
#         sqlcommand = "UPDATE my_user SET email_verified = TRUE WHERE email = %s"
#         curs.execute(sqlcommand, (email,))
#         conn.commit()

#         message = "Your email has been confirmed!"

#     except Exception as e:
#         print(f"An error occurred: {e}")  # Log the error
#         message = "Failed to confirm email due to a technical issue."

#     finally:
#         if 'curs' in locals():
#             curs.close()
#         if 'conn' in locals():
#             conn.close()

#     return render_template("email_confirmation_result.html", message=message)
