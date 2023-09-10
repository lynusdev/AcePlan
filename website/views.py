from flask import Blueprint, render_template, request, flash, send_file
from flask_login import login_required, current_user
from . import db
from .models import User
import requests
import json
from datetime import datetime

views = Blueprint('views', __name__)

alle_kurse = ["s1", "s2", "s3", "s4", "E1", "E2"]
alle_klassen = ["5a", "5b", "5c", "5d", "6a", "6b", "6c", "6d", "7a", "7b", "7c", "7d", "8a", "8b", "8c", "8d", "9a", "9b", "9c", "9d", "10a", "10b", "10c", "10d", "J1", "J2"]

@views.route("/")
def lander():
    return render_template("lander.html", user=current_user)

@views.route("/download")
def download():
    return send_file(".\static\MyPlan.mobileconfig", as_attachment=True)

@views.route("/home", methods=["GET", "POST"])
@login_required
def home():

    if request.method == 'POST':
        date = request.form.get('date')
    else:
        date = datetime.today().strftime('%Y-%m-%d')

    url = "https://hektor.webuntis.com/WebUntis/monitor/substitution/data?school=KurfuerstFGym"
    payload = {"formatName":"Vertr_Lehrer_heute","schoolName":"KurfuerstFGym","date":date.replace("-", ""),"dateOffset":0,"strikethrough":True,"mergeBlocks":True,"showOnlyFutureSub":False,"showBreakSupervisions":False,"showTeacher":True,"showClass":True,"showHour":True,"showInfo":True,"showRoom":True,"showSubject":True,"groupBy":2,"hideAbsent":True,"departmentIds":[3,2,1,4],"departmentElementType":1,"hideCancelWithSubstitution":False,"hideCancelCausedByEvent":False,"showTime":False,"showSubstText":True,"showAbsentElements":[4,1,2],"showAffectedElements":[],"showUnitTime":False,"showMessages":True,"showStudentgroup":False,"enableSubstitutionFrom":False,"showSubstitutionFrom":0,"showTeacherOnEvent":False,"showAbsentTeacher":True,"strikethroughAbsentTeacher":True,"activityTypeIds":[2,3,4],"showEvent":False,"showCancel":True,"showOnlyCancel":False,"showSubstTypeColor":False,"showExamSupervision":False,"showUnheraldedExams":False}
    response = requests.post(url, json=payload).text
    data_dict = json.loads(response)

    last_update = data_dict["payload"]["lastUpdate"]
    week_day = data_dict["payload"]["weekDay"]
    messages_raw = data_dict["payload"]["messageData"]["messages"]
    messages_cleaned = []
    
    for message in messages_raw:
        message_cleaned = message["body"].replace("<br>", " ").replace("<b>", "").replace("</b>", "")
        messages_cleaned.append(message_cleaned)

    return render_template("home.html", user=current_user, messages=messages_cleaned, date=date, week_day=week_day, last_update=last_update)

@views.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    global alle_kurse
    global alle_klassen
    
    if request.method == 'POST':
        flash('Your settings have been saved!', category='success')
        ausgewählte_kurse = ",".join(request.form.getlist('kurse'))
        klasse = request.form.get('klasse')
        user = User.query.filter_by(id=current_user.id).first()
        user.kurse = ausgewählte_kurse
        user.klasse = klasse
        db.session.commit()

    if not current_user.kurse == None:
        ausgewählte_kurse = current_user.kurse.split(",")
    else:
        ausgewählte_kurse = []
        
    return render_template("settings.html", user=current_user, alle_kurse=alle_kurse, alle_klassen=alle_klassen, ausgewählte_kurse=ausgewählte_kurse)
    