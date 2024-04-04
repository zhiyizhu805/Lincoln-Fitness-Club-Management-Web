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
from sessions.model import Timetable,NoticeSender,Class
from member.model import Member,Booking


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

def getGroupSessions(dateChosen):
    timetable = Timetable()
    maxDate = timetable.getMaxAvailableDate()
    weekNum = timetable.getWeeknumByDateChosen(dateChosen)
    ExpireClassID = timetable.getExpiredClasses(weekNum)
    dates = timetable.getCorrespondingDates(weekNum)
    timetableByWeekNum = timetable.getGroupSessionsTimetableByWeeknum(weekNum)
    return{
       'maxDate': maxDate,
       'dates':dates,
       'ExpireClassID':ExpireClassID,
       'timetableByWeekNum':timetableByWeekNum
    }
    
def calculateTimedelta(classDateTime):   # Allowed classDateTime type <class 'str'> in "%Y-%m-%d %H:%M:%S" format.
    formatedClassDateTime = datetime.strptime(classDateTime, "%Y-%m-%d %H:%M:%S")  # Convert to type <class 'datetime.datetime'>
    formatedCurrentTime = datetime.strptime(formatted_now_nz, "%Y-%m-%d %H:%M:%S") 
    time_delta = formatedClassDateTime - formatedCurrentTime  #<class 'datetime.timedelta'>
    print('time_delta',type(time_delta))
    return time_delta

@sessions.route("/classes")
def classes():
    if "username" in session:
        mybooking = Booking(session["userID"])
        myBookedClassIds = mybooking.getMyBookedGroupSessionsIDs()
        dateChosen = request.args.get("dateChosen", "")
        groupSessions = getGroupSessions(dateChosen)
        return render_template(
            "classes.html",
            username=session["username"],
            dbcols=groupSessions['timetableByWeekNum']["dbcols"],
            dbresult=groupSessions['timetableByWeekNum']["result"],
            dateChosen=dateChosen,
            dbresultDate=groupSessions['dates'],
            Today=Today,
            maxdate=groupSessions['maxDate'],
            BookedClassID=myBookedClassIds,
            ExpireClassID=groupSessions['ExpireClassID'],
        )
    else:
        dateChosen = request.args.get("dateChosen", "")
        groupSessions = getGroupSessions(dateChosen)
        return render_template(
            "classes.html",
            dbcols=groupSessions['timetableByWeekNum']["dbcols"],
            dbresult=groupSessions['timetableByWeekNum']["result"],
            dateChosen=dateChosen,
            dbresultDate=groupSessions['dates'],
            Today=Today,
            maxdate=groupSessions['maxDate'],
            ExpireClassID=groupSessions['ExpireClassID'],
        )
    



