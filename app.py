from random import randint
from flask import Flask, render_template, request, Response, redirect, send_file,session,url_for, jsonify
from flask_login import LoginManager,login_required,UserMixin, current_user,login_user,logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail,Message
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import holidays
import cv2
import numpy as np
import csv
import face_recognition
from deepface import DeepFace
from datetime import datetime, timedelta,date
import pyshine as ps
import timeit
import time
import threading
from playsound import playsound
import pandas as pd
import plotly
import plotly.express as px
import secrets
import json
from anti_spoofing.anti_spoofing import liveness_check  # import our new module

app = Flask(__name__)
# Load environment variables from .env
load_dotenv()

#configurations for database and mail
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))  # Convert to int
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'  # Convert to bool
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail_ = Mail(app)



@login_manager.user_loader
def load_user(user_id):
    return users.query.get(user_id)

#employee database 
class employee(db.Model,UserMixin):
    id = db.Column(db.String(20), primary_key=True, unique=True)
    name = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    hiringDate = db.Column(db.String(10), default=datetime.now().strftime("%d-%m-%Y"))

    def __repr__(self) -> str:
        return f"{self.id} - {self.name} - {self.department} - {self.email} - {self.hiringDate}"

#users/owner database
class users(db.Model,UserMixin):
    id = db.Column(db.String(20), primary_key=True,unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable = True) 
    mail = db.Column(db.String(80), nullable = True) 
    password = db.Column(db.String(200), nullable=False)
    dateCreated = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

path = 'static/TrainingImages'

@app.route('/')
def index():
    try:
        cap.release()
    except:
        pass
    try:
        cap2.release()
    except:
        pass
    return render_template('index.html')

# About Us Page Route
@app.route('/about')
def about():
    return render_template('about.html')

#user login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Find the user by username
        user = users.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            # Log the user in (using Flask-Login)
            login_user(user)
            return redirect('/')  # Redirect to the home page or dashboard
        else:
            return render_template('login.html', incorrect=True, msg='Invalid username or password')
        
    return render_template('login.html')

#user logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

# to mail employee for successful registration (already defined)
def send_mail(email, text, subject='No Subject', html=None):
    msg = Message(subject=subject, recipients=[email], sender='Face Recognition Attendance <{app.config["MAIL_USERNAME"]}>', body=text)
    if html:
        msg.html = html
    mail_.send(msg)


# New function to mail employee on attendance marking
def send_attendance_mail(email, name):
    # Email subject
    subject = "Attendance Marked Successfully"

    msg = f'''Hi {name},

Your attendance has been successfully recorded for today.
Thank you for being punctual.

Have a great day!
SmartAttend: Employee Facial Attendance System
'''
    send_mail(email, msg,subject)

