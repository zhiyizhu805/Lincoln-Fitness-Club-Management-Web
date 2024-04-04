from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from datetime import datetime
from datetime import timedelta, date
from database import db_manager
import pytz
from sessions.model import Timetable, NoticeSender, Class
from member.model import Member, Booking
from trainer.model import Trainer


sessions = Blueprint(
    "sessions",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/sessions/static",
    url_prefix="",
)

# Current NZ time
now_nz = datetime.now(pytz.timezone("Pacific/Auckland"))
formatted_now_nz = now_nz.strftime("%Y-%m-%d %H:%M:%S")
Today = date.today()


def getGroupSessions(dateChosen, classCode):
    timetable = Timetable()
    maxDate = timetable.getMaxAvailableDate()
    weekNum = timetable.getWeeknumByDateChosen(dateChosen)
    ExpireClassID = timetable.getExpiredClasses(weekNum)
    dates = timetable.getCorrespondingDates(weekNum)
    if classCode == "ptsession":
        timetableByWeekNum = timetable.getPersonClassTimetableByWeeknum(weekNum)
    else:
        timetableByWeekNum = timetable.getGroupSessionsTimetableByWeeknum(weekNum)
    return {
        "maxDate": maxDate,
        "dates": dates,
        "ExpireClassID": ExpireClassID,
        "timetableByWeekNum": timetableByWeekNum,
    }


def calculateTimedelta(
    classDateTime,
):  # Allowed classDateTime type <class 'str'> in "%Y-%m-%d %H:%M:%S" format.
    formatedClassDateTime = datetime.strptime(
        classDateTime, "%Y-%m-%d %H:%M:%S"
    )  # Convert to type <class 'datetime.datetime'>
    formatedCurrentTime = datetime.strptime(formatted_now_nz, "%Y-%m-%d %H:%M:%S")
    time_delta = (
        formatedClassDateTime - formatedCurrentTime
    )  # <class 'datetime.timedelta'>
    return time_delta


def getDayWeekHelper():
    dayHelper = [1, 2, 3, 4, 5, 6, 7]
    weekDayList = [
        (1, "SUN"),
        (2, "MON"),
        (3, "TUE"),
        (4, "WED"),
        (5, "THU"),
        (6, "FRI"),
        (7, "SAT"),
    ]
    return {
        'dayList':dayHelper,
        'weekDayList':weekDayList
    }

@sessions.route("/classes")
def classes():
    if "username" in session:
        mybooking = Booking(session["userID"])
        myBookedClassIds = mybooking.getMyBookedGroupSessionsIDs()
        dateChosen = request.args.get("dateChosen", "")
        groupSessions = getGroupSessions(dateChosen, "groupclass")
        return render_template(
            "classes.html",
            username=session["username"],
            dbcols=groupSessions["timetableByWeekNum"]["dbcols"],
            dbresult=groupSessions["timetableByWeekNum"]["result"],
            dateChosen=dateChosen,
            dbresultDate=groupSessions["dates"],
            Today=Today,
            maxdate=groupSessions["maxDate"],
            BookedClassID=myBookedClassIds,
            ExpireClassID=groupSessions["ExpireClassID"],
        )
    else:
        dateChosen = request.args.get("dateChosen", "")
        groupSessions = getGroupSessions(dateChosen)
        return render_template(
            "classes.html",
            dbcols=groupSessions["timetableByWeekNum"]["dbcols"],
            dbresult=groupSessions["timetableByWeekNum"]["result"],
            dateChosen=dateChosen,
            dbresultDate=groupSessions["dates"],
            Today=Today,
            maxdate=groupSessions["maxDate"],
            ExpireClassID=groupSessions["ExpireClassID"],
        )


@sessions.route("/classes/addClasses/process", methods=["POST"])
def addClasse():
    if "username" in session:
        username = session["username"]
        member = Member(session["username"])
        member.getMemberDetails()
        timetable = Timetable()
        mybooking = Booking(member.member_id)
        if member.member_status != "Inactive":
            WaitForProcess = request.form["WaitForProcess"]
            BookedClassDetails = request.form["BookedClassDetails"]
            BookingValidation = mybooking.getMyBookedGroupSessionsIDs()
            # if WaitForProcess=='1',show members the detailed class info page first with the booking button.
            if WaitForProcess == "1":
                ptsessionbook = request.form["ptsessionbook"]
                ClassID = request.form["ClassID"]
                chosenClass = Class(ClassID)
                chosenClassDetails = chosenClass.getClassInfoByID()
                weekNum = timetable.getWeeknumByDateChosen(
                    chosenClass.class_datetime.split(" ")[0]
                )
                ExpireClassID = timetable.getExpiredClasses(weekNum)
                return render_template(
                    "ClassBook.html",
                    section="#DisplayFirst",
                    dbresultClassInfo=chosenClassDetails,
                    ClassID=ClassID,
                    BookingValidation=BookingValidation,
                    username=username,
                    BookedClassDetails=BookedClassDetails,
                    ptsessionbook=ptsessionbook,
                    ExpireClassID=ExpireClassID,
                )
            elif WaitForProcess == "0":
                ClassID = request.form["ClassID"]
                chosenClass = Class(ClassID)
                if chosenClass.class_id not in BookingValidation:
                    mybooking.addBookingByID(ClassID)
                    myNoticeSender = NoticeSender(session["userID"], ClassID)
                    myNoticeSender.sendBookingNotice()
                    flash(
                        f"{chosenClass.class_name}({chosenClass.class_datetime}) has been added to your list!",
                        "successBooked",
                    )
                    return redirect(
                        f"/myBooking?dateChosen={chosenClass.class_datetime.split(' ')[0]}"
                    )
            else:
                # If fail adding class.Print error notice.
                return redirect(f"/classes")
        else:
            flash("Sorry! Only active members can book a class.", "error")
            return redirect(url_for("auth.home"))
    else:
        flash("Please login to book a class!", "error")
        return redirect(url_for("auth.home"))


