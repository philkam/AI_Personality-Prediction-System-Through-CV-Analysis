from fileinput import filename
import os
import string
import pymysql
from flask import Flask, render_template, request, redirect, flash, send_file, session
from passlib.hash import sha256_crypt
import gc
from werkzeug.utils import secure_filename
import csv
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from PIL import Image
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import pafy
import plotly.express as px
import io,random
from werkzeug.utils import secure_filename
import pandas
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.naive_bayes import MultinomialNB
from test_utils import *

UPLOAD_FOLDER = 'C:/Users/Phoebe E. A. Memsah/Downloads/web_platform_for_aptitude_assessment-master/web_platform_for_aptitude_assessment-master/CV/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

app = Flask(__name__)
app.debug = True
app.secret_key = 'some secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='Quiz_Database',
    port=3306,
    use_unicode=True,
    charset="utf8"
)



@app.route("/")
def home():
    return render_template("/home.html")


@app.route("/aboutus.html")
def aboutus():
    return render_template("/aboutus.html")

@app.route('/index.html')
def homem():
	return render_template('index.html')

@app.route('/prediction', methods=["GET", "POST"])
def prediction():
	if request.method == "POST" and "username" in request.form:
		username = request.form['username']
		model_prediction, tweets = get_prediction(username)
		return render_template('prediction.html', username=username, predicted_type=model_prediction, tweets=tweets)

@app.route("/cvreport.html")
def cvreport():
    cursor = connection.cursor()
    save_image_path = os.path.join(app.config['UPLOAD_FOLDER'], session['cv'])
    resume_data = ResumeParser(save_image_path).get_extracted_data()
    if resume_data:
        ## Get the whole resume data
        resume_text = pdf_reader(save_image_path)
        insert_data(resume_data['name'], resume_data['email'],resume_data['no_of_pages'], str(resume_data['skills']), session['id'])
    command = "select Name, Email_ID, Page_No, Actual_skills from user_data where stud_id =%s"
    cursor.execute(command, session['id'])
    res = cursor.fetchall()

    ### Resume writing recommendation
    resume_text = pdf_reader(save_image_path)
    resume_score = 0
    
    if 'Objective' in resume_text:
        resume_score = resume_score+20
        a = '[+] Awesome! You have added Objective'
    else:
        a = '[-] According to our recommendation please add your career objective, it will give your career intension to the Recruiters.'
        

    if 'Declaration'  in resume_text:
        resume_score = resume_score + 20
        b = '[+] Awesome! You have added Declaration✍'
    else:
        b ='[-] According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you'

    if 'Hobbies' or 'Interests'in resume_text:
        resume_score = resume_score + 20
        c = '[+] Awesome! You have added your Hobbies⚽'
    else:
        c = '[-] According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.'

    if 'Achievements' in resume_text:
        resume_score = resume_score + 20
        d = '[+] Awesome! You have added your Achievements🏅'
    else:
        d = '[+] According to our recommendation please add Achievements🏅. It will show that you are capable for the required position.'

    if 'Projects' in resume_text:
        resume_score = resume_score + 20
        e = '[+] Awesome! You have added your Projects👨‍💻'
    else:
        e = '[-] According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not.'
    
    f = '**Resume Score📝**"'
   
    score = 0
    for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
    g = 'Your Resume Writing Score:' + str(score)
    print(" Your Resume Writing Score: ", str(score))
    h = '** Note: This score is calculated based on the content that you have added in your Resume. **'
    
    connection.commit()
    cursor.close()
    return render_template("/cvreport.html", data = res, value1=a, value2 =b, value3 = c, value4 =d, value5 =e, value6= f, value7 =g, value8=h)
    
    
   
        

@app.route("/reportview.html", methods=['GET'])
def reportview():
    cursor = connection.cursor()

    mark1 = session['sciscore'] 
    mark2 = session['comscore'] 
    mark3 = session['humscore'] 
    mark4 = session['aptitude'] 
    percentage1 = mark1 
    percentage2 = mark2 
    percentage3 = mark3 
    percentage4 = mark4 
    percentage5 = (mark1 + mark2 + mark3 + mark4)
    query = "update student_profile set science = %s , commerce = %s, humanities = %s, aptitude = %s, total =%s where stud_id = %s"
    cursor.execute(query, (percentage1, percentage2, percentage3, percentage4, percentage5, session['id']))
    connection.commit()
    cursor.close()
    return render_template("/studenthome.html")
   


@app.route("/reportgeneration")
def reportgeneration():
    cursor = connection.cursor()
    command = "select stud_first_name, stud_last_name, stud_class, science, humanities, commerce, aptitude, total from student_profile where stud_id =%s "
    cursor.execute(command, session['id'])
    res = cursor.fetchall()
    cursor.close()
    return render_template("/reportgeneration.html", data=res)




@app.route("/questionpaper")
def questionpaper():
    cursor = connection.cursor()
    command = "select * from question_details"
    cursor.execute(command)
    res = cursor.fetchall()
    cursor.close()
    return render_template("/questionpaper.html", data=res)


@app.route("/adddesc", methods=['POST', 'GET'])
def adddesc():
    cursor = connection.cursor()
    if request.method == "POST":
        command = "select count(*) from student_description where stud_id =%s"
        cursor.execute(command, session['id'])
        res = cursor.fetchone()[0]
        if res == 0:
            desc1 = request.form['des1']
            desc2 = request.form['des2']
            desc3 = request.form['des3']
            id = session['id']
            command = "insert into student_description (stud_id,descrip1,descrip2,descrip3) values(%s,%s,%s,%s)"
            cursor.execute(command, (id, desc1, desc2, desc3))
            connection.commit()
            cursor.close()
            return render_template("/studenthome.html")
        else:
            flash("You have already aswered to these questions")
            return render_template("/studentdescription.html")
    else:
        cursor = connection.cursor()
        command = "select count(*) from student_description where stud_id =%s"
        cursor.execute(command, session['id'])
        res = cursor.fetchone()[0]
        cursor.close()
        if res == 0:
            return render_template("/studentdescription.html")
        else:
            flash("You have already answered to these questions")
            return render_template("/studentdescription.html")