#user registration
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        id = request.form['id']
        username = request.form['username']
        name = request.form['name']
        mail = request.form['mail']
        pass1 = request.form['pass']
        pass2 = request.form['pass2']

        #check if the owner id and username are unique or not.
        user = users.query.filter_by(username=username).first()
        user2 = users.query.filter_by(id = id).first()
        #if not unique or passwords do not match then back to sign up page with informative message, otherwise register the user
        if user is not None or user2 is not None:
            return render_template('signup.html', incorrect=True, msg = 'User with same ID or Username already exist')
        elif pass1 != pass2:
            return render_template('signup.html', incorrect = True, msg = "Passwords do not match")
        else:
             # Hash the password before storing it
            hashed_password = generate_password_hash(pass1, method='sha256')
            new_user = users(id = id,name = name, mail = mail,username=username, password=hashed_password)  #password=pass1
            db.session.add(new_user)
            db.session.commit()
            # Email subject
            # Email subject
            subject = "Owner Account Created Successfully"

            # Plain text fallback
            msg = f'''Hello {new_user.name}

            Your owner account has been successfully created.

            Thank You.
            SmartAttend: Employee Facial Attendance System
            '''

            # HTML version (inserted from previous answer, variable-ready)
            html_msg = f'''
            <div style="font-family:'Segoe UI', Roboto, sans-serif; max-width:600px; margin:0 auto; background-color:#0e0e2c; color:#e0e0ff; padding:30px; border-radius:12px; box-shadow:0 0 15px rgba(0,255,255,0.2);">
            <div style="text-align:center; border-bottom:1px solid #3a3a75; padding-bottom:20px;">
                <h1 style="font-size:26px; color:#00ffe0; margin:0;">SmartAttend: Employee Facial Attendance System</h1>
                <p style="color:#9ca3af; font-size:14px;">Welcome to the future of attendance systems</p>
            </div>

            <div style="margin-top:30px;">
                <h2 style="color:#00d8ff; font-size:22px;">🎉 Owner Registration Successful!</h2>
                <p style="line-height:1.6; font-size:16px;">
                Hello <strong>{new_user.name}</strong>,<br><br>
                Your owner account has been <span style="color:#22c55e;">successfully created</span> in our system.<br><br>
                <strong>Username:</strong> {new_user.username}<br>
                <strong>Registered Email:</strong> {new_user.mail}
                </p>
            </div>

            <div style="margin-top:30px; background-color:#1a1a3d; padding:20px; border-radius:8px; border-left:4px solid #00ffe0;">
                <h3 style="margin:0 0 10px 0; color:#93c5fd;">🔐 Security Reminder</h3>
                <ul style="padding-left:20px; color:#cbd5e1; font-size:14px;">
                <li>Keep your login credentials secure.</li>
                <li>Never share your password with anyone.</li>
                <li>Ensure your email <strong>facerecognition2003@gmail.com</strong> is active for alerts.</li>
                </ul>
            </div>

            <div style="text-align:center; margin-top:40px; font-size:13px; color:#94a3b8;">
                <p>This is an automated message from <strong>SmartAttend</strong>. Please do not reply.</p>
            </div>
            </div>
            '''

            # Send both text and HTML
            send_mail(new_user.mail, msg, subject, html=html_msg)

            return render_template('login.html', registered = True)

    return render_template('signup.html')

def sendResetMail(mail, otp):
    subject = '🔐 SmartAttend | Password Reset Request'

    html = f'''
        <div style="font-family: 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; padding: 50px 20px; color: #e2e8f0;">
            <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 16px; padding: 40px; box-shadow: 0 0 25px rgba(99,102,241,0.3);">
                
                <header style="text-align: center; margin-bottom: 30px;">
                    <h1 style="font-size: 28px; color: #60a5fa; font-weight: 700; letter-spacing: 1px;">SmartAttend: Employee Facial Attendance System</h1>
                    <p style="font-size: 14px; color: #94a3b8; margin-top: 4px;">Welcome to the future of attendance systems</p>
                </header>

                <main>
                    <h2 style="font-size: 22px; color: #cbd5e1; font-weight: 600; margin-bottom: 20px;">Password Reset Request</h2>
                    <p style="font-size: 15px; line-height: 1.7; color: #cbd5e1;">
                        Hey there, human.<br><br>
                        A password reset was initiated from your account in the SmartAttend neural core. 
                        Use the OTP below to verify your identity and restore access.
                    </p>

                    <div style="margin: 30px 0; text-align: center;">
                        <div style="display: inline-block; padding: 20px 40px; background-color: #1e40af; border-radius: 12px; font-size: 34px; font-family: monospace; font-weight: bold; color: #ffffff; letter-spacing: 10px; box-shadow: 0 0 15px #3b82f6;">
                            {otp:06}
                        </div>
                    </div>

                    <div style="background-color: #1e293b; padding: 20px; border-radius: 8px; border-left: 4px solid #f87171; margin-bottom: 30px;">
                        <h3 style="color: #fca5a5; font-size: 16px; margin: 0 0 10px;">⚠️ Security Alert</h3>
                        <ul style="padding-left: 20px; font-size: 14px; color: #f1f5f9;">
                            <li>This OTP is confidential – never share it</li>
                            <li>If this wasn’t you, no action is needed</li>
                            <li>Stay vigilant. Stay verified.</li>
                        </ul>
                    </div>
                </main>

                <footer style="text-align: center; border-top: 1px solid #334155; padding-top: 20px;">
                    <p style="font-size: 14px; color: #64748b;">Need support? Reach out:</p>
                    <p style="font-size: 14px; color: #60a5fa;">
                        📧 <a href="mailto:facerecognition2003@gmail.com" style="color: #93c5fd; text-decoration: none;">facerecognition2003@gmail.com</a><br>
                        📞 +91 (91) 529-0705<br>
                        🧭 Mon–Fri | 9:00 AM–6:00 PM IST
                    </p>
                    <p style="margin-top: 20px; font-size: 12px; color: #475569;">This message was generated by SmartAttend’s AI core. Do not reply directly.</p>
                </footer>
            </div>
        </div>
        '''

    msg = Message(
        subject=subject,
        recipients=[mail],
        sender='SmartAttend AI Core <facerecognition2003@gmail.com>',
    )
    
    # ✅ Attach HTML content to the message
    msg.html = html

    # ✅ Now send without any extra arguments
    mail_.send(msg)