@sessions.route("/ptCalendar")
def ptCalendar():
    if "username" in session:
        mybooking = Booking(session["userID"])
        myBookedClassIds = mybooking.getMyBookedGroupSessionsIDs()
        dateChosen = request.args.get("dateChosen", "")
        groupSessions = getGroupSessions(dateChosen, "ptsession")
        return render_template(
            "PTcalendar.html",
            username=session["username"],
            dbcols=groupSessions["timetableByWeekNum"]["dbcols"],
            dbresult=groupSessions["timetableByWeekNum"]["result"],
            dateChosen=dateChosen,
            dbresultDate=groupSessions["dates"],
            Today=Today,
            maxdate=groupSessions["maxDate"],
            BookedClassID=myBookedClassIds,
            ExpireClassID=groupSessions["ExpireClassID"],
        )
    else:
        dateChosen = request.args.get("dateChosen", "")
        groupSessions = getGroupSessions(dateChosen)
        return render_template(
            "PTcalendar.html",
            dbcols=groupSessions["timetableByWeekNum"]["dbcols"],
            dbresult=groupSessions["timetableByWeekNum"]["result"],
            dateChosen=dateChosen,
            dbresultDate=groupSessions["dates"],
            Today=Today,
            maxdate=groupSessions["maxDate"],
            ExpireClassID=groupSessions["ExpireClassID"],
        )


@sessions.route("/ptsession")
def ptsession():
    if "username" in session:
        username = session["username"]
        trainer = Trainer(session["username"])
        trainerStatus = trainer.getTrainerStatus()
        trainerList = trainer.getTrainerList()
        timetableList = trainer.getTrainerTablelist()
        weekDayHelper = getDayWeekHelper()
        existedSessionList = trainer.getExistedSessionDate()
        return render_template(
            "ptSession.html",
            username=username,
            trainerList=trainerList,
            timetableList=timetableList,
            weekDayList=weekDayHelper['weekDayList'],
            dayHelper=weekDayHelper['dayList'],
            existedSessionList=existedSessionList,
            memberStatus=trainerStatus,
        )

    else:
        trainer = Trainer()
        trainerList = trainer.getTrainerList()
        timetableList = trainer.getTrainerTablelist()
        weekDayHelper = getDayWeekHelper()
        return render_template(
            "ptSession.html",
            username="",
            trainerList=trainerList,
            timetableList=timetableList,
            weekDayList=weekDayHelper['weekDayList'],
            dayHelper=weekDayHelper['dayList'],
        )


# book session function
@sessions.route("/bookSession", methods=["POST"])
def bookSession():
    mybooking = Booking(session["username"])
    classID = request.form["classID"]
    bankaccount = request.form["bankaccount"]
    expireMonth = request.form["expireMonth"]
    expireYear = request.form["expireYear"]
    bankcvc = request.form["bankcvc"]
    isCardValid = False
    if (int(expireYear) == now_nz.year and int(expireMonth) >= now_nz.month) or int(
        expireYear
    ) > now_nz.year:
        isCardValid = True
    if len(bankaccount) == 16 and len(bankcvc) > 2 and isCardValid:
        mybooking.addPTsessionByID(classID)
        myNoticeSender = NoticeSender(session["userID"], classID)
        myNoticeSender.sendBookingNotice()
        flash("PT session has been added to your list!", "successBooked")
        return redirect(url_for("member.myBooking"))
    else:
        flash("payment is fail,try again")
        return redirect(url_for("ptsession"))


@sessions.route("/cancelClass", methods=["POST"])
def cancelClass():
    ClassID = request.form["ClassID"]
    MemberID = request.form["MemberID"]
    myNoticeSender = NoticeSender(session["userID"], ClassID)
    chosenClass = Class(ClassID)
    mybooking = Booking(MemberID)
    time_delta = calculateTimedelta(chosenClass.class_datetime)
    if time_delta.days > 7 or (time_delta.days <= 7 and chosenClass.class_code != 1):
        mybooking.cancelBookingReleaseSpace(ClassID)
        myNoticeSender.sendCancelBookingNotice()
        flash(
            f"{chosenClass.class_name}({chosenClass.class_datetime}) has been cancelled successfully!",
            "successCancelled",
        )
        if chosenClass.class_code == 1:
            myNoticeSender.sendRefundNotice()
        return redirect(
            f"/myBooking?dateChosen={chosenClass.class_datetime.split(' ')[0]}"
        )
    else:
        # pt sessions that are cancelled within 7 days members will not get the refund.
        mybooking.cancelBookingReleaseSpace(ClassID)
        myNoticeSender.sendCancelBookingNotice()
        myNoticeSender.sendNoRefundNotice()
        flash(
            "Your PT session has been successfully cancelled. Please note that you are not eligible for a refund as the cancellation occurred within one week of the session.",
            "successCancelled",
        )
        return redirect(
            f"/myBooking?dateChosen={chosenClass.class_datetime.split(' ')[0]}"
        )
