from flask import (
    Blueprint,
    Flask,
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
from sessions.model import Timetable
from member.model import Member


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


@sessions.route("/classes")
def classes():
    if "username" in session:
        member = Member(session["username"])
        member.getMemberDetails()
        timetable = Timetable(session["username"])
        # get member chosen date
        dateChosen = request.args.get("dateChosen", "")
        maxDate = timetable.getMaxAvailableDate()
        weekNum = timetable.getWeeknumByDateChosen(dateChosen)
        # get member booked class list
        myBookedClassIds = member.getMyBookedGroupSessionsIDs()
        # get expired classes list by weeknum
        ExpireClassID = timetable.getExpiredClasses(weekNum)
        # get dates by weeknum
        dates = timetable.getCorrespondingDates(weekNum)
        # get timetable by weeknum
        timetableByWeekNum = timetable.getGroupSessionsTimetableByWeeknum(weekNum)
        return render_template(
            "classes.html",
            username=session["username"],
            dbcols=timetableByWeekNum["dbcols"],
            dbresult=timetableByWeekNum["result"],
            dateChosen=dateChosen,
            dbresultDate=dates,
            Today=Today,
            maxdate=maxDate,
            BookedClassID=myBookedClassIds,
            ExpireClassID=ExpireClassID,
        )
    else:
        return redirect(url_for("auth.home"))


@sessions.route("/classes/addClasses/process", methods=["POST"])
def addClasse():
    if "username" in session:
        username = session["username"]
        # Get MemberID
        result1 = db_manager.execute_query(
            "SELECT * FROM Member where Member.Email=%s", (username,)
        )
        dbresult1 = result1["result"]
        memberStatus = dbresult1[0][-2]
        if memberStatus != "Inactive":
            MemberID = dbresult1[0][0]
            # the variable is to define where the data come from,and show different content to users or redirect to different pages
            WaitForProcess = request.form["WaitForProcess"]
            # if BookedClassDetails==1 show button link back to my booking page
            BookedClassDetails = request.form["BookedClassDetails"]
            # if WaitForProcess=='1',show members the detailed class info page first with the booking button.
            if WaitForProcess == "1":
                ptsessionbook = request.form["ptsessionbook"]
                # GET classID
                ClassID = request.form["ClassID"]
                result2 = db_manager.execute_query(
                    """
                                select distinct t.ClassID,c.ClassName,concat(tr.Firstname,' ',tr.LastName) as 'Trainer Name',DATE_FORMAT(t.ClassDate,'%d-%b-%Y'),WeekDayTable.WeekDay,t.StartTime,t.EndTime,CONCAT(ClassDate, ' ', StartTime) AS 'DateTime',tr.TrainerID,
                                (c.Capacity-ifnull(RemainTable.TotalBooked,0)) as"TotalRemaining",c.Capacity,c.ClassDescription
                                from Timetable t
                                left join
                                (select ClassID,date_format(ClassDate,'%W') as 'WeekDay' from Timetable) as WeekDayTable
                                on WeekDayTable.ClassID=t.ClassID
                                left join (select b.classID,count(b.MemberID) as"TotalBooked" from Booking b
                                left join Timetable t
                                on b.ClassID=t.ClassID
                                left join ClassType c
                                on c.ClassCode=t.ClassCode
                                group by b.classID) as RemainTable
                                on  RemainTable.classID=t.ClassID
                                left join Booking b
                                on b.ClassID=t.ClassID
                                left join ClassType c
                                on c.ClassCode=t.ClassCode
                                left join Trainer tr
                                on tr.TrainerID=t.TrainerID
                                where t.ClassID=%s
                                """,
                    (ClassID,),
                )
                dbresultClassInfo = result2["result"]
                # Validation
                # check if the class has been booked.If yes,disable the book button
                result3 = db_manager.execute_query(
                    """select ClassID from Booking
                                where MemberID=%s""",
                    (MemberID,),
                )
                BookingValidationDB = result3["result"]
                BookingValidation = []
                for x in BookingValidationDB:
                    for y in x:
                        y = str(y)
                        BookingValidation.append(y)
                now = datetime.now()
                ClassDateTime = datetime.strptime(
                    dbresultClassInfo[0][7], "%Y-%m-%d %H:%M:%S"
                )
                if ClassDateTime < now:
                    DisableBookButton = "Yes"
                    flash("Lessons that have already occurred cannot be booked.")
                else:
                    DisableBookButton = "No"
                return render_template(
                    "ClassBook.html",
                    section="#DisplayFirst",
                    dbresultClassInfo=dbresultClassInfo,
                    ClassID=ClassID,
                    BookingValidation=BookingValidation,
                    username=username,
                    BookedClassDetails=BookedClassDetails,
                    DisableBookButton=DisableBookButton,
                    ptsessionbook=ptsessionbook,
                )
            elif WaitForProcess == "0":
                ClassID = request.form["ClassID"]
                # get related class info for the new class need to be added.
                result4 = db_manager.execute_query(
                    """
                            select t.ClassID,t.ClassDate,t.StartTime,c.ClassName from Timetable t
                            left join ClassType c
                            on c.Classcode=t.ClassCode
                            where t.ClassID=%s
                            """,
                    (ClassID,),
                )
                dbresultClassTobeBooked = result4["result"]
                ClassDateTobeBooked = dbresultClassTobeBooked[0][1]
                ClassTimeTobeBooked = dbresultClassTobeBooked[0][2]
                # validation for same time same date booking.Prevent double booking.
                result5 = db_manager.execute_query(
                    """
                            select t.ClassID,c.ClassName,t.ClassDate,t.StartTime,t.EndTime,DATE_FORMAT(t.ClassDate,'%d-%b-%Y') from Booking b
                            left join Timetable t
                            on b.ClassID=t.ClassID
                            left join ClassType c
                            on c.ClassCode=t.ClassCode
                            left join Member m
                            on m.MemberID=b.MemberID
                            where b.MemberID=%s
                            and t.ClassDate=%s
                            and t.StartTime=%s
                            order by t.ClassDate;
                            """,
                    (MemberID, ClassDateTobeBooked, ClassTimeTobeBooked),
                )
                dbresultValidation = result5["result"]
                # if dbresult is empty means there is no classes booked in this specific datetime
                if dbresultValidation == []:
                    # then book the new class in
                    print("start executing")
                    db_manager.execute_query(
                        "insert into Booking (MemberID,ClassID,IsPaid,BookingStatus) values(%s,%s,'0','Current')",
                        (MemberID, ClassID),
                        commit=True,
                    )
                    print("finish executing")
                    # After the course reservation is successful, redirect the user to the "My Reservations" page which displays
                    # the latest reservation information.
                    sql = """select ClassDate from Timetable
                            where ClassID=%s"""
                    result6 = db_manager.execute_query(sql, (ClassID,))
                    ClassDateDB = result6["result"]
                    ClassDate = ClassDateDB[0][0].strftime("%Y-%m-%d")
                    # NOTICE INSERT
                    result7 = db_manager.execute_query(
                        "SELECT ClassCode from Timetable where ClassID=%s", (ClassID,)
                    )
                    dbClassCode = result7["result"]
                    now = datetime.now()
                    if dbClassCode[0][0] != 1:
                        db_manager.execute_query(
                            "INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s, 'ClassBooked', 'You have booked a class successfully!')",
                            (MemberID, now),
                            commit=True,
                        )
                    flash("The Class has been added to your list!", "successBooked")
                    return redirect(f"/myBooking?dateChosen={ClassDate}")
                else:
                    # flash(f"Fail to add {dbresultClassTobeBooked[0][-1]} to your list because you have already scheduled {dbresultValidation[0][1]} at {dbresultValidation[0][3]} on {dbresultValidation[0][-1]}.","errorbook")
                    flash(
                        f"Fail to add {dbresultClassTobeBooked[0][-1]}! to your list.You have scheduled for another class at same time.",
                        "errorbook",
                    )
                    return redirect(f"/myBooking")

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
        # flash("You have booked a PT session successfully!")

        # Notice add
        dbClassCode = db_manager.execute_query(
            "SELECT ClassCode from Timetable where ClassID=%s", (classID,)
        )["result"]
        now = datetime.now()
        if dbClassCode[0][0] == 1:
            db_manager.execute_query(
                "INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s, 'Deduction', 'You have made a payment with $50')",
                (memberID, now),
                commit=True,
            )
        # Notice add

        flash("PT session has been added to your list!", "successBooked")
        return redirect(url_for("member.myBooking"))
    else:
        flash("payment is fail,try again")
        return redirect(url_for("ptsession"))


@sessions.route("/cancelClass", methods=["POST"])
def cancelClass():
    ClassID = request.form["ClassID"]
    MemberID = request.form["MemberID"]
    # if classDate is less than a week before today. No refund
    sql = """   select t.ClassDate,CONCAT(ClassDate, ' ', StartTime) AS 'DateTime',c.ClassCode,c.ClassName from Timetable t
                left join ClassType c
                on c.Classcode=t.ClassCode
                where t.ClassID=%s"""
    ClassDateDB = db_manager.execute_query(sql, (ClassID,))["result"][0]
    ClassCode = ClassDateDB[-2]
    ClassDate = ClassDateDB[0].strftime("%Y-%m-%d")
    ClassDateTime = datetime.strptime(ClassDateDB[1], "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    time_delta = ClassDateTime - now
    if time_delta.days < 0:
        flash(
            f"Sorry!{ClassDateDB[-1]} scheduled for {ClassDateDB[0]} cannot be cancelled as the course has already taken place!",
            "error",
        )
        return redirect(f"/myBooking?dateChosen={ClassDate}")

    else:
        # if > 7days,both pt session and class can get refund and places released for re-book
        # if < 7 days,only places for classes will be released for re-book
        if time_delta.days > 7 or (time_delta.days <= 7 and ClassCode != 1):
            sql = """DELETE FROM Booking
                    WHERE MemberID = %s AND ClassID = %s """
            db_manager.execute_query(sql, (MemberID, ClassID), commit=True)
            # NOTICE INSERT
            dbClassCode = db_manager.execute_query(
                "SELECT ClassCode from Timetable where ClassID=%s", (ClassID,)
            )["result"]
            if dbClassCode[0][0] != 1:
                db_manager.execute_query(
                    "INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s,'CancelClass', 'You have cancel a class')",
                    (MemberID, now),
                    commit=True,
                )
            else:
                db_manager.execute_query(
                    "INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s,'Refund', 'You have cancelled a PT session and received a refund of $50')",
                    (MemberID, now),
                    commit=True,
                )
            # NOTICE INSERT
            flash("The class has been cancelled successfully!", "successCancelled")
            return redirect("/myBooking")
        else:
            # pt sessions that are cancelled within 7 days members will not get the refund and
            # the place for pt session will not be released.(cant re-book by other members)
            sql = """update Booking set BookingStatus='Cancelled'
                    where ClassID=%s and MemberID=%s"""
            db_manager.execute_query(sql, (ClassID, MemberID), commit=True)
            # NOTICE INSERT
            db_manager.execute_query(
                "INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s,'CancelClass', 'You have successfully canceled the PT session.Cancellation within seven days is non-refundable.')",
                (MemberID, now),
                commit=True,
            )
            # NOTICE INSERT
            flash(
                "You have successfully canceled the PT session, but as the cancellation was made within one week of the session, you will not receive a refund.!",
                "successCancelled",
            )
            return redirect("/myBooking")