@app.route("/adddata", methods=['POST'])
def adddata():
    if request.method == "POST":
        qid = request.form['btn']
        qpid = request.form['qp_id']
        cursor = connection.cursor()
        cmd = "select count(question_id) from question_paper where question_paper_id =%s and question_id =%s"
        cursor.execute(cmd, (qpid, qid))
        res = cursor.fetchone()[0]
        if res == 0:
            command = "insert into question_paper(question_paper_id, question_id, question_type) select %s, question_details.question_id, question_details.question_type from question_details WHERE question_details.question_id =%s "
            cursor.execute(command, (qpid, qid))
            connection.commit()
            cursor.close()
            flash("Successful")
            return redirect("/questionpaper")
        else:
            flash("Question is already added to the question paper")
            return redirect("/questionpaper")


@app.route("/home.html")
def intro():
    return render_template("/home.html")


@app.route("/login.html")
def login():
    return render_template("/login.html")


@app.route("/contactus.html")
def contactus():
    return render_template("/contactus.html")


@app.route('/check_user', methods=['POST'])  # login function
def check_user():
    if request.method == 'POST':
        email = request.form['email']
        user_password = request.form['password']
        cursor = connection.cursor()
        com = "select * from login where u_email='" + email + "'"
        result = cursor.execute(com)
        cursor.close()
        if not result:
            flash("Invalid Login")
            return render_template("/login.html")
        else:
            cursor = connection.cursor()
            com = "select * from login where u_email='" + email + "'"
            cursor.execute(com)
            data = cursor.fetchone()[2]
            com = "select * from login where u_email='" + email + "'"
            cursor.execute(com)
            utype = cursor.fetchone()[3]
            com = "select * from login where u_email='" + email + "'"
            cursor.execute(com)
            uid = cursor.fetchone()[0]
            cursor.close()
            if utype == "Applicant":
                if sha256_crypt.verify(user_password, data):
                    session['logged_in'] = True
                    session['type'] = "Applicant"
                    session['username'] = email
                    session['id'] = uid
                    return render_template("/studenthome.html")
                else:
                    flash("Invalid Login")
                gc.collect()
                return redirect("/login.html")
            elif utype == "admin":
                if sha256_crypt.verify(user_password, data):
                    session['logged_in'] = True
                    session['type'] = "admin"
                    session['username'] = email
                    session['id'] = uid
                    return render_template("/adminhome.html")
                else:
                    flash("Invalid Login")
                    gc.collect()
                    return redirect("/login.html")
            elif utype == "personnel":
                if sha256_crypt.verify(user_password, data):
                    session['logged_in'] = True
                    session['type'] = "personnel"
                    session['username'] = email
                    session['id'] = uid
                    return render_template("/instructorhome.html")
                else:
                    flash("Invalid Login")
                    gc.collect()
                    return redirect('/login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return render_template("/login.html")


@app.route('/logoutprofile', methods=['POST'])  # if not registered
def logoutprofile():
    id = session['username']
    cursor = connection.cursor()
    cmd = "delete from login where u_email = '" + id + "' "
    cursor.execute(cmd)
    connection.commit()
    session.pop('user', None)
    cursor.close()
    flash("Sorry registration unsuccessful")
    return render_template("/signup.html")


@app.route("/studenthome.html")
def stud_home():
    return render_template("/studenthome.html")


@app.route("/signup.html")
def index():
    return render_template("/signup.html")


@app.route("/instructorhome.html")
def instructorhome():
    return render_template("/instructorhome.html")


@app.route("/startquiz.html", methods=['GET'])
def startquiz():
    if request.method == "GET":
        cursor = connection.cursor()
        qry = "select count(*) from active_question_paper where stud_id =%s"
        cursor.execute(qry, session['id'])
        res = cursor.fetchone()[0]
        if res == 0:
            session['countquestion'] = 0
            session['sciscore'] = 0
            session['humscore'] = 0
            session['comscore'] = 0
            session['aptitude'] = 0
            query = "SELECT DISTINCT question_paper_id FROM question_paper where question_paper_id order by  rand() limit 1"
            cursor.execute(query)
            row = cursor.fetchone()
            name = row[0] if row else None
            session['paper'] = name
            qry = "insert into active_question_paper(question_paper_id, question_id, question_type, stud_id, attend) select question_paper.question_paper_id, question_paper.question_id, question_paper.question_type,'%s','0'from question_paper WHERE question_paper.question_paper_id = '%s'"
            cursor.execute(qry, (session['id'], session['paper']))
            connection.commit()
            return render_template("/startquiz.html")
        else:
            qry = "select question_paper_id from active_question_paper where stud_id = %s and attend ='0'"
            cursor.execute(qry, session['id'])
            row = cursor.fetchone()
            name = row[0] if row else None
            session['paper'] = name
            connection.commit()
            flash("Welcome Back")
            return render_template("/startquiz.html")


@app.route("/quiz.html")
def quiz():
    cursor = connection.cursor()
    qry1 = "SELECT COUNT(attend) FROM `active_question_paper` WHERE attend= '0' "
    cursor.execute(qry1)
    row = cursor.fetchone()
    name = row[0] if row else None
    result = name
    if result == 0:
        qry1 = "delete from active_question_paper where question_paper_id = %s"
        cursor.execute(qry1, (session['paper'],))
        connection.commit()
        return render_template("/studenthome.html")
    else:
        query = "select question_id from active_question_paper where question_paper_id= %s and attend='0' and stud_id =%s limit 1"
        cursor.execute(query, (session['paper'], session['id']))
        row = cursor.fetchone()
        res = row[0] if row else None
        session['quiz'] = res
        qry = "select question_type from active_question_paper where question_id= %s and attend='0' and stud_id =%s"
        cursor.execute(qry, (res, session['id']))
        row = cursor.fetchone()
        name = row[0] if row else None
        qtype = name
        if qtype == 110 or qtype == 210 or qtype == 310:
            query1 = "SELECT question_paper.question_paper_id,question_details.question_id,question_details. * from question_paper RIGHT JOIN question_details ON question_paper.question_id= question_details.question_id WHERE question_paper.question_paper_id ='%s' and question_paper.question_id='%s' "
            cursor.execute(query1, (session['paper'], session['quiz']))
            res = cursor.fetchall()
            connection.commit()
            return render_template("/quiz.html", data=res)
        elif qtype == 120 or qtype == 220 or qtype == 320:
            command = "select image from question_details where question_id =%s"
            cursor.execute(command, session['quiz'])
            d = cursor.fetchone()[0]
            connection.commit()
            a = "questionimage/" + d
            command = "select * from question_details where question_id =%s"
            cursor.execute(command, session['quiz'])
            res = cursor.fetchall()
            return render_template("/displayquiz.html", data=res, image=a)
        elif qtype == 130 or qtype == 230 or qtype == 330:
            command = "select * from question_details where question_id =%s"
            cursor.execute(command, session['quiz'])
            res = cursor.fetchone()
            qid = res[0]
            qs = res[1]
            op1 = "questionimage/" + res[2]
            op2 = "questionimage/" + res[3]
            op3 = "questionimage/" + res[4]
            op4 = "questionimage/" + res[5]
            d = "questionimage/" + res[8]
            return render_template("/displayallimage.html", image=d, op1=op1, op2=op2, op3=op3, op4=op4, qs=qs, qid=qid)
        elif qtype == 140 or qtype == 240 or qtype == 340:
            command = "select * from question_details where question_id =%s"
            cursor.execute(command, session['quiz'])
            res = cursor.fetchone()
            qid = res[0]
            qs = res[1]
            op1 = "questionimage/" + res[2]
            op2 = "questionimage/" + res[3]
            op3 = "questionimage/" + res[4]
            op4 = "questionimage/" + res[5]
            return render_template("/onlyoptiondisplay.html", op1=op1, op2=op2, op3=op3, op4=op4, qs=qs, qid=qid)
        else:
            query1 = "SELECT question_paper.question_paper_id,question_details.question_id,question_details. * from question_paper RIGHT JOIN question_details ON question_paper.question_id= question_details.question_id WHERE question_paper.question_paper_id ='%s' and question_paper.question_id='%s' "
            cursor.execute(query1, (session['paper'], session['quiz']))
            res = cursor.fetchall()
            connection.commit()
            return render_template("/quiz.html", data=res)


@app.route("/settings.html")
def settings():
    return render_template("/settings.html")


@app.route("/selectquestionpaper")
def selques():
    cursor = connection.cursor()
    command = "SELECT DISTINCT question_paper_id FROM question_paper"
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("selectquestionpaper.html", data=res)


@app.route("/questionweightage", methods=['GET', 'POST'])
def questionweightage():
    if request.method == "POST":
        session['quesid'] = request.form['option']
        cursor = connection.cursor()
        command = "SELECT question_details.question_id, question_details.question, question_paper.science, question_paper.commerce, question_paper.humanities, question_paper.apt FROM question_details RIGHT JOIN question_paper ON question_paper.question_id= question_details.question_id WHERE question_paper.question_paper_id= '" + \
                  session['quesid'] + "'"
        cursor.execute(command)
        res = cursor.fetchall()
        return render_template("/questionweightage.html", data=res)
    else:
        cursor = connection.cursor()
        command = "SELECT question_details.question_id, question_details.question, question_paper.science, question_paper.commerce, question_paper.humanities,question_paper.apt FROM question_details RIGHT JOIN question_paper ON question_paper.question_id= question_details.question_id WHERE question_paper.question_paper_id= '" + \
                  session['quesid'] + "'"
        cursor.execute(command)
        res = cursor.fetchall()
        return render_template("/questionweightage.html", data=res)


@app.route("/questionweightageedit/<id>")
def questionweightageedit(id):
    cursor = connection.cursor()
    command = "select question_id,science,commerce,humanities,apt from question_paper where question_id =%s and question_paper_id =%s"
    cursor.execute(command, (id, session['quesid']))
    res = cursor.fetchall()
    return render_template("/questionweightageadd.html", data=res)


@app.route("/questionweightageadd", methods=['POST'])
def addquestionweight():
    if request.method == 'POST':
        qid = request.form['id']
        sci = request.form['des1']
        comm = request.form['des2']
        humani = request.form['des3']
        apt = request.form['des4']
        cursor = connection.cursor()
        command = "update question_paper set science = '" + sci + "', commerce= '" + comm + "', humanities= '" + humani + "', apt='" + apt + "' where question_id = '" + qid + "' and question_paper_id = '" + \
                  session['quesid'] + "'"
        cursor.execute(command)
        connection.commit()
        flash("Weightage adding is successful")
        return redirect("/questionweightage")


@app.route("/post_question", methods=['POST'])
def post_question():
    if request.method == 'POST':
        qpid = session['paper']
        qid = request.form['question_id']
        session['quiz'] = int(qid)
        stud_id = session['id']
        user_answer = request.form['response']
        cursor = connection.cursor()
        qry2 = "update active_question_paper set attend='1' where question_paper_id =%s and question_id = %s"
        cursor.execute(qry2, (qpid, qid))
        connection.commit()
        sql = """ALTER TABLE answer_details AUTO_INCREMENT = 1"""
        cursor.execute(sql)
        connection.commit()
        qry = "insert into answer_details (question_paper_id, question_id, stud_id, response) values (%s,%s,%s,%s) "
        cursor.execute(qry, (qpid, qid, stud_id, user_answer))
        connection.commit()
        cursor.execute("SELECT * FROM question_details WHERE question_id= '" + qid + "'")
        res = cursor.fetchone()[6]
        correct_answer = res
        if correct_answer == user_answer:
            command = "select * FROM question_paper WHERE question_paper_id = %s AND question_id = %s"
            cursor.execute(command, (qpid, qid))
            row = cursor.fetchone()
            print( "row3 ", row[3])
            print( "row4 ", row[4])
            print( "row5 ", row[5])
            print( "row6 ", row[6])
            sci = row[3]
            com = row[4]
            hum = row[5]
            apt = row[6]
          
            connection.commit()
            if sci == None:
                sci = 0
            if com == None:
                com = 0
            if hum == None:
                hum = 0
            if apt == None:
                apt = 0
            print("sci", sci)
            print("com", com)
            print("hum", hum)
            print("apt", apt)
            session['sciscore'] = session['sciscore'] +  sci
            print(session['sciscore'])
            session['comscore'] = session['comscore'] +  com
            print(session['comscore'])
            session['humscore'] = session['humscore'] +  hum
            print(session['humscore'])
            session['aptitude'] = session['aptitude'] +  apt
            print(session['aptitude'])
            session['total'] = session['sciscore'] + session['comscore'] + session['humscore'] + session['aptitude']
        qry1 = "SELECT COUNT(question_id) FROM `active_question_paper` WHERE attend= '0' "
        cursor.execute(qry1)
        print(qry1)
        row = cursor.fetchone()
        name = row[0] if row else None
        result = name
        print(result)
        if result == 2:
            qry1 = "delete from active_question_paper where question_paper_id = %s"
            cursor.execute(qry1, session['paper'])
            connection.commit()
            flash(
                "Your assessment is over, please do fill out the details in 'tell us more' section and you can also view your results in 'report' section. Thank you")
            return reportview()
        else:
            return quiz()


@app.route('/post_user', methods=['POST'])  # sign up function
def post_user():
    if request.method == 'POST':
        cursor = connection.cursor()
        email = request.form['email']
        password = sha256_crypt.encrypt(request.form['password'])
        utype = "Applicant"
        x = cursor.execute("select * from login where u_email='" + email + "'")
        if int(x) > 0:
            flash("That username is already taken, please choose another")
            return redirect("/signup.html")
        else:
            if request.form['password'] == request.form['con_password']:
                sql = """ALTER TABLE login AUTO_INCREMENT = 100"""
                cursor.execute(sql)
                com = """insert into login (u_email,password,user_type) values (%s, %s, %s)"""
                cursor.execute(com, (email, password, utype))
                query = "select * from login where u_email='" + email + "'"
                cursor.execute(query)
                data = cursor.fetchone()[0]
                connection.commit()
                session['logged_in'] = True
                session['username'] = email
                session['id'] = data
                cursor.close()
                return render_template("/profile.html")
            else:
                flash("Password not same")
                return redirect("/signup.html")


@app.route("/profile.html")
def profile():
    return render_template('/profile.html')


@app.route("/adminhome.html")
def adminhome():
    return render_template('/adminhome.html')


@app.route("/adminaddinstructor")
def addinstructor():
    return render_template('/adminaddinstructor.html')


@app.route("/adminaddinst_profile", methods=['POST'])  # admin add instructor profile and login details
def adminaddinst_profile():
    if request.method == 'POST':
        firstnme = request.form['frst_name']
        lst_nme = request.form['lst_name']
        dob = request.form['dob']
        gender = request.form['optradio']
        cntno = request.form['phn_no']
        email = request.form['e_mail']
        qualification = request.form['quali']
        house = request.form['house_name']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        pin = request.form['pin_code']
        pasw = "instructor"
        p = sha256_crypt.encrypt(pasw)
        utype = "personnel"
        cursor = connection.cursor()
        sql = """ALTER TABLE login AUTO_INCREMENT = 100"""
        cursor.execute(sql)
        cmd = "insert into login (u_email,password,user_type) values (%s, %s, %s)"
        cursor.execute(cmd, (email, p, utype))
        qry = "select id from login where u_email = '" + email + "'"
        cursor.execute(qry)
        row = cursor.fetchone()
        name = row[0] if row else None
        data = name
        insqry = "insert into instructor_details values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
        cursor.execute(insqry, (
            data, firstnme, lst_nme, dob, gender, cntno, email, qualification, house, city, state, country, pin))
        connection.commit()
        flash("Instructor Creation successful.... Password is" + pasw)
        return render_template("/adminhome.html")


@app.route('/post_profile', methods=['POST'])  # profile completion function
def post_profile():
    id = session['id']
    if request.method == 'POST':
        cursor = connection.cursor()
        firstnme = request.form['frst_name']
        lst_nme = request.form['lst_name']
        dob = request.form['dob']
        gender = request.form['optradio']
        cntno = request.form['phn_no']
        email = session['username']
        institute = request.form['inst']
        clas = request.form['clasnme']
        house = request.form['house_name']
        city = request.form['city']
        country = request.form['country']
        pin = request.form['pin_code'] 
        cv = request.files['cv']
        
        com = "insert into student_profile (stud_id,stud_first_name,stud_last_name,stud_dob,stud_gender,cnt_number,stud_email,stud_inst,stud_class,stud_house,stud_city,stud_country, pin_code)	values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(com,
                       (session['id'], firstnme, lst_nme, dob, gender, cntno, email, institute, clas, house, city, country, pin))
        connection.commit()
        if cv and allowed_file(cv.filename):
            filename = secure_filename(cv.filename)
            cv.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['cv'] = secure_filename(cv.filename)
            
        flash("Thanks for registering!")
        return redirect("/studenthome.html")
    connection.close()
    