@sessions.route("/classes/addClasses/process", methods=["POST"])
def addClasse():
    if "username" in session:
        username = session["username"]
        member = Member(session["username"])
        member.getMemberDetails()
        # timetable = Timetable()
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
                return render_template(
                    "ClassBook.html",
                    section="#DisplayFirst",
                    dbresultClassInfo=chosenClassDetails,
                    ClassID=ClassID,
                    BookingValidation=BookingValidation,
                    username=username,
                    BookedClassDetails=BookedClassDetails,
                    ptsessionbook=ptsessionbook,
                )
            elif WaitForProcess == "0":
                ClassID = request.form["ClassID"]
                chosenClass = Class(ClassID)
                if chosenClass.class_id not in BookingValidation:
                    mybooking.addBookingByID(ClassID)
                    myNoticeSender = NoticeSender(session["userID"],ClassID)
                    myNoticeSender.sendBookingNotice()
                    flash(f"{chosenClass.class_name}({chosenClass.class_datetime}) has been added to your list!", "successBooked")
                    return redirect(f"/myBooking?dateChosen={chosenClass.class_datetime.split(' ')[0]}")
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
        username = session["username"]
        userID = session["userID"]
    else:
        username = ""
        userID = ""
    # get booked class info
    currentUserClassInfo = db_manager.execute_query(
        "SELECT ClassID FROM Booking WHERE MemberID = %s", (userID,)
    )["result"]
    BookedClassID = [str(x[0]) for x in currentUserClassInfo]
    # get user input date info
    dateChosen = request.args.get("dateChosen", "")
    # if user input is empty,show current date class schedule
    # min date(today)
    Today = date.today()
    # max date
    three_weeks = timedelta(weeks=3)
    maxdate = Today + three_weeks
    if dateChosen == "":
        dateChosen = Today
        WeekNum = int(Today.strftime("%W"))
    else:
        dateChosen = datetime.strptime(dateChosen, "%Y-%m-%d").date()
        WeekNum = int(dateChosen.strftime("%W"))
    # get expired class info
    expiredClassInfo = db_manager.execute_query(
        "SELECT * FROM Timetable WHERE CONCAT(ClassDate, ' ', StartTime) < %s AND WEEKOFYEAR(ClassDate) = %s",
        (formatted_now_nz, WeekNum),
    )["result"]
    ExpireClassID = [str(x[0]) for x in expiredClassInfo]
    WeekNum = f"{WeekNum}%"
    # get date
    dbresultDate = db_manager.execute_query(
        """SELECT DISTINCT
                    'Date' AS StartTime,
                    DATE_FORMAT(MAX(CASE WHEN WeekDayTable.WeekDay = 'Monday' THEN WeekDayTable.ClassDate ELSE '' END), '%d-%b-%Y') AS Monday,
                    DATE_FORMAT(MAX(CASE WHEN WeekDayTable.WeekDay = 'Tuesday' THEN WeekDayTable.ClassDate ELSE '' END), '%d-%b-%Y') AS Tuesday,
                    DATE_FORMAT(MAX(CASE WHEN WeekDayTable.WeekDay = 'Wednesday' THEN WeekDayTable.ClassDate ELSE '' END), '%d-%b-%Y') AS Wednesday,
                    DATE_FORMAT(MAX(CASE WHEN WeekDayTable.WeekDay = 'Thursday' THEN WeekDayTable.ClassDate ELSE '' END), '%d-%b-%Y') AS Thursday,
                    DATE_FORMAT(MAX(CASE WHEN WeekDayTable.WeekDay = 'Friday' THEN WeekDayTable.ClassDate ELSE '' END), '%d-%b-%Y') AS Friday,
                    DATE_FORMAT(MAX(CASE WHEN WeekDayTable.WeekDay = 'Saturday' THEN WeekDayTable.ClassDate ELSE '' END), '%d-%b-%Y') AS Saturday,
                    DATE_FORMAT(MAX(CASE WHEN WeekDayTable.WeekDay = 'Sunday' THEN WeekDayTable.ClassDate ELSE '' END), '%d-%b-%Y') AS Sunday
                    FROM (SELECT ClassID,ClassDate, DATE_FORMAT(ClassDate, '%W') AS 'WeekDay' FROM Timetable) AS WeekDayTable
                    WHERE WEEKOFYEAR(ClassDate)=%s;
                """,
        (WeekNum,),
    )["result"][0]
    result = db_manager.execute_query(
        """
                SELECT Timetable.StartTime, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
                FROM
                (SELECT DISTINCT StartTime FROM Timetable) AS Timetable
                LEFT JOIN
                (SELECT
                t.StartTime,
                GROUP_CONCAT(distinct CASE WHEN WeekDayTable.WeekDay = 'Monday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',tr.trainerID,',',t.ClassDate,',',t.StartTime,',',t.EndTime,',',dayofweek(t.ClassDate),',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END SEPARATOR ';') AS Monday,
                GROUP_CONCAT(distinct CASE WHEN WeekDayTable.WeekDay = 'Tuesday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',tr.trainerID,',',t.ClassDate,',',t.StartTime,',',t.EndTime,',',dayofweek(t.ClassDate),',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END SEPARATOR ';') AS Tuesday,
                GROUP_CONCAT(distinct CASE WHEN WeekDayTable.WeekDay = 'Wednesday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',tr.trainerID,',',t.ClassDate,',',t.StartTime,',',t.EndTime,',',dayofweek(t.ClassDate),',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END SEPARATOR ';') AS Wednesday,
                GROUP_CONCAT(distinct CASE WHEN WeekDayTable.WeekDay = 'Thursday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',tr.trainerID,',',t.ClassDate,',',t.StartTime,',',t.EndTime,',',dayofweek(t.ClassDate),',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END SEPARATOR ';') AS Thursday,
                GROUP_CONCAT(distinct CASE WHEN WeekDayTable.WeekDay = 'Friday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',tr.trainerID,',',t.ClassDate,',',t.StartTime,',',t.EndTime,',',dayofweek(t.ClassDate),',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END SEPARATOR ';') AS Friday,
                GROUP_CONCAT(distinct CASE WHEN WeekDayTable.WeekDay = 'Saturday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',tr.trainerID,',',t.ClassDate,',',t.StartTime,',',t.EndTime,',',dayofweek(t.ClassDate),',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END SEPARATOR ';') AS Saturday,
                GROUP_CONCAT(distinct CASE WHEN WeekDayTable.WeekDay = 'Sunday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',tr.trainerID,',',t.ClassDate,',',t.StartTime,',',t.EndTime,',',dayofweek(t.ClassDate),',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END SEPARATOR ';') AS Sunday
                FROM Timetable t
                LEFT JOIN (SELECT ClassID,StartTime, DATE_FORMAT(ClassDate, '%W') AS 'WeekDay' FROM Timetable) AS WeekDayTable
                ON WeekDayTable.ClassID = t.ClassID
                LEFT JOIN (SELECT b.classID, COUNT(b.MemberID) AS"TotalBooked" FROM Booking b
                LEFT JOIN Timetable t
                ON b.ClassID = t.ClassID
                LEFT JOIN ClassType c
                ON c.ClassCode = t.ClassCode
                GROUP BY b.classID) AS RemainTable
                ON RemainTable.classID = t.ClassID
                LEFT JOIN Booking b
                ON b.ClassID = t.ClassID
                LEFT JOIN ClassType c
                ON c.ClassCode = t.ClassCode
                LEFT JOIN Trainer tr
                ON tr.TrainerID = t.TrainerID
                WHERE WEEKOFYEAR(t.ClassDate) Like %s
                and c.ClassCode=1
                GROUP BY t.StartTime) AS Table2
                ON Timetable.StartTime = Table2.StartTime
                ORDER BY Timetable.StartTime;
                                    """,
        (WeekNum,),
    )
    # get data for database and process
    dbcols = result["dbcols"]
    dbresult = result["result"]
    listdb = []
    listlayer = []
    listclass = []
    listIndividualClassInfo = []
    for x in dbresult:
        for y in x:
            if type(y) != str or y == None:
                listlayer.append(y)
            else:
                if ";" in y:
                    for individualClassInfo in y.split(";"):
                        for (
                            eachElementOfIndividualClassInfo
                        ) in individualClassInfo.split(","):
                            listIndividualClassInfo.append(
                                eachElementOfIndividualClassInfo
                            )
                        listclass.append(listIndividualClassInfo)
                        listIndividualClassInfo = []
                    listlayer.append(listclass)
                    listclass = []
                else:
                    for b in y.split(","):
                        listclass.append(b)
                    listlayer.append(listclass)
                    listclass = []

        listdb.append(listlayer)
        listclass = []
        listlayer = []
    return render_template(
        "PTcalendar.html",
        username=username,
        dbcols=dbcols,
        dbresult=listdb,
        dateChosen=dateChosen,
        dbresultDate=dbresultDate,
        Today=Today,
        maxdate=maxdate,
        BookedClassID=BookedClassID,
        ExpireClassID=ExpireClassID,
    )


