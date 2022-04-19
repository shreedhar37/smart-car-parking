import datetime
from flask import Flask, render_template, redirect, request, request_tearing_down, session, url_for
import re
from idna import valid_label_length
import pyrebase
from requests import Session
import re
import time


try:
    app = Flask(__name__, template_folder='templates')
    app.secret_key = "your secret key"

    firebaseConfig = {
  
  }


    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()
    
    
    
    
    status = ""
    @app.route("/")

    def index():
        global status   
        status = db.child("sensor_value").get().val()
        status = "green" if status == "0" else "red"
        print(status)
        
        return render_template('index.html', status = status)

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

                else:    
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
            global status
            msg = ''
            
            if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
                email = request.form['email']
                password = request.form['password']
                
                user = auth.sign_in_with_email_and_password(email, password)
                
                
                if user:
                    session['uid'] = user['email'][:-10]
                   
                    return render_template('index.html', msg = 'Logged in successfully', status = status)
                
                else:
                    return render_template('login.html', msg = 'Invalid email or password')
            
            if  request.method == "GET" :
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
            return render_template('index.html', msg = e, status = status)

    @app.route('/logout')
    def logout():
        print("inside log out")
        session.pop('uid', None)
        return render_template('login.html', msg = 'Logged out successfully!!')

    @app.route('/bookings', methods = ["GET", "POST"])
    def bookings():
        try:
            if session['uid'] and request.method == "POST" and 'vno' in request.form and 'time' in request.form: 
                dt = str(datetime.datetime.now())[:11]
                vehicle_no  = request.form['vno']
                duration = request.form['time']
                
                
                bookings = db.child("bookings").child(session['uid']).get()    
                data = { ("date") : dt, ("vehicle_no" ) : vehicle_no, ("duration") : duration}
                db.child("bookings").child(session['uid']).push(data)
                bookings = db.child("bookings").child(session['uid']).get()    
                global status
                status = "red"
                return redirect(url_for('my_bookings'))
            
           
        except Exception as e:
            print(e)
            return render_template("book_slot.html", msg = e)  

    @app.route('/my_bookings.html')
    def my_bookings():
            
        try:
            if session['uid']:

                bookings = db.child("bookings").child(session['uid']).get()
                if bookings.val():
                    my_bookings = dict()
                    for booking in bookings.each():
                        my_bookings[booking.key()] = {'vehicle_no': booking.val()['vehicle_no'], 
                                                'duration': booking.val()['duration'], 
                                                'date': booking.val()['date']
                                                }
                    
                    return render_template("my_bookings.html", my_bookings = my_bookings)
                else:
                    return render_template("my_bookings.html", msg = "You haven't made any booking !! ")

            else:
                return render_template("login.html", msg = "Please login first!!!")
            
        except Exception as e:
            print(e)
            return render_template("my_bookings.html", msg = e)

except Exception as e:
    print(e)


if __name__ == "__main__":
    app.run(port = 5000, debug=True)
    