@app.route('/change_password', methods=['POST'])  # change password
def change_password():
    if request.method == 'POST':
        cursor = connection.cursor()
        uid = session['username']
        newpassword = sha256_crypt.encrypt(request.form['password1'])
        if request.form['password1'] == request.form['password2']:
            com = "update login set password ='" + newpassword + "' where u_email = '" + uid + "' "
            cursor.execute(com)
            connection.commit()
            flash("Password updated")
            return redirect("/settings.html")
        else:
            flash("Password Does not Match")
            return redirect("/settings.html")


@app.route('/instchange_password', methods=['POST'])  # instructor change password
def instchange_password():
    if request.method == 'POST':
        cursor = connection.cursor()
        uid = session['username']
        newpassword = sha256_crypt.encrypt(request.form['password1'])
        if request.form['password1'] == request.form['password2']:
            com = "update login set password ='" + newpassword + "' where u_email = '" + uid + "' "
            cursor.execute(com)
            connection.commit()
            flash("Password updated")
            return redirect("/instsettings.html")
        else:
            flash("Password Does not Match")
            return redirect("/instsettings.html")


@app.route('/adminchange_password', methods=['POST'])  # admin change password
def adminchange_password():
    if request.method == 'POST':
        cursor = connection.cursor()
        uid = session['username']
        newpassword = sha256_crypt.encrypt(request.form['password1'])
        if request.form['password1'] == request.form['password2']:
            com = "update login set password ='" + newpassword + "' where u_email = '" + uid + "' "
            cursor.execute(com)
            connection.commit()
            flash("Password updated")
            return redirect("/adminsettings.html")
        else:
            flash("Password Does not Match")
            return redirect("/adminsettings.html")


