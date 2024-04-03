from flask import (Blueprint, flash, redirect, render_template,
                   request, session, url_for)
from database import db_manager
from datetime import  date,datetime
from dateutil.relativedelta import relativedelta
import pytz 

member = Blueprint("member",__name__,template_folder="templates",static_folder="static",static_url_path='/member/static', url_prefix='')

# Current NZ time
now_nz = datetime.now(pytz.timezone('Pacific/Auckland'))
formatted_now_nz = now_nz.strftime("%Y-%m-%d %H:%M:%S")

@member.route("/membership/mySubscription")
def mySubscription():
    if "username" in session:
        username = session["username"]
        select_result_MemberInfo = db_manager.execute_query("SELECT * FROM Member where Member.Email=%s",(username,))['result'][0]
        # select_result_MemberInfo = cur.fetchone()
        MemberID=select_result_MemberInfo[0]
        AutoFee=select_result_MemberInfo[-6]
        MemberStatus=select_result_MemberInfo[-2]
        select_result_SubscriptionInfo = db_manager.execute_query("""select distinct max(SubscriptionEndDate) from Subscription
                    where memberID=%s""",(MemberID,))['result'][0]
        ExpiryDate=select_result_SubscriptionInfo[0]
        Today=date.today()
        if ExpiryDate!=None:
            if ExpiryDate>=Today and AutoFee=='No':
                daystoExpiry=abs(ExpiryDate-Today).days
                validperiodNotice=f" Your subscription status will become inactive on {ExpiryDate}."
                daysRemain=f"Your current subscription still has a validity of {daystoExpiry} days and you will not be auto charged for the next month"
                return render_template("mySubscription.html",
                                username=username,
                                select_result=select_result_MemberInfo ,
                                validperiodNotice=validperiodNotice,
                                daysRemain=daysRemain)

            elif ExpiryDate>=Today and AutoFee=='Yes':
                DeductionNotice=f"You subscription will be auto renewed on {ExpiryDate}."
                return render_template("mySubscription.html",
                            username=username,
                            select_result=select_result_MemberInfo ,
                            DeductionNotice=DeductionNotice)
            elif ExpiryDate<Today:
                ExpiryNotice=f" Your account has expired on {ExpiryDate}."
                return render_template("mySubscription.html",
                            username=username,
                            select_result=select_result_MemberInfo ,
                            ExpiryNotice=ExpiryNotice,ExpiryDate=ExpiryDate,
                            MemberStatus=MemberStatus)
        else:
            if MemberStatus=='Inactive':
                flash("You have never activated a subscription before. Please contact the manager to activate your first subscription.","ContactManager")
                return redirect('/membership')


    else:
        return redirect(url_for("auth.home"))



@member.route("/membership/CancelSubscription",methods=['POST'])
def CancelSubscription():
    if "username" in session:
        username = session["username"]
        MemberID=request.form["MemberID"]
        TaskToDo=request.form['TaskToDo']
        dbrsultSubscriptionInfo=db_manager.execute_query( """select * from Member
                        where MemberID=%s """,(MemberID,))['result']
        select_result_SubscriptionInfo=db_manager.execute_query("""select distinct max(SubscriptionEndDate) from Subscription
                where MemberID=%s""",(MemberID,))['result'][0]
        ExpiryDate=select_result_SubscriptionInfo[0]
        Today=date.today()
        delta = ExpiryDate - Today

        if TaskToDo=='Deactivate':
            db_manager.execute_query( """UPDATE Member SET AuthorityOnCollectingFees ="No"
                        where MemberID=%s """,(MemberID,),commit=True)
            flash("You have successfully cancelled the Auto-renew for your subscription!","cancelSubSuccess")

        elif TaskToDo=='Reactivate':
            db_manager.execute_query( """UPDATE Member SET MemberStatus = 'Active', AuthorityOnCollectingFees ="Yes"
                            where MemberID=%s """,(MemberID,),commit=True)
            if ExpiryDate<Today:
                # get new expiry date
                NewExpiryDate = Today + relativedelta(months=1)
                #insert new subscription data into db
                db_manager.execute_query( """INSERT INTO Subscription (MemberID, SubscriptionStartDate, SubscriptionEndDate, PaymentAmount, IsPaid)
                                VALUES(%s,%s,%s,100,1)""",(MemberID,Today,NewExpiryDate),commit=True)

            flash("You have successfully reactivated the auto-renew for your subscription!","ReActSuccess")

        return redirect("/membership/mySubscription")
    else:
        return render_template("membership.html")
    
    
    