@sessions.route("/ptsession")
def ptsession():
    if "username" in session:
        userID = session["userID"]
        memberIDs = db_manager.execute_query("SELECT * FROM role WHERE role='member'")[
            "result"
        ]
        memberIDList = []
        for memberID in memberIDs:
            memberIDList.append(memberID[0])
        if userID in memberIDList:
            username = session["username"]
            member_result = db_manager.execute_query(
                "SELECT MemberStatus FROM Member WHERE Email=%s", (username,)
            )["result"]
            memberStatus = member_result[0][0]
            sql_trainer = "SELECT TrainerID, FirstName, LastName FROM Trainer WHERE TrainerStatus='Active' ORDER BY FirstName "
            trainerList = db_manager.execute_query(sql_trainer)["result"]

            sql_timetable = """SELECT Timetable.TrainerID, Timetable.ClassDate, Timetable.StartTime, Timetable.EndTime, DAYOFWEEK(Timetable.ClassDate), Timetable.ClassID
                            FROM Timetable
                            WHERE  Timetable.ClassCode = 1 AND DATE(Timetable.ClassDate) > %s
                            ORDER BY Timetable.ClassDate

            """
            timetableList = db_manager.execute_query(
                sql_timetable, (datetime.today(),)
            )["result"]
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
            sql_existed_session = """SELECT Timetable.ClassID, Timetable.ClassCode, Timetable.ClassDate FROM Timetable
                                    INNER JOIN Booking ON Timetable.ClassID = Booking.ClassID
                                    WHERE IsPaid=1  AND Timetable.ClassCode=1 AND DATE(Timetable.ClassDate) > %s """
            existedSessionData = db_manager.execute_query(
                sql_existed_session, (datetime.today(),)
            )["result"]
            existedSessionList = []
            for existedSession in existedSessionData:
                existedSessionList.append(existedSession[0])
            return render_template(
                "ptSession.html",
                username=username,
                trainerList=trainerList,
                timetableList=timetableList,
                weekDayList=weekDayList,
                dayHelper=dayHelper,
                existedSessionList=existedSessionList,
                memberStatus=memberStatus,
            )
        else:
            session.pop("username", None)
            return redirect(url_for("ptsession"))
    else:
        sql_trainer = "SELECT TrainerID, FirstName, LastName FROM Trainer WHERE TrainerStatus='Active' ORDER BY FirstName "

        trainerList = db_manager.execute_query(sql_trainer)["result"]

        sql_timetable = """SELECT Timetable.TrainerID, Timetable.ClassDate, Timetable.StartTime, Timetable.EndTime, DAYOFWEEK(Timetable.ClassDate)
                        FROM Timetable
                        WHERE  Timetable.ClassCode = 1 AND DATE(Timetable.ClassDate) > %s
                        ORDER BY Timetable.ClassDate

        """
        timetableList = db_manager.execute_query(sql_timetable, (datetime.today(),))[
            "result"
        ]
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
        return render_template(
            "ptSession.html",
            username="",
            trainerList=trainerList,
            timetableList=timetableList,
            weekDayList=weekDayList,
            dayHelper=dayHelper,
        )