@app.route('/delete_user', methods=['POST'])  # Delete Account
def delete_user():
    if request.method == 'POST':
        uid = session['username']
        cursor = connection.cursor()
        command = "delete from student_profile where stud_email = '" + uid + "'"
        cursor.execute(command)
        query = "delete from login where u_email= '" + uid + "'"
        cursor.execute(query)
        connection.commit()
        cursor.close()
        session.pop('user', None)
        return redirect("/home.html")

    else:
        flash("Wrong password")
        return redirect("/settings.html")


@app.route('/instdelete_user', methods=['POST'])  # instructor Delete Account
def instdelete_user():
    if request.method == 'POST':
        uid = session['username']
        cursor = connection.cursor()
        command = "delete from instructor_details where inst_email = '" + uid + "'"
        cursor.execute(command)
        connection.commit()
        query = "delete from login where u_email= '" + uid + "'"
        cursor.execute(query)
        connection.commit()
        cursor.close()
        session.pop('user', None)
        flash("user deleted successfully...")
        return redirect("/home.html")

    else:
        flash("Wrong password")
        return redirect("/settings.html")


@app.route("/studeditprofile/<id>")  # student profile edit
def studeditprofile(id):
    cursor = connection.cursor()
    command = "select * from student_profile where stud_id= '" + id + "'"
    cursor.execute(command)
    res = cursor.fetchone()
    return render_template("/studeditprofile.html", data=res)