@member.route("/membership")
def membership():
    if "username" in session:
        username = session["username"]
        return render_template("membership.html", username=username)
    else:
        return render_template("membership.html")
#My profile section
@member.route("/myProfile")
def myProfile():
    if "username" in session:
        username = session["username"]
        select_result = db_manager.execute_query("SELECT * FROM Member where Member.Email=%s",(username,))['result'][0]
        return render_template("myProfile.html", username=username, select_result=select_result)
    else:
        return redirect(url_for("auth.home"))

@member.route("/myProfile/edit")
def myProfileEditGet():
    if "username" in session:
        username = session["username"]
        select_result = db_manager.execute_query("SELECT * FROM Member where Member.Email=%s",(username,))['result'][0]
        return render_template("myProfileEdit.html", username=username, select_result=select_result)
    else:
        return redirect(url_for("auth.home"))

#My profile edit section
@member.route("/myProfileEditPOST",methods=["POST"])
def myProfileEdit():
    if "username" in session:
        username = session["username"]
        memberID=request.form['memberID']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']
        phone=request.form['phone']
        PhysicalAddress=request.form['physicaladdress']
        DOB=request.form['birthdate']
        EmergencyName=request.form['emergencycontactname']
        EmergencyNumber=request.form['emergencycontactnumber']
        Mconditions=request.form['medicalconditions']
        ReceivingNotifications=request.form['receivingnotifications']
        autoFee=request.form['authorityoncollectingfees']
        BankName=request.form['bankname']
        BankAccountHolderName=request.form['bankaccountholdername']
        BankAccountNumber=request.form['bankaccountnumber']
        MemberNotes=request.form['notes']
        sql="""update Member set FirstName=%s, LastName=%s,Email=%s, PhysicalAddress=%s, Phone=%s, DateOfBirth=%s,
                EmergencyContactName=%s, EmergencyContactNumber=%s, MedicalConditions=%s, ReceivingNotifications=%s,
                AuthorityOnCollectingFees=%s, BankName=%s, BankAccountHolderName=%s, BankAccountNumber=%s ,MemberNotes=%s
                where memberID=%s"""
        db_manager.execute_query(sql,(firstname,lastname,email,PhysicalAddress,phone,DOB,EmergencyName,EmergencyNumber,Mconditions,ReceivingNotifications,autoFee,BankName,BankAccountHolderName,BankAccountNumber,MemberNotes,memberID),commit=True)
        #render the the same member page with same memberID
        result = db_manager.execute_query("select * from Member where MemberID=%s",(memberID,))['result'][0]
        flash("Details have been successfully updated")
        return redirect(url_for("member.myProfile"))
    else:
        return redirect(url_for("auth.home"))



