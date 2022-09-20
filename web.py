
from unicodedata import name
from flask import Flask,jsonify,request,render_template,url_for,flash,redirect,session
from flask_session import Session
import sqlite3
import json,bcrypt,re
from flask_mail import Mail, Message
from random import *
import os
from werkzeug.utils import secure_filename
#from werkzeug.wrappers import Request, Response


app=Flask(__name__)
app.secret_key = b'\x1e\xfb\x06%\xd8IN\x8c\xad@\xe6M'
mail=Mail(app)
otp=randint(100000,999999)
UPLOAD_FOLDER = r"C:\Users\pr.srivastava1\flask"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'srivastavashibu0@gmail.com'
app.config['MAIL_PASSWORD'] = 'khiwnokzoibznjfa'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def db_connection():                             #for connection
    conn=None
    try:
        conn=sqlite3.connect('geek2.db')
    except sqlite3.erorr as e:
        print(e)
    return conn

@app.route('/register',methods=["GET","POST"])
def register():
    if request.method=="POST":
        conn=db_connection()
        cursor=conn.cursor()
        NAME=request.form["NAME"]
        CLASS=request.form["CLASS"]
        SECTION=request.form["SECTION"]
        email=request.form["email"]
        password=request.form["password"]
        cpassword=request.form["cpassword"]
        #print(NAME)
        #print(CLASS)
        #print(SECTION)
        #print(cpassword)
        #print(email)
        if len(NAME)<3:                                                     #name validation
            flash('Name length should be greater than 2')
            return render_template('register.html')

        if int(CLASS)>12:
            flash('Class can not be greater than 12th')
            return render_template('postdata.html')                             #class validation
        else:
            if CLASS=='1':
                CLASS=CLASS+'st'
            elif CLASS=='2':
                CLASS=CLASS+'nd'
            elif CLASS=='3':
                CLASS=CLASS+'rd'
            else:
                if CLASS=='4' or CLASS=='5' or CLASS=='6' or CLASS=='7' or CLASS=='8' or CLASS=='9' or CLASS=='10' or CLASS=='11' or CLASS=='12':
                    CLASS=CLASS+'th'
        

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{3,}\b'
        if not re.fullmatch(regex,email):                                   #email verification
            flash('Write correct email','error')
            return render_template('register.html')
        

        if password==cpassword:
            regex1=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            if not re.fullmatch(regex1,password):
                flash('Password is not strong.Your password should be 8 in lenghth,use of small and capital letter should be there and use of special character','error')
                return render_template('register.html')

            sql="select * from customer where email='{}'".format(email)
            cursor=cursor.execute(sql)
            ans=cursor.fetchall()                                          #duplicate verification
            if len(ans)>0:
                flash('An email already exist','error')
                return render_template('register.html')

            hashed=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            print(hashed)
            sql="INSERT INTO CUSTOMER(name,class,section,email,password)values(?,?,?,?,?)"
            cursor=cursor.execute(sql,(NAME,CLASS,SECTION,email,hashed,))
            #sql1="INSERT INTO STUDENT(email)values(?)"
            #cursor=cursor.execute(sql1,(email,))
            conn.commit()
            conn.close()
            flash('User successfully created')
        else:
            flash('password do not match')
            return render_template('register.html')
 
    return render_template("register.html")

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="POST":
        conn=db_connection()
        cursor=conn.cursor()
        email=request.form["email"]
        password=request.form["password"]
        session["mail1"]=email
        otp=randint(100000,999999)
        print(otp)
        sql1="select * from customer where email='{}'".format(email)
        cursor=cursor.execute(sql1)
        res1=cursor.fetchall()
        print(res1)
        if not len(res1)>0:
            flash('Enter valid email','error')
            return render_template('login.html')
        ans=""
        ans=res1[0][5]
        ans1=res1[0][0]
        session["sno1"]=ans1

        
        if bcrypt.checkpw(password.encode('utf-8'),ans):
            msg=Message(
                'OTP Verification',
                sender="srivastavashibu0@gmail.com",
                recipients=[email]
            )
            msg.body='Hello customer, Use this otp for verification'+ str(otp)
            mail.send(msg)
            session["otp1"]=otp
            flash(f'Mail sent on {email}, Please use the otp for verification')
            return render_template('otp.html')
            #return render_template('main.html')
        else:
            flash('Enter correct password','error')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/fpass',methods=["GET","POST"])