#user password reset request
@app.route('/reset_request',methods = ['GET','POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form['mail']
        user = users.query.filter_by(mail = email).first()
        #if user with given mail id exists then generate an OTP and mail to the user
        if user:           
            otp = randint(000000,999999)
            sendResetMail(email,otp)
            session['id'] = user.id
            session['otp'] = otp
            return render_template('OTP.html')
        else:
            return render_template('resetRequest.html', incorrect = True)
    return render_template('resetRequest.html')

#function to mail password reset OTP






#to verigy OTP
@app.route('/verifyOTP', methods = ['GET','POST'])
def verifyOTP():
    #if sent OTP matches with user typed OTP then redirect to reset password page
    otp2 = int(request.form['otp'])
    if session['otp'] == otp2:
        return render_template('resetPassword.html')
    else:
        return render_template('OTP.html', incorrect = True)

#user password reset
@app.route('/resetPass',methods = ['GET','POST'])
def resetPass():
    pw1 = request.form['pass1']
    pw2 = request.form['pass2']
    #if both passwords matches and are of length atleast 8, then chnage the user password.
    if pw1 == pw2:
        user = users.query.filter_by(id = session['id']).first()
        #user.password = pw1
        user.password = generate_password_hash(pw1, method='sha256')
        db.session.commit()
        return render_template('login.html', reseted = True)
    else:
        return render_template('resetPassword.html',incorrect = True)

#add new employee in the employee database
@app.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    try:
        cap2.release()
    except:
        pass
    invalid =0
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        dept = request.form['dept']
        mail = request.form['mail']
        #in below code invalid = 0 for no problem, invalid = 1 for not a unique id, invalid=2 for not uploading photo
        #if account created the send mail to the employee otherwise rollback last submission
        try:
            invalid = 1
            emp = employee(id=id, name=name, department=dept, email=mail)
            db.session.add(emp)
            db.session.commit()
            fileNm = id + '.jpg'
            # Email subject
            subject = "Employee Registration Successful"
            
            # Plain text fallback
            msg = f'''Hi {name},

        Welcome to the organization.
        You have been successfully registered in the employee database.

        Thank You.
        SmartAttend: Employee Facial Attendance System
        '''

            # HTML content
            html = f'''
            <div style="font-family: 'Segoe UI', Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; padding: 30px; border-radius: 12px; max-width: 600px; margin: auto; box-shadow: 0 0 30px #1e293b;">
            <div style="text-align: center; border-bottom: 1px solid #334155; padding-bottom: 20px;">
                <h1 style="font-size: 26px; color: #60a5fa;">SmartAttend: Employee Facial Attendance System</h1>
                <p style="font-size: 14px; color: #94a3b8;">Welcome to the future of attendance systems</p>
            </div>

            <div style="padding: 30px 0;">
                <h2 style="color: #38bdf8; font-size: 22px; text-align: center;">Welcome, {name}!</h2>
                <p style="font-size: 16px; color: #cbd5e1; text-align: center;">
                You have been <strong style="color: #a3e635;">successfully registered</strong> in our employee database.
                </p>
                <div style="background-color: #1e293b; padding: 20px; border-radius: 8px; margin-top: 25px;">
                <p style="font-size: 15px; line-height: 1.6; color: #e0f2fe;">
                    📌 <strong>Department:</strong> {dept}<br>
                    🆔 <strong>Employee ID:</strong> {id}<br>
                    📧 <strong>Email:</strong> {mail}
                </p>
                </div>
            </div>

            <div style="margin-top: 30px; padding: 20px; background-color: #0ea5e9; border-radius: 8px; text-align: center;">
                <p style="margin: 0; font-size: 16px; font-weight: 600; color: #ffffff;">
                We’re excited to have you on board. Your facial data will be used to seamlessly mark attendance.
                </p>
            </div>

            <div style="text-align: center; font-size: 13px; color: #64748b; padding-top: 20px; border-top: 1px solid #334155; margin-top: 40px;">
                <p>This is an automated system email from SmartAttend. Do not reply.</p>
                <p>Contact: <a href="mailto:facerecognition2003@gmail.com" style="color: #60a5fa;">facerecognition2003@gmail.com</a></p>
            </div>
            </div>
            '''

            # Send the email with HTML content
            send_mail(mail, msg, subject, html)
            try:
                photo = request.files['photo']
                photo.save(os.path.join(path, fileNm))
            except:
                invalid = 2
                cv2.imwrite(os.path.join(path, fileNm), pic)
                del globals()['pic']
            invalid = 0
        except:
            db.session.rollback()
    allRows = employee.query.all()
    return render_template("insertPage.html", allRows=allRows, invalid = invalid)

#to delete an existing employee
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    #delete from database
    emp = employee.query.filter_by(id=id).first()
    db.session.delete(emp)
    db.session.commit()
    fn = id + ".jpg"
    #delete photo stored in training images
    try:
        os.unlink(os.path.join(path, fn))
    except:
        pass
    #marking status as terminated in attendance records for deleted employee
    df = pd.read_csv("static/records.csv")
    df.loc[df["Id"] == id, "Status"] = "Terminated"
    df.to_csv("static/records.csv", index=False)

    return redirect("/add")

#to update an existing employee
@app.route("/update", methods=['GET', 'POST'])
@login_required
def update():
    id = request.form['id']
    emp = employee.query.filter_by(id=id).first()
    #upate in database
    emp.name = request.form['name']
    emp.department = request.form['dept']
    emp.email = request.form['mail']
    db.session.commit()
    #update photo
    fileNm = id + '.jpg'
    try:
        try:
            photo = request.files['photo']
            photo.save(os.path.join(path, fileNm))
        except:
            cv2.imwrite(os.path.join(path, fileNm), pic)
            del globals()['pic']
    except:
        pass
    #update in attendance records
    df = pd.read_csv("static/records.csv")
    df.loc[(df["Id"] == id) & (df['Status'] == 'On Service'), ['Name','Department']] = [emp.name,emp.department]
    df.to_csv("static/records.csv", index=False)
    return redirect("/add")

#generating frames for capturing photo ny detecting smile
def gen_frames_takePhoto():
    start = timeit.default_timer()
    flag = False
    num = -1

    while True:
        ret, frame = cap2.read()  # read the camera feed
        if ret:
            if num == 0:
                #if the numbering for capturing phto has completed then release camera and save the image 
                global pic
                pic = frame
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                playsound("static/cameraSound.wav")
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n')
                cap2.release()
                break

            # resize and convert the frame to Gray
            frameS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
            frameS = cv2.cvtColor(frameS, cv2.COLOR_BGR2RGB)
            # finding list of face locations
            facesLoc = face_recognition.face_locations(frameS)
            #if more than 1 person is in frame then don't consider
            if len(facesLoc) > 1:
                cv2.putText(frame, "Only one person allowed", (100, 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                flag = False
                continue

            for faceLoc in facesLoc:  
                # analyze the frame and look for emotion attribute and save it in a result
                result = DeepFace.analyze(
                    frame, actions=['emotion'], enforce_detection=False)
                #face locations
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                #if the smotion is happy, start numbering and check same for 3 upcoming frames
                if result['dominant_emotion'] == 'neutral' and timeit.default_timer() - start > 5:

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    if flag:
                        cv2.putText(frame, str(num), (150, 200),cv2.FONT_HERSHEY_SIMPLEX, 6, (255, 255, 255), 20)
                        time.sleep(1)
                        num = num-1

                    else:
                        flag = True
                        num = 3
                else:
                    flag = False
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            #pass the frame to show on html page
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n'+frame+b'\r\n')

#passing generated frames to html page
@app.route('/takePhoto', methods=['GET', 'POST'])
def takePhoto():
    #start camera 
    global cap2
    cap2 = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    return Response(gen_frames_takePhoto(), mimetype='multipart/x-mixed-replace; boundary=frame')

# encodings of known faces
@app.route("/encode")
@login_required
def encode():
    images = []
    myList = os.listdir(path)

    global encodedList
    global imgNames

    # function for saving images name ie employees' ids in imgNames
    def findClassNames(myList):
        cNames = []
        for l in myList:
            curImg = cv2.imread(f'{path}/{l}')
            images.append(curImg)
            cNames.append(os.path.splitext(l)[0])
        return cNames

    # function for saving face encodings in encodedList
    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            try:
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            except:
                pass
        return encodeList

    imgNames = findClassNames(myList)
    encodedList = findEncodings(images)
    return render_template("recogPage.html")

# generating frames for recognizer
def gen_frames():
    oldIds = []
    recognition_start_time = None
    recognized_id = None

    # In your markEntry function (within gen_frames), update as below:
    def markEntry(id):
        with open('static/records.csv', 'r+') as f:
            myDataList = [line for line in f if datetime.now().strftime('%d-%m-%Y') in line]
            idList = [line.split(',')[0] for line in myDataList]
            if id not in idList:
                now = datetime.now()
                date = now.strftime("%d-%m-%Y")
                dtime = now.strftime('%H:%M:%S')
                emp = employee.query.filter_by(id=id).first()
                f.writelines(f'\n{id},{emp.name},{emp.department},{dtime},{date},{"On Service"}')
                print("Sending attendance mail to", emp.email)
                # Offload mail sending to a background thread
                threading.Thread(target=send_mail_in_context, args=(emp.email, emp.name), daemon=True).start()

    def send_mail_in_context(email, name):
        with app.app_context():
            send_attendance_mail(email, name)

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        # Resize and convert to RGB
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        cv2.putText(img, datetime.now().strftime("%D %H:%M:%S"), (10, 15), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        # Liveness check: run anti-spoofing on the original frame or on the cropped face.
        # Here, we run it on the original frame; alternatively, you could loop through faces.
        live = liveness_check(img)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodedList, encodeFace)
            faceDis = face_recognition.face_distance(encodedList, encodeFace)
            matchIndex = np.argmin(faceDis)

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            # Check liveness before proceeding.
            if not live:
                # Optionally, show a message on the frame.
                ps.putBText(img, 'Spoof', text_offset_x=x1+5, text_offset_y=y2+10,
                            vspace=5, hspace=5, font_scale=1,
                            background_RGB=(0,0,255), text_RGB=(255,255,255),
                            thickness=2, alpha=0.5)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 2)
                recognition_start_time = None
                recognized_id = None
                continue

            if matches[matchIndex] and faceDis[matchIndex] < 0.5:
                Id = imgNames[matchIndex]
                emp = employee.query.filter_by(id=Id).first()

                # Analyze emotion 
                '''
                result = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
                if result['dominant_emotion'] != 'happy':
                    cv2.putText(img, "Please smile to mark attendance", (x1+5, y2+30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    continue
                '''
                if recognized_id != Id:
                    recognition_start_time = datetime.now()
                    recognized_id = Id

                elapsed_time = (datetime.now() - recognition_start_time).total_seconds()
                if elapsed_time < 2:
                    text = f"Recognizing {emp.name}..."
                    text2 = "Hold still and face forward"
                    text3 = f"for {int(3 - elapsed_time)}s"

                    y_offset = y2 + 30  # Adjust the starting position

                    cv2.putText(img, text, (x1+5, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, text2, (x1+5, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, text3, (x1+5, y_offset + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    cv2.rectangle(img, (x1, y1), (x2, y2-4), (0, 255, 0), 2)
                else:
                    text1 = "Press Stop to mark attendance"
                    text2 = f"for {emp.name}"

                    y_offset = y2 + 30  # Adjust vertical position to prevent overlap

                    cv2.putText(img, text1, (x1+5, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(img, text2, (x1+5, y_offset + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    cv2.rectangle(img, (x1, y1), (x2, y2-4), (0, 255, 0), 2)
                    if Id in oldIds:
                        pass
                    else:
                        markEntry(Id)
                        oldIds.append(Id)
            else:
                ps.putBText(img, 'Unknown', text_offset_x=x1+5, text_offset_y=y2+10,
                            vspace=5, hspace=5, font_scale=1,
                            background_RGB=(255,0,0), text_RGB=(255,255,255),
                            thickness=2, alpha=0.5)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 2)
                recognition_start_time = None
                recognized_id = None

        ret, buffer = cv2.imencode('.jpg', img)
        img_bytes = buffer.tobytes()
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + img_bytes + b'\r\n')

# passing generated frames to html page 'recogPage.html'
@app.route('/video', methods=['GET', 'POST'])
def video():
    global cap
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
#show attendance records
@app.route("/AttendanceSheet")
@login_required
def AttendanceSheet():
    rows = []
    with open('static/records.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    fieldnames = ['Id', 'Name', 'Department', 'Time', 'Date', 'Status']
    return render_template('RecordsPage.html', allrows=rows, fieldnames=fieldnames, len=len)

# download all records (combined for all dates)
@app.route("/downloadAll")
def downloadAll():
    return send_file('static/records.csv', as_attachment=True)

# download today's attendance records only
@app.route("/downloadToday")
def downloadToday():
    #extracting todays' records only
    df = pd.read_csv("static/records.csv")
    df = df[df['Date'] == datetime.now().strftime("%d-%m-%Y")]
    df.to_csv("static/todayAttendance.csv", index=False)
    return send_file('static/todayAttendance.csv', as_attachment=True)

# reset today's attendance
@app.route("/resetToday")
@login_required
def resetToday():
    df = pd.read_csv("static/records.csv")
    df = df[df['Date'] != datetime.now().strftime("%d-%m-%Y")]
    df.to_csv("static/records.csv", index=False)
    return redirect('/AttendanceSheet')

def get_working_days(year, month, country='IN'):
    india_holidays = holidays.CountryHoliday(country)
    # Manually add/remove holidays if needed
    if year == 2025 and month == 3:
        india_holidays.pop(date(2025, 3, 14))  # Ensure only Holi is excluded
    total_days_in_month = (date(year, month + 1, 1) - date(year, month, 1)).days if month < 12 else 31
    working_days = 0
    for day in range(1, total_days_in_month + 1):
        current_date = date(year, month, day)
        if current_date.weekday() < 5 and current_date not in india_holidays:
            working_days += 1
    return working_days

def calculate_attendance_percentage(employee_id, year, month, df):
    total_working_days = get_working_days(year, month)
    month_df = df[(df['Id'] == employee_id) & 
                  (pd.to_datetime(df['Date'], format='%d-%m-%Y').dt.year == year) & 
                  (pd.to_datetime(df['Date'], format='%d-%m-%Y').dt.month == month)]
    present_days = month_df[month_df['Status'] == 'On Service'].shape[0]
    if total_working_days > 0:
        percentage = round((present_days / total_working_days) * 100, 2)
    else:
        percentage = 0.0
    return percentage
# some stats on attendance records
@app.route("/stats")
@login_required
def stats():

    #fetching data from attendance csv file and employee database
    df = pd.read_csv("static/records.csv")
    rows = employee.query.all()
    db = [str(row) for row in rows]
    db = pd.DataFrame(db)
    db = pd.DataFrame(data=list(map(lambda x: x.split(" - "), db[0])), columns=['Id', 'Name', 'Department', 'Mail', 'Hiring Date'])

    #create a dataframe which consists the num of employees registered and present today grouped by their dept
    today = df[(df["Date"] == datetime.now().strftime("%d-%m-%Y")) & (df['Status'] == 'On Service')]
    today_counts = pd.DataFrame(today.groupby(['Department']).count()['Id'])
    db_counts = pd.DataFrame(db.groupby(['Department']).count()['Id'])
    attendance = pd.merge(db_counts, today_counts,
                          how='outer', left_index=True, right_index=True)
    attendance.columns = ["Registered", "Present"]
    attendance = attendance.fillna(0).astype(int)
    attendance['Absent'] = attendance['Registered']-attendance['Present']

    #today's attendance dept wise 
    fig1 = px.bar(attendance, x=attendance.index, y=attendance.columns, barmode='group',  labels={'value': 'No of Employees'}, 
    title='Department Wise today\'s Attendance', color_discrete_sequence=px.colors.qualitative.T10, template='presentation')

    #department wise attendance in percentage&counts
    #department wise attendance in percentage&counts
    fig2 = []
    for d in db['Department'].unique():
        present = len(today[today['Department'] == d])
        fig2.append(px.pie(df, values=[present, len(db[db['Department'] == d])-present], names=['Present', 'Absent'],  
         hole=.4, title=d + ' Department', color_discrete_sequence=px.colors.qualitative.T10))


    #last 7 working days' attendance
    dates = df['Date'].unique()[-7:]
    df_last7 = df[df['Date'].isin(dates)]
    fig3 = px.histogram(df_last7, x='Date', color="Department", title='Date & Department wise Attendance',  
    color_discrete_sequence=px.colors.qualitative.T10, template='presentation')

    # Individual attendance percentage (monthly since joining date)
    hiring_dates = [datetime.strptime(d, '%d-%m-%Y') for d in db['Hiring Date']]
    db['Hiring Date'] = hiring_dates

    # Calculate monthly attendance percentage for each employee
    monthly_attendance = []
    for index, row in db.iterrows():
        employee_id = row['Id']
        hiring_date = row['Hiring Date']
        current_date = datetime.now()

        # Generate all months since hiring date
        months_since_hiring = (current_date.year - hiring_date.year) * 12 + (current_date.month - hiring_date.month)
        monthly_percentages = []

        for i in range(months_since_hiring + 1):
            year = hiring_date.year + (hiring_date.month + i - 1) // 12
            month = (hiring_date.month + i - 1) % 12 + 1

            # Calculate attendance percentage for the specific month and year
            percentage = calculate_attendance_percentage(employee_id, year, month, df)
            monthly_percentages.append({
                'Year': year,
                'Month': month,
                'Attendance(%)': percentage
            })

        monthly_attendance.append(monthly_percentages)

    JSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    JSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    JSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    # Pass the current year to the template
    current_year = datetime.now().year
    current_month = datetime.now().month

    return render_template('statsPage.html', JSON1=JSON1, JSON2=JSON2, JSON3=JSON3, depts=db['Department'].unique(), 
                          td=[sum(attendance['Registered']), sum(attendance['Present'])], titles=db.columns.values, 
                          data=list(db.sort_values(by='Name', ascending=True).values.tolist()), len=len, current_year=current_year, current_month=current_month)

@app.route("/filter-monthly-attendance")
@login_required
def filter_monthly_attendance():
    # Get the selected month and year from the request
    selected_month_year = request.args.get('month_year')
    selected_month, selected_year = map(int, selected_month_year.split('-'))

    df = pd.read_csv("static/records.csv")
    rows = employee.query.all()
    db = [str(row) for row in rows]
    db = pd.DataFrame(db)
    db = pd.DataFrame(data=list(map(lambda x: x.split(" - "), db[0])), columns=['Id', 'Name', 'Department', 'Mail', 'Hiring Date'])

    filtered_data = []
    for index, row in db.iterrows():
        employee_id = row['Id']
        hiring_date = datetime.strptime(row['Hiring Date'], '%d-%m-%Y')

        # Check if the selected month and year are after the hiring date
        if selected_year > hiring_date.year or (selected_year == hiring_date.year and selected_month >= hiring_date.month):
            percentage = calculate_attendance_percentage(employee_id, selected_year, selected_month, df)
        else:
            percentage = 0.0  # Employee was not hired in the selected month/year

        filtered_data.append({
            'Id': employee_id,
            'Attendance': percentage
        })

    return jsonify(filtered_data)
'''
@app.route('/get')
def get_bot_response():
    userText = request.args.get('msg')
    # fetch ans corresponding to given question, bot_responses is a global variable declared in helpBot route
    bot_response = bot_responses.get(userText, "Sorry, Can't help with it :(")
    return bot_response
    

@app.route('/helpBot')
def helpBot():
    #load json file globally
    global bot_responses
    with open('static/help.json') as f:
        bot_responses = json.load(f) 
    return render_template('chatBot.html', keys = [*bot_responses])
'''
# Load bot responses once when the app starts
with open('static/help.json', encoding='utf-8') as f:
    bot_responses = json.load(f)

# Predefined greeting messages
greetings = ["hi", "hello", "hey", "hola", "hi there", "good morning", "good afternoon", "good evening"]

@app.route('/helpBot')
def helpBot():
    return render_template('chatBot.html', keys=list(bot_responses.keys()))

@app.route('/get', methods=['GET'])
def chatbot_response():
    user_message = request.args.get('msg', '').strip().lower()

    # Check if user input is a greeting
    if user_message in greetings:
        return jsonify("Hi, welcome to the User Guide ChatBot! Ask your question. 😄")

    # Case-insensitive matching for chatbot responses
    for key in bot_responses.keys():
        if user_message.lower() == key.lower():  # Convert both to lowercase for exact match
            return jsonify(bot_responses[key])

    # If no match found
    return jsonify("I'm sorry, I don't understand that question. 🤔 Please try rephrasing or ask something related to the system!")



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
    