# book session function
@sessions.route("/bookSession", methods=["POST"])
def bookSession():
    username = session["username"]
    member = db_manager.execute_query(
        "SELECT * FROM Member where Member.Email=%s", (username,)
    )["result"][0]
    memberID = member[0]
    classID = request.form["classID"]
    bankaccount = request.form["bankaccount"]
    expireMonth = request.form["expireMonth"]
    expireYear = request.form["expireYear"]
    bankcvc = request.form["bankcvc"]
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    isCardValid = False
    if (int(expireYear) == currentYear and int(expireMonth) >= currentMonth) or int(
        expireYear
    ) > currentYear:
        isCardValid = True
    if len(bankaccount) == 16 and len(bankcvc) > 2 and isCardValid:

        sql_addBooking = """INSERT INTO Booking(MemberID,ClassID,IsPaid,BookingStatus)
                            VALUES(%s,%s,%s,%s) """
        db_manager.execute_query(
            sql_addBooking, (memberID, classID, 1, "Current"), commit=True
        )
        myNoticeSender = NoticeSender(session["userID"],classID)
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
    myNoticeSender = NoticeSender(session["userID"],ClassID)
    chosenClass = Class(ClassID)
    mybooking = Booking(MemberID)
    time_delta = calculateTimedelta(chosenClass.class_datetime)
    if time_delta.days > 7 or (time_delta.days <= 7 and chosenClass.class_code != 1):
        mybooking.cancelBookingReleaseSpace(ClassID)
        myNoticeSender.sendCancelBookingNotice()
        flash(f"{chosenClass.class_name}({chosenClass.class_datetime}) has been cancelled successfully!", "successCancelled")
        if chosenClass.class_code == 1:
            myNoticeSender.sendRefundNotice()
        return redirect(f"/myBooking?dateChosen={chosenClass.class_datetime.split(' ')[0]}")
    else:
        # pt sessions that are cancelled within 7 days members will not get the refund.
        mybooking.cancelBookingReleaseSpace(ClassID)
        myNoticeSender.sendCancelBookingNotice()
        myNoticeSender.sendNoRefundNotice()
        flash(
            "You have successfully canceled the PT session, but as the cancellation was made within one week of the session, you will not receive a refund.!",
            "successCancelled",
        )
        return redirect(f"/myBooking?dateChosen={chosenClass.class_datetime.split(' ')[0]}")