@app.route("/insttextcorpus", methods=['GET', 'POST'])
def textcorpus():
    if request.method == "GET":
        cursor = connection.cursor()
        command = "select student_profile.stud_id,student_profile.stud_first_name,student_profile.stud_last_name,student_description.label FROM student_profile JOIN student_description ON student_profile.stud_id= student_description.stud_id"
        cursor.execute(command)
        res = cursor.fetchall()
        return render_template("/insttextcorpus.html", data=res)
    else:
        btn = request.form['btn']
        label = 1
        cursor = connection.cursor()
        command = "update student_description set label =%s where stud_id =%s"
        cursor.execute(command, (label, btn))
        connection.commit()
        command = "select student_profile.stud_id,student_profile.stud_first_name,student_profile.stud_last_name,student_description.label FROM student_profile JOIN student_description ON student_profile.stud_id= student_description.stud_id"
        cursor.execute(command)
        res = cursor.fetchall()
        return render_template("/insttextcorpus.html", data=res)


@app.route("/insttextnot", methods=['GET','POST'])
def insttextnot():
    if request.method == "GET":
        cursor = connection.cursor()
        command = "select student_profile.stud_id,student_profile.stud_first_name,student_profile.stud_last_name,student_description.label FROM student_profile JOIN student_description ON student_profile.stud_id= student_description.stud_id"
        cursor.execute(command)
        res = cursor.fetchall()
        return render_template("/insttextcorpus.html", data=res)
    else:
        btn = request.form['btn']
        label = 0
        cursor = connection.cursor()
        command = "update student_description set label =%s where stud_id =%s"
        cursor.execute(command, (label, btn))
        connection.commit()
        command = "select student_profile.stud_id,student_profile.stud_first_name,student_profile.stud_last_name,student_description.label FROM student_profile JOIN student_description ON student_profile.stud_id= student_description.stud_id"
        cursor.execute(command)
        res = cursor.fetchall()
        return render_template("/insttextcorpus.html", data=res)


@app.route("/csvadd", methods=['POST'])
def csvadd():
    s= ','
    cursor = connection.cursor()
    command = "SELECT * FROM student_description "
    cursor.execute(command)
    res = cursor.fetchall()
    with open('studenttrain.csv', 'wb') as csvfile:
        fieldnames = ['id', 'label', 'msg']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in res:
            ds1 = i[2]
            de2 = i[3]
            de3 = i[4]
            a = (ds1,de2 ,de3)
            writer.writerow({'id': i[0], 'label': i[1], 'msg': s.join(a)})
    flash("sucessful")
    command = "select student_profile.stud_id,student_profile.stud_first_name,student_profile.stud_last_name,student_description.label FROM student_profile JOIN student_description ON student_profile.stud_id= student_description.stud_id"
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/insttextcorpus.html", data=res)


@app.route("/viewprofile")  # student profile view
def view_user():
    uid = session['username']
    cursor = connection.cursor()
    command = "select * from student_profile where stud_email= '" + uid + "'"
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/viewprofile.html", data=res)


@app.route("/instructorprofileview")  # instructor profile view
def instructorprofileview():
    uid = session['username']
    cursor = connection.cursor()
    command = "select * from instructor_details"
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/instructorprofileview.html", data=res)


@app.route("/editinstructorprofile/<id>")  # instructor profile edit
def editinstructorprofile(id):
    cursor = connection.cursor()
    command = "select * from instructor_details where inst_id= '" + id + "'"
    cursor.execute(command)
    res = cursor.fetchone()
    return render_template("/editinstructorprofile.html", data=res)


@app.route("/update_instr", methods=['POST', 'GET'])  # instructor profile update
def update_instr():
    if request.method == 'POST':
        cursor = connection.cursor()
        uid = request.form['id']
        frst_name = request.form['frst_name']
        lst_name = request.form['lst_name']
        phone_no = request.form['phn_no']
        qualification = request.form['quali']
        house = request.form['house_name']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        pincode = request.form['pin_code']
        qry = "update instructor_details set inst_first_name='" + frst_name + "',inst_last_name='" + lst_name + "',inst_contact_no='" + phone_no + "', inst_qualification='" + qualification + "', inst_state='" + state + "',inst_house='" + house + "',inst_city='" + city + "',inst_country='" + country + "', inst_pin='" + pincode + "' where inst_id='" + uid + "'"
        cursor.execute(qry)
        connection.commit()
        flash("update successful")
        return render_template("/instructorhome.html")
    else:
        return render_template("/instructorhome.html")


@app.route("/instmanagestudent")  # instructor student profile view
def instmanagestudent():
    uid = session['username']
    cursor = connection.cursor()
    command = "select * from student_profile"
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/instmanagestudent.html", data=res)


@app.route("/insteditstudent/<id>")  # instructor editview student profile
def insteditstudent(id):
    cursor = connection.cursor()
    command = "select * from student_profile where stud_id= '" + id + "'"
    cursor.execute(command)
    res = cursor.fetchone()
    return render_template("/insteditstudent.html", data=res)


@app.route("/update_stud", methods=['POST', 'GET'])  # instructor student profile update
def update_stud():
    if request.method == 'POST':
        cursor = connection.cursor()
        uid = request.form['id']
        frst_name = request.form['frst_name']
        lst_name = request.form['lst_name']
        phone_no = request.form['phn_no']
        institute = request.form['inst']
        clasnme = request.form['clasnme']
        house = request.form['house_name']
        city = request.form['city']
        country = request.form['country']
        pincode = request.form['pin_code']
        qry = "update student_profile set stud_first_name='" + frst_name + "',stud_last_name='" + lst_name + "',cnt_number='" + phone_no + "', stud_inst='" + institute + "', stud_class='" + clasnme + "',stud_house='" + house + "',stud_city='" + city + "',stud_country='" + country + "', pin_code='" + pincode + "' where stud_id='" + uid + "'"
        cursor.execute(qry)
        connection.commit()
        flash("update successful")
        return render_template("/instructorhome.html")
    else:
        return render_template("/instructorhome.html")