#My Booking section
@member.route("/myBooking")
def myBooking():
    if "username" in session:
        username = session["username"]
        #get MemberID
        dbresult1 = db_manager.execute_query("SELECT * FROM Member where Member.Email=%s",(username,))['result']
        MemberID=dbresult1[0][0]
        dateChosen=request.args.get("dateChosen","")
        #if user input is empty,show current date class booking record
        if dateChosen=="" :
            Today=date.today()
            dateChosen=Today
            WeekNum=int(Today.strftime("%W"))
        else:
            dateChosen=datetime.strptime(dateChosen, '%Y-%m-%d').date()
            WeekNum=int(dateChosen.strftime("%W"))
        #get expired class info
        expiredClassInfo = db_manager.execute_query("SELECT * FROM Timetable WHERE CONCAT(ClassDate, ' ', StartTime) < %s AND WEEKOFYEAR(ClassDate) = %s",(formatted_now_nz,WeekNum))['result']
        ExpireClassID=[ str(x[0]) for x in expiredClassInfo]
        WeekNum=f"{WeekNum}%"
        #get date for each weeknum
        dbresultDate=db_manager.execute_query("""SELECT DISTINCT
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
                    """,(WeekNum,))['result'][0]
        #get my booking details
        #get related 'current' class booking info for each member,Cancelled class will not show on table.
        dbresult2 = db_manager.execute_query("""
                SELECT Timetable.StartTime, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
                FROM
                (SELECT DISTINCT StartTime FROM Timetable) AS Timetable
                LEFT JOIN
                (SELECT
                t.StartTime,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Monday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',DATE_FORMAT(t.ClassDate,'%d-%b-%Y'),',',t.StartTime,',',t.EndTime,',',t.ClassCode) ELSE NULL END) AS Monday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Tuesday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',DATE_FORMAT(t.ClassDate,'%d-%b-%Y'),',',t.StartTime,',',t.EndTime,',',t.ClassCode) ELSE NULL END) AS Tuesday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Wednesday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),DATE_FORMAT(t.ClassDate,'%d-%b-%Y'),',',t.StartTime,',',t.EndTime,',',t.ClassCode) ELSE NULL END) AS Wednesday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Thursday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',DATE_FORMAT(t.ClassDate,'%d-%b-%Y'),',',t.StartTime,',',t.EndTime,',',t.ClassCode) ELSE NULL END) AS Thursday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Friday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',DATE_FORMAT(t.ClassDate,'%d-%b-%Y'),',',t.StartTime,',',t.EndTime,',',t.ClassCode) ELSE NULL END) AS Friday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Saturday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',DATE_FORMAT(t.ClassDate,'%d-%b-%Y'),',',t.StartTime,',',t.EndTime,',',t.ClassCode) ELSE NULL END) AS Saturday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Sunday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',DATE_FORMAT(t.ClassDate,'%d-%b-%Y'),',',t.StartTime,',',t.EndTime,',',t.ClassCode) ELSE NULL END) AS Sunday
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
                WHERE
                b.MemberID=%s AND
                b.BookingStatus='Current' and
                WEEKOFYEAR(t.ClassDate) Like %s
                GROUP BY t.StartTime) AS Table2
                ON Timetable.StartTime = Table2.StartTime
                ORDER BY Timetable.StartTime;""",(MemberID,WeekNum))
        dbcols=dbresult2['dbcols']
        dbresult=dbresult2['result']
        #get data for database and process
        listdb=[]
        listlayer=[]
        listclass=[]
        for x in dbresult:
            for y in x:
                if type(y)!=str or y=='':
                    listlayer.append(y)
                else:
                    for b in y.split(","):
                        listclass.append(b)
                    listlayer.append(listclass)
                    listclass=[]
            listdb.append(listlayer)
            listclass=[]
            listlayer=[]
        return render_template("myBooking.html",
                        username=username,
                        dbcols=dbcols,
                        dbresult=listdb,
                        dateChosen=dateChosen,
                        dbresultDate=dbresultDate,
                        MemberID=MemberID,
                        ExpireClassID=ExpireClassID)
    else:
        return redirect(url_for("auth.home"))

@member.route("/myMessage")
def myMessage():
    if "username" in session:
        username = session["username"]
        member = db_manager.execute_query("SELECT * FROM Member where Member.Email=%s limit 2000 ",(username,))['result'][0]
        memberID = member[0]
        memberIsReceivingNotifation = member[11]
        memberStatus = member[17]
        memberJoinDate = member[10]
        current_time = datetime.now()
        today_date = datetime.now().day
        memberJoinDay = memberJoinDate.strftime('%d')
        today_date_int = int(today_date)
        memberJoinDay_int = int(memberJoinDay)
        sql_weeklyupdate = """SELECT * FROM weeklyupdate ORDER BY updateTime DESC LIMIT 1 """
        weeklyupdate = db_manager.execute_query(sql_weeklyupdate)['result']
        sql_notice = """SELECT NoticeSubject, Content, NoticeDate FROM Notice
                        WHERE MemberID=%s
                        ORDER BY NoticeDate DESC
                        LIMIT 60 """
        messageList = db_manager.execute_query(sql_notice,(memberID,))['result']
        return render_template("myMessage.html", username=username, messageList=messageList,memberIsReceivingNotifation=memberIsReceivingNotifation,weeklyupdate=weeklyupdate,memberStatus=memberStatus,current_time=current_time,today_date_int=today_date_int,memberJoinDay_int=memberJoinDay_int)
    else:
        return redirect(url_for("auth.home"))