from flask import (Blueprint,flash, redirect, render_template,
                   request, session, url_for)
from database import db_manager


auth = Blueprint("auth",__name__,template_folder="templates",static_folder="static",static_url_path='/auth/static', url_prefix='')


@auth.route("/")
def home():
    if "username" in session:
        userID = session["userID"]
        query = "SELECT * FROM role WHERE role='member'"
        memberIDList = []
        memberIDs = db_manager.execute_query(query,)
        for memberID in memberIDs:
            memberIDList.append(memberID[0])
        if userID in memberIDList:
            username = session["username"]
            return render_template("base.html", username=username)
        else:
            session.pop("username", None)
            return redirect(url_for("auth.home"))
    else:
        return render_template("base.html")


@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    error = ""
    # cur=getCursor()
    sql = """SELECT * FROM Member WHERE Email = %s AND MemberPassword = %s """
    # cur.execute(sql, (email,password))
    member = db_manager.execute_query(sql, (email,password))
    if len(member) == 1:
        if member[0][17]=="Archived":
            flash("You are an archived user, please contact gym staff for more information!")
            return render_template("base.html")
        else:
            memberID = member[0][0]
            session["userID"] = memberID
            session["username"] = email
            return redirect(url_for("auth.home"))
    else:
        flash("Invalid user name or password!","error")
        return render_template("base.html", error=error)
    

# public interface logout function
@auth.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("auth.home"))

# public interface password reset function
@auth.route("/resetPassword", methods=["POST"])
def password_reset():
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")
    email = session["username"]
    error = ""
    # new password has to be at leat 8 characters
    if len(password)>7 and (password==confirmPassword):
        sql = """UPDATE Member SET MemberPassword = %s WHERE Email = %s """
        db_manager.execute_query(sql, (password, email))
        flash("Password reset succeed!Please login with new password!","success")
        session.pop("username", None)
        return redirect(url_for("auth.home"))
    else:
        flash("Error! Please reset again!","error")
        return redirect(url_for("auth.home"))

# admin login function
@auth.route("/admin")
def adminLogin_get():
    return render_template("adminLogin.html")

@auth.route("/admin/login", methods=["POST"])
def adminLogin_post():
    username = request.form.get("username")
    password = request.form.get("password")
    error = ""
    sql = """SELECT * FROM Admin WHERE Username = %s AND UserPassword = %s """
    user = db_manager.execute_query(sql, (username,password))
    if len(user) == 1:
        userID = user[0][0]
        session["userID"] = userID
        session["username"] = username
        return redirect(url_for("admin"))
    else:
        flash("Invalid user name or password!","error")
        return render_template("adminLogin.html")

@auth.route("/admin/logout")
def adminLogout():
    session.pop("username", None)
    return redirect(url_for("adminLogin_get"))

#trainer login
@auth.route("/trainer",methods=["POST", "GET"])
def trainerLogin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        error = ""
        sql = """SELECT * FROM Trainer WHERE Email = %s AND TrainerPassword = %s """
        trainer = db_manager.execute_query(sql, (email,password))
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

# trainer password reset function
@auth.route("/trainerPWReset", methods=["POST"])
def trainer_password_reset():
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")
    email = session["username"]
    # new password has to be at leat 8 characters
    if len(password)>7 and (password==confirmPassword):
        sql = """UPDATE Trainer SET TrainerPassword = %s WHERE Email = %s """
        db_manager.execute_query(sql, (password, email))
        flash("Password reset succeed, please login with new password!")
        return render_template("trainerLogin.html")
    else:
        flash("Error! Please reset again!")
        return redirect(url_for("trainer"))