@app.route("/adminstudentmanage")  # admin view student
def adminstudentmanage():
    cursor = connection.cursor()
    command = "select * from student_profile "
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/adminstudentmanage.html", data=res)


@app.route("/admineditstudent/<id>")  # admin edit view student profile
def admineditstudent(id):
    cursor = connection.cursor()
    command = "select * from student_profile where stud_id= '" + id + "'"
    cursor.execute(command)
    res = cursor.fetchone()
    return render_template("/admineditstudent.html", data=res)


@app.route("/update_studadmin", methods=['POST', 'GET'])  # admin student profile update
def update_studadmin():
    if request.method == 'POST':
        cursor = connection.cursor()
        uid = request.form['id']
        frst_name = request.form['frst_name']
        lst_name = request.form['lst_name']
        phone_no = request.form['phn_no']
        institute = request.form['insti']
        clasnme = request.form['cls']
        house = request.form['house_name']
        city = request.form['city']
        country = request.form['country']
        pincode = request.form['pin_code']
        qry = "update student_profile set stud_first_name='" + frst_name + "',stud_last_name='" + lst_name + "',cnt_number='" + phone_no + "', stud_inst='" + institute + "', stud_class='" + clasnme + "',stud_house='" + house + "',stud_city='" + city + "',stud_country='" + country + "', pin_code='" + pincode + "' where stud_id='" + uid + "'"
        cursor.execute(qry)
        connection.commit()
       

        flash("update successful")
        return render_template("/adminhome.html")
    else:
        return render_template("/adminhome.html")

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def insert_data(name,email,no_of_pages,skills, stud_id):
    cursor = connection.cursor()
    DB_table_name = 'user_data'
    insert_sql = "REPLACE INTO " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, no_of_pages, skills,stud_id)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

@app.route("/questionview", methods=['GET'])  # instructor view question
def questionview():
    if request.method == 'GET':
        cursor = connection.cursor()
        command = "select * from question_details"
        cursor.execute(command)
        res = cursor.fetchall()
        return render_template("/questionview.html", data=res)


@app.route("/questionedit/<id>")  # instructor edit view question
def questionedit(id):
    cursor = connection.cursor()
    command = "select * from question_details where question_id= '" + id + "'"
    cursor.execute(command)
    res = cursor.fetchone()
    return render_template("/questionedit.html", data=res)


@app.route("/deletequestion/<id>")  # instructor delete question
def deletequestion(id):
    cursor = connection.cursor()
    qry = "select question_id from question_paper where question_id= %s"
    res = cursor.execute(qry, id)
    if res > 0:
        cmd = "DELETE question_details.*, question_paper.* FROM question_details JOIN question_paper ON question_paper.question_id=question_details.question_id WHERE question_details.question_id= %s"
        cursor.execute(cmd, id)
        connection.commit()
        flash("Question has been removed")
        return questionviewselect()
    else:
        command = "delete from question_details where question_id = %s"
        cursor.execute(command, id)
        connection.commit()
        flash("Question has been removed")
        return questionviewselect()


@app.route("/update_question", methods=['POST', 'GET'])  # instructor question update
def update_question():
    if request.method == 'POST':
        cursor = connection.cursor()
        uid = request.form['id']
        question = request.form['question']
        val1 = request.form['val1']
        val2 = request.form['val2']
        val3 = request.form['val3']
        val4 = request.form['val4']
        ans = request.form['ans']
        qry = "update question_details set question='" + question + "',value1='" + val1 + "',value2='" + val2 + "', value3='" + val3 + "', value4='" + val4 + "',answer='" + ans + "' where question_id='" + uid + "'"
        cursor.execute(qry)
        connection.commit()
        flash("update successful")
        return render_template("/instructorhome.html")
    else:
        return render_template("/instructorhome.html")


@app.route("/addquestion", methods=['POST', 'GET'])  # add question by instructor
def addquestion():
    if request.method == "POST":
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        cursor = connection.cursor()
        commad = "ALTER TABLE question_details AUTO_INCREMENT = 1"
        cursor.execute(commad)
        cmd = int(session['aof'] + session['qtype'] + '0')
        command = "insert into question_details (question,value1,value2,value3,value4, answer,question_type ) values (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(command, (question, option1, option2, option3, option4, answer, cmd))
        connection.commit()
        flash("Question insertion successful")
        return render_template("/addquestion.html")
    else:
        return render_template("/addquestion.html")


@app.route("/instsettings.html")
def instsettings():
    return render_template("/instsettings.html")


@app.route("/adminsettings.html")
def adminsettings():
    return render_template("/adminsettings.html")


@app.route("/adminviewinstructor")  # admin instructor profile view
def view_instructor():
    cursor = connection.cursor()
    command = "select * from instructor_details "
    cursor.execute(command)
    res = cursor.fetchall()
    return render_template("/adminviewinstructor.html", data=res)


@app.route("/admineditinstructordetails/<id>")  # admin instructor profile edit
def admineditinstructordetails(id):
    cursor = connection.cursor()
    command = "select * from instructor_details where inst_id= '" + id + "'"
    cursor.execute(command)
    res = cursor.fetchone()
    return render_template("/admineditinstructordetails.html", data=res)


@app.route("/updateinst_profile", methods=['post'])  # admin update instructor profile
def updateinst_profile():
    if request.method == 'POST':
        uid = request.form['id']
        firstnme = request.form['frst_name']
        lst_nme = request.form['lst_name']
        dob = request.form['dob']
        gender = request.form['gender']
        cntno = request.form['phn_no']
        email = request.form['e_mail']
        qualification = request.form['quali']
        house = request.form['house_name']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        pin = request.form['pin_code']
        cursor = connection.cursor()
        qry = "update instructor_details set inst_first_name = '" + firstnme + "', inst_last_name ='" + lst_nme + "', inst_dob ='" + dob + "', inst_gender='" + gender + "', inst_contact_no= '" + cntno + "', inst_email='" + email + "', inst_qualification= '" + qualification + "', inst_house = '" + house + "', inst_city = '" + city + "', inst_state='" + state + "', inst_country='" + country + "', inst_pin= '" + pin + "' where inst_id = '" + uid + "'"
        cursor.execute(qry)
        connection.commit()
        flash("update successful")
        return render_template("/adminhome.html")
    else:
        return render_template("/adminhome.html")


