from flask import (Blueprint,Flask, flash, redirect, render_template,
                   request, session, url_for)



traniner = Blueprint("traniner",__name__,template_folder="templates",static_folder="static",static_url_path='/traniner/static', url_prefix='')


#trainer interface
@traniner.route("/trainer/myProfile")
def trainer():
    if "username" in session:
        username = session["username"]
        cur=getCursor()
        sql_trainer = """SELECT * FROM Trainer WHERE Email = %s """
        para= (username,)
        cur.execute(sql_trainer,para)
        trainer = cur.fetchall()
        trainer_id = trainer[0][0]
        month = request.args.get('month')
        # only show selected month data
        if month :
            sql_timetable = """SELECT ClassType.ClassName, Timetable.ClassDate,Timetable.StartTime,Timetable.EndTime
                            FROM Timetable
                            INNER JOIN ClassType ON ClassType.ClassCode = Timetable.ClassCode
                             WHERE TrainerID = %s
                             AND  MONTH(Timetable.ClassDate) = %s
                             ORDER BY Timetable.ClassDate;  """
            cur.execute(sql_timetable,(trainer_id, month))
        else:
            sql_timetable = """SELECT ClassType.ClassName, Timetable.ClassDate,Timetable.StartTime,Timetable.EndTime
                            FROM Timetable
                            INNER JOIN ClassType ON ClassType.ClassCode = Timetable.ClassCode
                             WHERE TrainerID = %s
                             ORDER BY Timetable.ClassDate;  """
            cur.execute(sql_timetable,(trainer_id,))
        timetable = cur.fetchall()
        months = []
        for rows in timetable:
            date = rows[1]
            datestring = str(date)
            dateStringList = datestring.split('-')
            months.append(dateStringList[1])
        filteredMonths = list(dict.fromkeys(months))

        return render_template("trainer.html",username=username, trainer=trainer, timetable=timetable, filteredMonths=filteredMonths, trainer_id=trainer_id)
    else:
        return redirect(url_for("trainerLogin"))

#trainer login
@traniner.route("/trainer",methods=["POST", "GET"])
def trainerLogin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        error = ""
        cur=getCursor()
        sql = """SELECT * FROM Trainer WHERE Email = %s AND TrainerPassword = %s """
        cur.execute(sql, (email,password))
        trainer = cur.fetchall()
        if len(trainer) == 1:
            trainerID = trainer[0][0]
            session["userID"] = trainerID
            session["username"] = email
            if trainer[0][11] == "Active":
                return redirect(url_for("trainer"))
            else:
                flash("Your profile has been archived.Please contact the gym manager!")
                return render_template("trainerLogin.html")
        else:
            flash("Invalid email or password!", "error")
            return render_template("trainerLogin.html", error=error)
    return render_template("trainerLogin.html")


# trainer update
@traniner.route("/trainerUpdate",methods=["POST"])
def trainerUpdate():
    phone = request.form.get("phone")
    contactName = request.form.get("contactName")
    contactPhone = request.form.get("contactPhone")
    cur=getCursor()
    sql = """UPDATE Trainer SET Phone = %s, EmergencyContactName = %s, EmergencyContactNumber=%s """
    cur.execute(sql, (phone,contactName,contactPhone),commit=True)
    flash("Update successful!")
    return redirect(url_for("trainer"))


# trainer password reset function
@traniner.route("/trainerPWReset", methods=["POST"])
def trainer_password_reset():
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")
    email = session["username"]
    cur=getCursor()
    # new password has to be at leat 8 characters
    if len(password)>7 and (password==confirmPassword):
        sql = """UPDATE Trainer SET TrainerPassword = %s WHERE Email = %s """
        cur.execute(sql, (password, email),commit=True)
        flash("Password reset succeed, please login with new password!")
        return render_template("trainerLogin.html")
    else:
        flash("Error! Please reset again!")
        return redirect(url_for("trainer"))


# trainer/myTrainee section
@traniner.route("/trainer/myTrainee")
def myTrainee():
    if "username" in session:
        username = session["username"]
        cur=getCursor()
        cur.execute("SELECT Trainer.TrainerID FROM Trainer where Trainer.Email=%s",(username,))
        TrainerID = cur.fetchone()
        # the SQL query has returned a tuple, the TrainerID is extracted from the tuple below
        TrainerID =TrainerID[0]
        cur=getCursor()
        #the mySQL query below identifies all PT session bookings for the logged in trainer that occur today or in the future
        cur.execute("SELECT Member.MemberID, Member.FirstName, Member.LastName, Member.DateOfBirth, Member.MemberNotes, Booking.ClassID, Timetable.TrainerID, Timetable.ClassCode, Timetable.ClassDate \
        FROM Member \
        JOIN Booking ON Member.MemberID=Booking.MemberID \
        JOIN Timetable ON Booking.ClassID=Timetable.ClassID \
        WHERE (Timetable.ClassCode=1 AND Timetable.TrainerID=%s AND Timetable.ClassDate >=CURDATE()) ORDER BY Member.LastName, Member.FirstName, Member.MemberID, Timetable.ClassDate;", (TrainerID,))
        TraineesDetails = cur.fetchall()
        #convert TraineesDetails from list of tuples to list of lists so DateOfBirth can be replaced with trainee's age
        List_TraineesDetails = [list(ele) for i,ele in enumerate(TraineesDetails)]
        #the loop below uses each trainee's date of birth to calculate their age, then replaces their DateOfBirth with their age
        for x in List_TraineesDetails:
            DateOfBirth=(x[3])
            today=date.today()
            age = relativedelta(today, DateOfBirth).years
            x[3]=age
        #convert lists of lists back into a list of tuples
        tuples=[]
        for x in List_TraineesDetails:
            tuples.append(tuple(x))
        TraineesDetails=tuples
        return render_template("myTrainee.html",TraineesDetails=TraineesDetails, username=username)
    else:
        return redirect(url_for("trainerLogin"))