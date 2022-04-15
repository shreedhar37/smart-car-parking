
from argparse import ArgumentError
from pydoc import render_doc
from tkinter import E
from wsgiref.util import request_uri

# from firebase_admin import credentials
# from firebase_admin import auth
from flask import Flask, render_template, redirect, request, request_tearing_down, session, url_for
import re
from idna import valid_label_length
import pyrebase
from requests import Session



try:
    app = Flask(__name__, template_folder='templates')
    app.secret_key = "your secret key"

    firebaseConfig = {
   
    }

    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()

    @app.route("/")

    def index():
        return render_template('index.html')

    @app.route("/register", methods = ["GET", "POST"])
    def register():
        try:
            msg = ''
        
            if request.method == "POST" and 'email' in request.form and 'password' in request.form:
                email = request.form['email']
                password = request.form['password']
                cpassword = request.form['cpassword']
                
                if len(password) < 8 and len(cpassword) < 8:
                    return render_template('register.html', msg = 'Please type 8 characters long password!!')
                
                elif cpassword != password:
                    return render_template('register.html', msg = "Confirm password doesn't match with password!!")

                elif not session['uid']:    
                    auth.create_user_with_email_and_password(email = email, password= password)

                    return render_template('login.html', msg = 'Account created successfully!!!')

            
            
            if request.method == "GET" :
                print("inside normal request")
                return render_template('register.html', msg = msg)

       
       
        except Exception as e:


            print(e)           

            return render_template('register.html', msg = 'Email Already exists!!!')
            
    @app.route("/login", methods = ["GET", "POST"])
    def login():

        try:
            msg = ''
            
            if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
                email = request.form['email']
                password = request.form['password']
                
                user = auth.sign_in_with_email_and_password(email, password)
                
                
                if user:
                    session['uid'] = user

                    return render_template('index.html', msg = 'Logged in successfully')
                
                else:
                    return render_template('login.html', msg = 'Invalid email or password')
            
            if not session['uid'] and request.method == "GET" :
                print("inside normal request")
                
                return render_template('login.html')
            


        except Exception as e:
            print(e)
            return render_template("login.html", msg = "Invalid email or password!!")

    @app.route("/book_slot")
    def book_slot():
        try:
            
            if session.get('uid'):

                return render_template('book_slot.html')

            else:
                return render_template("login.html")

        
        except Exception as e:
            print(e)
            return render_template('index.html', msg = e)

    @app.route('/logout')
    def logout():
        print("inside log out")
        session.pop('uid', None)
        return render_template('login.html', msg = 'Logged out successfully!!')

except Exception as e:
    print(e)


if __name__ == "__main__":
    app.run(debug=True)
    