@app.route("/update_profile", methods=['post'])  # student profile update
def update_user():
    if request.method == 'POST':
        uid = session['username']
        frst_name = request.form['frst_name']
        lst_name = request.form['lst_name']
        phone_no = request.form['phn_no']
        institute = request.form['inst']
        clasnme = request.form['clasnme']
        house = request.form['house_name']
        city = request.form['city']
        country = request.form['country']
        pincode = request.form['pin_code']
        qry = "update student_profile set stud_first_name='" + frst_name + "',stud_last_name='" + lst_name + "',cnt_number='" + phone_no + "', stud_inst='" + institute + "', stud_class='" + clasnme + "',stud_house='" + house + "',stud_city='" + city + "',stud_country='" + country + "', pin_code='" + pincode + "' where stud_email='" + uid + "'"
        cursor = connection.cursor()
        cursor.execute(qry)
        connection.commit()
        flash("update successful")
        return render_template("/studenthome.html")
    else:
        return render_template("/studenthome.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/imagequestion", methods=['GET', 'POST'])
def imagequestion():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        answer = request.form['answer']
        cursor = connection.cursor()
        commad = "ALTER TABLE question_details AUTO_INCREMENT = 1"
        cursor.execute(commad)
        command = "insert into question_details (question,value1,value2,value3,value4, answer ) values (%s,%s,%s,%s,%s,%s)"
        cursor.execute(command, (question, option1, option2, option3, option4, answer))
        connection.commit()
        commad = "select question_id from question_details where question =%s"
        cursor.execute(commad, question)
        qid = cursor.fetchone()[0]
        fname = str(qid) + str(session['qtype'])
        cmd = int(session['aof'] + session['qtype'] + '0')
        connection.commit()
        file = request.files['file']
        oldext = filfunction(file, fname)
        commad = "update question_details set image= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (fname + oldext, cmd, qid))
        connection.commit()
        flash("successful")
        return render_template("/imagequestion.html")
    else:
        return render_template("/imagequestion.html")


def filfunction(file, fname):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        oldext = os.path.splitext(filename)[1]
        os.rename(UPLOAD_FOLDER + filename, UPLOAD_FOLDER + fname + oldext)
        return oldext


@app.route("/imagequestionoptionadd", methods=['GET', 'POST'])
def imagequestionoptionadd():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.files['opt1']
        option2 = request.files['opt2']
        option3 = request.files['opt3']
        option4 = request.files['opt4']
        answer = request.form['answer']
        file = request.files['file']
        cursor = connection.cursor()
        commad = "ALTER TABLE question_details AUTO_INCREMENT = 1"
        cursor.execute(commad)
        cmd = "select max(question_id) from question_details"
        cursor.execute(cmd)
        id = cursor.fetchone()[0]
        cmd = "insert into question_details (question) values (%s)"
        cursor.execute(cmd, question)
        connection.commit()
        qid = id + 1
        opt1 = str(qid) + session['qtype'] + '10'
        opt2 = str(qid) + session['qtype'] + '20'
        opt3 = str(qid) + session['qtype'] + '30'
        opt4 = str(qid) + session['qtype'] + '40'
        img = str(qid) + session['qtype'] + '0'
        cmd = int(session['aof'] + session['qtype'] + '0')
        oldext = filfunction(file, img)
        commad = "update question_details set image= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (img + oldext, cmd, qid))
        connection.commit()
        oldext = filfunction(option1, opt1)
        commad = "update question_details set value1= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (opt1 + oldext, cmd, qid))
        connection.commit()
        if answer == "option1":
            op = "questionimage/" + opt1 + oldext
            commad = "update question_details set answer =%s where question_id = %s"
            cursor.execute(commad, (op, qid))
            connection.commit()
        oldext = filfunction(option2, opt2)
        commad = "update question_details set value2= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (opt2 + oldext, cmd, qid))
        connection.commit()
        if answer == "option2":
            op = "questionimage/" + opt2 + oldext
            commad = "update question_details set answer =%s  where question_id = %s"
            cursor.execute(commad, (op, qid))
            connection.commit()
        oldext = filfunction(option3, opt3)
        commad = "update question_details set value3= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (opt3 + oldext, cmd, qid))
        connection.commit()
        if answer == "option3":
            op = opt3 + oldext
            commad = "update question_details set answer =%s  where question_id = %s"
            cursor.execute(commad, (op, qid))
            connection.commit()
        oldext = filfunction(option4, opt4)
        commad = "update question_details set value4= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (opt4 + oldext, cmd, qid))
        connection.commit()
        if answer == "option4":
            op = "questionimage/" + opt4 + oldext
            commad = "update question_details set answer =%s  where question_id = %s"
            cursor.execute(commad, (op, qid))
            connection.commit()
        flash("successful")
        return render_template("/imagequestionoptionadd.html")

    else:
        return render_template("/imagequestionoptionadd.html")


@app.route("/onlyoptionadd", methods=['GET', 'POST'])
def onlyoptionadd():
    if request.method == 'POST':
        question = request.form['question']
        option1 = request.files['opt1']
        option2 = request.files['opt2']
        option3 = request.files['opt3']
        option4 = request.files['opt4']
        answer = request.form['answer']
        cursor = connection.cursor()
        commad = "ALTER TABLE question_details AUTO_INCREMENT = 1"
        cursor.execute(commad)
        cmd = "select max(question_id) from question_details"
        cursor.execute(cmd)
        id = cursor.fetchone()[0]
        cmd = "insert into question_details (question) values (%s)"
        cursor.execute(cmd, question)
        connection.commit()
        qid = id + 1
        opt1 = str(qid) + session['qtype'] + '10'
        opt2 = str(qid) + session['qtype'] + '20'
        opt3 = str(qid) + session['qtype'] + '30'
        opt4 = str(qid) + session['qtype'] + '40'
        img = str(qid) + session['qtype'] + '0'
        cmd = int(session['aof'] + session['qtype'] + '0')
        oldext = filfunction(option1, opt1)
        commad = "update question_details set value1= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (opt1 + oldext, cmd, qid))
        connection.commit()
        if answer == "option1":
            op = "questionimage/" + opt1 + oldext
            commad = "update question_details set answer =%s where question_id = %s"
            cursor.execute(commad, (op, qid))
            connection.commit()
        oldext = filfunction(option2, opt2)
        commad = "update question_details set value2= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (opt2 + oldext, cmd, qid))
        connection.commit()
        if answer == "option2":
            op = "questionimage/" + opt2 + oldext
            commad = "update question_details set answer =%s  where question_id = %s"
            cursor.execute(commad, (op, qid))
            connection.commit()
        oldext = filfunction(option3, opt3)
        commad = "update question_details set value3= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (opt3 + oldext, cmd, qid))
        connection.commit()
        if answer == "option3":
            op = "questionimage/" + opt3 + oldext
            commad = "update question_details set answer =%s  where question_id = %s"
            cursor.execute(commad, (op, qid))
            connection.commit()
        oldext = filfunction(option4, opt4)
        commad = "update question_details set value4= %s, question_type =%s where question_id = %s"
        cursor.execute(commad, (opt4 + oldext, cmd, qid))
        connection.commit()
        if answer == "option4":
            op = "questionimage/" + opt4 + oldext
            commad = "update question_details set answer =%s  where question_id = %s"
            cursor.execute(commad, (op, qid))
            connection.commit()
        flash("successful")
        return render_template("/onlyoptionadd.html")
    else:
        return render_template("/onlyoptionadd.html")


