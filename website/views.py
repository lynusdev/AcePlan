from flask import Blueprint, render_template, request, flash, send_file
from flask_login import login_required, current_user
from . import db
from .models import User
import requests
import json
from datetime import datetime
import html

views = Blueprint('views', __name__)

alle_klassen = ["5A", "5B", "5C", "5D", "6A", "6B", "6C", "6D", "7A", "7B", "7C", "7D", "8A", "8B", "8C", "8D", "9A", "9B", "9C", "9D", "10A", "10B", "10C", "10D", "J1", "J2"]

# Landing page
@views.route("/")
def lander():
    return render_template("lander.html", user=current_user)

# Download iOS profile
@views.route("/ios")
def ios():
    return send_file("./static/AcePlan.mobileconfig", as_attachment=True)

# Download APK
@views.route("/android")
def android():
    return send_file("./static/AcePlan.apk", as_attachment=True)

# Home / Substitution plan
@views.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if request.method == 'POST':
        date = request.form.get('date')
    else:
        date = datetime.today().strftime('%Y-%m-%d')

    # Get substitution data
    url = "https://hektor.webuntis.com/WebUntis/monitor/substitution/data?school=KurfuerstFGym"
    payload = {"formatName":"Vertr_Lehrer_heute","schoolName":"KurfuerstFGym","date":date.replace("-", ""),"dateOffset":0,"strikethrough":True,"mergeBlocks":True,"showOnlyFutureSub":False,"showBreakSupervisions":False,"showTeacher":True,"showClass":True,"showHour":True,"showInfo":True,"showRoom":True,"showSubject":True,"groupBy":2,"hideAbsent":True,"departmentIds":[3,2,1,4],"departmentElementType":1,"hideCancelWithSubstitution":False,"hideCancelCausedByEvent":False,"showTime":False,"showSubstText":True,"showAbsentElements":[4,1,2],"showAffectedElements":[],"showUnitTime":False,"showMessages":True,"showStudentgroup":False,"enableSubstitutionFrom":False,"showSubstitutionFrom":0,"showTeacherOnEvent":False,"showAbsentTeacher":True,"strikethroughAbsentTeacher":True,"activityTypeIds":[2,3,4],"showEvent":False,"showCancel":True,"showOnlyCancel":False,"showSubstTypeColor":False,"showExamSupervision":False,"showUnheraldedExams":False}
    response = requests.post(url, json=payload).text
    data_dict = json.loads(response)

    # Last update
    last_update = data_dict["payload"]["lastUpdate"]

    # Date for data
    data_date = data_dict["payload"]["date"]
    data_date = str(data_date)[:4] + "-" + str(data_date)[4:]
    data_date = str(data_date)[:7] + "-" + str(data_date)[7:]

    # Week day
    week_day = data_dict["payload"]["weekDay"]

    # General info
    messages_raw = data_dict["payload"]["messageData"]["messages"]
    messages_cleaned = []
    for message in messages_raw:
        message_cleaned = message["body"].replace("<br>", " ").replace("<b>", "").replace("</b>", "")
        messages_cleaned.append(message_cleaned)

    # Changes
    rows = data_dict["payload"]["rows"]
    unsorted_changes = []
    for row in rows:
        classes = row["data"][1]
        if current_user.klasse in classes:
            cleaned_row = []

            # Hour
            row_hour = html.unescape(row["data"][0].replace(' ', ""))
            if row_hour == "":
                cleaned_row.append("---")
            else:
                cleaned_row.append(row_hour)

            # Subject
            row_subject = html.unescape(row["data"][2])
            if row_subject == "":
                cleaned_row.append("---")
            else:
                cleaned_row.append(row_subject)

            # Room
            row_room = html.unescape(row["data"][3].split(" (")[0].replace('<span class="substMonitorSubstElem">', "").replace('</span>', ""))
            if row_room == "":
                cleaned_row.append("---")
            else:
                cleaned_row.append(row_room)

            # Teacher
            row_teacher = html.unescape(row["data"][4].split(" (")[0].replace('<span class="substMonitorSubstElem">', "").replace('</span>', ""))
            if row_teacher == "":
                cleaned_row.append("---")
            else:
                cleaned_row.append(row_teacher)

            # Info
            row_info = html.unescape(row["data"][5])
            cleaned_row.append(row_info)

            # Text
            row_text = html.unescape(row["data"][6])
            if row_info == "" and row_text == "":
                cleaned_row.append("---")
            else:
                cleaned_row.append(row_text)

            # Canceled / Change
            if "1" in row["cellClasses"]:
                cleaned_row.append("CANCELED")
            else:
                cleaned_row.append("CHANGE")

            # Room change
            if "(" in html.unescape(row["data"][3]):
                cleaned_row.append("CHANGE")
            else:
                cleaned_row.append("NOCHANGE")

            # Teacher change
            if "(" in html.unescape(row["data"][4]):
                cleaned_row.append("CHANGE")
            else:
                cleaned_row.append("NOCHANGE")

            # Append if not duplicate
            if cleaned_row not in unsorted_changes:
                unsorted_changes.append(cleaned_row)

    # Sort changes list
    changes = []
    len_unsortet_changes = len(unsorted_changes)
    first_hour = 999
    first_index = 0
    while not len(changes) == len_unsortet_changes:
        for x, change in enumerate(unsorted_changes):
            hour = int(change[0][:1])
            if hour <= first_hour:
                first_hour = hour
                first_index = x
        changes.append(unsorted_changes[first_index])
        unsorted_changes.pop(first_index)
        first_hour = 999

    return render_template("home.html", user=current_user, messages=messages_cleaned, date=data_date, week_day=week_day, last_update=last_update, changes=changes)

# Settings
@views.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    global alle_klassen
    
    if request.method == 'POST':
        flash('Your settings have been saved!', category='success')
        klasse = request.form.get('klasse')
        showgeneralinfo = request.form.get('showgeneralinfo')
        user = User.query.filter_by(id=current_user.id).first()
        user.klasse = klasse
        if showgeneralinfo == "on":
            user.showinfo = True
        else:
            user.showinfo = False
        db.session.commit()
        
    return render_template("settings.html", user=current_user, alle_klassen=alle_klassen)
    