def sendmail():
    if request.method=="POST":
        email=request.form["email"]
        #print(email)
        session["mail"]=email
        conn=db_connection()
        cursor=conn.cursor()
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{3,}\b'
        if not re.fullmatch(regex,email):                                   #email verification
            flash('Write correct email','error')
            return render_template('fpassword.html')
        sql1="select * from customer where email='{}'".format(email)
        cursor=cursor.execute(sql1)
        res=cursor.fetchall()
        if len(res)>0:
            msg=Message(
                'Hello',
                sender="srivastavashibu0@gmail.com",
                recipients=[email]
            )
            msg.body='Hello customer, Use this link to update your password http://127.0.0.1:5000/updatep'
            mail.send(msg)
            flash(f'Mail sent on {email}, Please update the password from the link')
            return render_template('fpassword.html')
        else:
            flash('This email does not exist, Please create a new account')
            return render_template('fpassword.html')
    return render_template('fpassword.html')

@app.route('/updatep',methods=["GET","POST"])
def updatepass():
    if request.method=="POST":
        #email=request.form["email"]
        password=request.form["password"]
        cpassword=request.form["cpassword"]
        email=session.get("mail")
        print(email)
        conn=db_connection()
        cursor=conn.cursor()
        if password==cpassword:
            sql="select * from customer where email='{}'".format(email)
            cursor=cursor.execute(sql)
            res=cursor.fetchall()
            #if not len(res)>0:
                #flash('Enter valid email')
                #return render_template('forgotp.html')
            ans=res[0][5]
            id=res[0][0]
            session["id1"]=id
            #print(type(ans))

            regex1=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            if not re.fullmatch(regex1,password):
                flash('Password is not strong.Your password should be 8 in lenghth,use of small and capital letter should be there and use of special character','error')
                return render_template('forgotp.html')

            if bcrypt.checkpw(password.encode('utf-8'),ans):
                flash('This password matches with your previous password')
                return render_template('forgotp.html')

            

            hashed=bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
            
            sql1="""UPDATE customer SET password=? where SNO=?"""
            cursor.execute(sql1,(hashed,id,))
            conn.commit()
            flash('Password successfully updated','success')
            return render_template('forgotp.html')
        else:
            flash('Password do not match')
            return render_template('forgotp.html')
    return render_template('forgotp.html')


@app.route('/otp',methods=["GET","POST"])
def verification():
    if request.method=="POST":
        otp=request.form["otp"]
        otpp=session.get("otp1")
        print(otpp)
        if otpp==int(otp):
            return redirect(url_for('showdata'))
        else:
            flash('Wrong Otp')
            return render_template('otp.html')
    return render_template('otp.html')

@app.route('/main',methods=["GET","POST"])
def showdata():
    conn=db_connection()    
    cursor=conn.cursor()
    email=session.get("mail1")
    print(email)
    sql="select name,class,section,email from customer where email=?"
    cursor=cursor.execute(sql,(email,))
    data=cursor.fetchall()
    res=data[0][0]
    flash(f'Hello {res}, Here are all your details')
    return render_template('main.html',data=data)

@app.route('/deactivate',methods=["GET","POST"])
def deleteuser():
    conn=db_connection()
    cursor=conn.cursor()
    if request.method=="POST":
        email=request.form["email"]
        email1=session.get("mail")
        print(email1)
        if email==email1:
            sql="DELETE FROM CUSTOMER WHERE email=?"
            cursor.execute(sql,(email,))
            conn.commit()
            flash('deleted successfully')
            return render_template('delete.html')
        else:
            flash('Enter your email')
            return render_template('delete.html')
    return render_template('delete.html')

@app.route('/updated',methods=["GET","POST"])
def get_update():
    if request.method=="POST":
        f=request.args
        print(f)
        f=json.dumps(f)
        f=json.loads(f)
        obj=update_info(f)
        #return render_template('update.html')
    return render_template('update.html')

 
def update_info(data):
    conn=db_connection()
    cursor=conn.cursor()
    qry="""UPDATE CUSTOMER SET """
    count=0
    print(data)
    for key,value in data.items():
        if value!='' and key != 'SNO':
            count+=1
            qry=qry+f"{key} ="
            qry=qry+'"'
            qry=qry+f"{value}"
            qry=qry+'"'+','
    qry=qry[:-1]+' '+f' where SNO = {data["SNO"]} '
    print(qry)
        # try:
    if count==0:
        return 'No value Provided'
    else:
        print(qry)
        cursor.execute(qry)
        ans1 =cursor.fetchall()
        conn.commit()
        print(qry)
        # except:
        return 'Value updated'
        

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        file = request.files['file']
        if 'file' not in request.files:
            flash('No file part')
            return render_template('upload.html')
        if file.filename == '':
            flash('No selected file')
            return render_template('upload.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('SUCCESSFULLY UPLOADED')
            return render_template('upload.html',name=filename)
        else:
            flash('Please upload the file wh')
    return render_template('upload.html')
        



if __name__=='__main__':
    app.run(debug=True)



#msg=Message(
            #'Hello',
            #sender="srivastavashibu0@gmail.com",
            #recipients=['shibuprakhar1999@gmail.com']
            #)
            #msg.body='Hello ji mail aagya'
            #mail.send(msg)
            #flash('sent')