@app.route("/questionselect", methods=['GET', 'POST'])
def questionselect():
    if request.method == 'POST':
        qptype = request.form['option1']
        aof = request.form['option2']
        session['aof'] = aof
        session['qtype'] = qptype
        if qptype == "1":
            return render_template("/addquestion.html")
        elif qptype == "2":
            return render_template("/imagequestion.html")
        elif qptype == "3":
            return render_template("/imagequestionoptionadd.html")
        else:
            return render_template("/onlyoptionadd.html")
    else:
        return render_template("/questionselect.html")


@app.route("/questionviewselect", methods=['GET', 'POST'])
def questionviewselect():
    if request.method == 'POST':
        qptype = request.form['option1']
        aof = request.form['option2']
        session['aof'] = int(aof)
        session['qtype'] = qptype
        cursor = connection.cursor()
        if qptype == "1":
            if aof == "1":
                command = "select * from question_details where question_type like '11%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/questionview.html", data=res)
            elif aof =="2":
                command = "select * from question_details where question_type like '21%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/questionview.html", data=res)
            elif aof =="3":
                command = "select * from question_details where question_type like '31%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/questionview.html", data=res)
            else:
                command = "select * from question_details where question_type like '41%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/questionview.html", data=res)
        elif qptype == "2":
            if aof =="1":
                command = "select * from question_details where question_type like '12%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/viewimagequestion.html", data=res)
            elif aof =="2":
                command = "select * from question_details where question_type like '22%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/viewimagequestion.html", data=res)
            elif aof =="3":
                command = "select * from question_details where question_type like '32%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/viewimagequestion.html", data=res)
            else:
                command = "select * from question_details where question_type like '42%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/viewimagequestion.html", data=res)
        elif qptype == "3":
            if aof=="1":
                command = "select * from question_details where question_type like '13%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/optionquestionimageview.html", data=res)
            elif aof =="2":
                command = "select * from question_details where question_type like '23%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/optionquestionimageview.html", data=res)
            elif aof =="3":
                command = "select * from question_details where question_type like '33%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/optionquestionimageview.html", data=res)
            else:
                command = "select * from question_details where question_type like '43%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/optionquestionimageview.html", data=res)
        else:
            if aof == "1":
                command = "select * from question_details where question_type like '14%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/imageoptiononlyview.html", data=res)
            elif aof =="2":
                command = "select * from question_details where question_type like '24%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/imageoptiononlyview.html", data=res)
            elif aof =="3":
                command = "select * from question_details where question_type like '34%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/imageoptiononlyview.html", data=res)
            else:
                command = "select * from question_details where question_type like '44%'"
                cursor.execute(command)
                res = cursor.fetchall()
                if len(res) <0:
                    flash("No questions are available")
                return render_template("/imageoptiononlyview.html", data=res)
    else:
        return render_template("/questionviewselect.html")



def learning_user():
    data = open('data/corpus').read()
    labels, texts = [], []
    for i, line in enumerate(data.split("\n")):
        content = line.split()
        labels.append(content[0])
        texts.append(" ".join(content[1:]))

    # create a dataframe using texts and lables
    trainDF = pandas.DataFrame()
    trainDF['text'] = texts
    trainDF['label'] = labels
    # split the dataset into training and validation datasets
    train_x, valid_x, train_y, valid_y = train_test_split(trainDF['text'], trainDF['label'])

    # label encode the target variable
    encoder = sklearn.preprocessing.LabelEncoder()
    train_y = encoder.fit_transform(train_y)
    valid_y = encoder.fit_transform(valid_y)

    # create a count vectorizer object
    count_vect = CountVectorizer(analyzer='word', token_pattern=r'\w{1,}')
    count_vect.fit(trainDF['text'])

    # transform the training and validation data using count vectorizer object
    xtrain_count = count_vect.transform(train_x)
    xvalid_count = count_vect.transform(valid_x)
    nb = MultinomialNB()
    nb.fit(xtrain_count, train_y)
    y_pred = nb.predict(xvalid_count)
    accuracy = (accuracy_score(valid_y, y_pred))
    print ("accuracy =", accuracy)
    print(classification_report(valid_y, y_pred))

    trainDF['char_count'] = trainDF['text'].apply(len)
    addfile(trainDF['char_count'].head())
    trainDF['word_count'] = trainDF['text'].apply(lambda x: len(x.split()))
    addfile(trainDF['word_count'].head())
    trainDF['word_density'] = trainDF['char_count'] / (trainDF['word_count'] + 1)
    addfile(trainDF['word_density'].head())
    trainDF['punctuation_count'] = trainDF['text'].apply(
        lambda x: len("".join(_ for _ in x if _ in string.punctuation)))
    addfile(trainDF['punctuation_count'].head())
    trainDF['title_word_count'] = trainDF['text'].apply(lambda x: len([wrd for wrd in x.split() if wrd.istitle()]))
    addfile(trainDF['title_word_count'].head())
    trainDF['upper_case_word_count'] = trainDF['text'].apply(lambda x: len([wrd for wrd in x.split() if wrd.isupper()]))
    addfile(trainDF['upper_case_word_count'].head())

    return 0


def addfile(x):
    f = open('outcome.txt', 'a')
    f.write(str(x) + '\n')
    f.close()


if __name__ == "__main__":
    app.run()
