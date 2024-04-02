from flask import (Blueprint,Flask, flash, redirect, render_template,
                   request, session, url_for)
from database import db_manager


admin = Blueprint("admin",__name__,template_folder="templates",static_folder="static",static_url_path='/admin/static', url_prefix='')



# admin system
@admin.route("/admin/dashboard")
def theAdmin():
    if "username" in session:
        username = session["username"]
        return render_template("adminDashboard.html"
                               ,username=username
                               )
    else:
        return redirect(url_for("auth.adminLogin_get"))

#Render Member List Page
@admin.route("/admin/member")
def MemberList():
    if "username" in session:
        username = session["username"]
        showMemberType=request.args.get("showMemberType","")
        showMemberType=f"{showMemberType}%"
        db = db_manager.execute_query("""Select MemberID,CONCAT(Firstname," ",Lastname) as 'Name',DateOfBirth,GymJoinDate,MemberStatus from Member
                        where  MemberStatus LIKE %s
                        order by CONCAT(Firstname," ",Lastname)""",(showMemberType,))
        message_nodata="Sorry!No member information under this category!"
        return render_template("manageMember.html",
                            dbcols=db['dbcols'],
                            dbresult=db['result']
                                ,username=username,
                                showMemberType=showMemberType,
                                message_nodata=message_nodata
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))


# Render Trainer Workload for admin
@admin.route("/admin/trainerwork", methods=['GET'])
def trainerwork():
    if "username" in session:
        sql_trainerwork = """Select t2.TrainerID, t2.TrainerName, count(t2.ClassDate) from (
                Select * from (
                Select tr.TrainerID, concat(FirstName, ' ', tr.LastName) as 'TrainerName', ct.ClassName, tb.ClassDate, tb.StartTime, tb.EndTime
                from Timetable tb
                left join ClassType ct on tb.ClassCode = ct.ClassCode
                left join Trainer tr on tb.TrainerID = tr.TrainerID
                Where tb.ClassCode != 1 and tb.ClassDate >= '2023-01-01' and tb.ClassDate <= '2023-12-31'
                ) t ) t2
                group by t2.TrainerID, t2.TrainerName order by t2.TrainerID asc;"""
        username = session["username"]
        db = db_manager.execute_query(sql_trainerwork)
        return render_template("managerTrainerWork.html",
                                username=username,
                                dbcols=db['dbcols'],
                                dbresult = db['result']
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))

# render trainer class work by selected date
@admin.route("/admin/checkclasscount", methods=['POST'])
def checkclasscount():
    if "username" in session:
        trainer_class_count = """Select t2.TrainerID, t2.TrainerName, count(t2.ClassDate) from (
                            Select * from (
                            Select tr.TrainerID, concat(FirstName, ' ', tr.LastName) as 'TrainerName', ct.ClassName, tb.ClassDate, tb.StartTime, tb.EndTime
                            from Timetable tb
                            left join ClassType ct on tb.ClassCode = ct.ClassCode
                            left join Trainer tr on tb.TrainerID = tr.TrainerID
                            Where tb.ClassCode != 1 and tb.ClassDate >= %s and tb.ClassDate <= %s
                            ) t ) t2
                            group by t2.TrainerID, t2.TrainerName Order by t2.TrainerID;"""
        username = session["username"]

        startdate = request.form.get("startdate")
        enddate = request.form.get("enddate")
        result = db_manager.execute_query(trainer_class_count, (startdate, enddate,))
        return render_template("manageTrainerWorkCount.html",
                                username=username,
                                startdate=startdate,
                                enddate=enddate,
                                dbcols=result['dbcols'],
                                dbresult=result['result']
                                )


#Individual trainer class details
@admin.route("/admin/trainer/workdetails",methods=["POST"])
def trainerclassdetails():
    if "username" in session:
        username = session["username"]
        trainerID=request.form["trainerID"]
        startdate = request.args.get('startdate')
        enddate = request.args.get('enddate')
        trainer_class_details = """Select concat(FirstName, ' ', tr.LastName) as 'TrainerName',
                                    ct.ClassName, DATE_FORMAT(tb.ClassDate,'%d/%m/%Y'), tb.StartTime, tb.EndTime
                                    from Timetable tb
                                    left join ClassType ct on tb.ClassCode = ct.ClassCode
                                    left join Trainer tr on tb.TrainerID = tr.TrainerID
                                    Where tb.ClassCode != 1 and tb.ClassDate >= %s and tb.ClassDate <= %s and tb.TrainerID=%s
                                    Order by tb.ClassDate asc"""
        result = db_manager.execute_query(trainer_class_details, (startdate, enddate, trainerID))
        return render_template("manageTrainerDetailsSelectedDate.html",
                                username=username,
                                dbcols=result['dbcols'],
                                dbresult=result['result'],
                                 trainerID=trainerID,
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))

# Render the popularity report
@admin.route("/admin/popularityreport", methods=['GET'])
def popularityreport():
    if "username" in session:
        popularity_sql = """Select px.ClassName, px.Trainer_Name, sum(px.Attended_Number) as 'Attended_Number', concat(convert(round(avg(px.Attdence_Rate), 2), char), '%') as 'Attdence_Rate'
from (
Select  tx.ClassName, tx.Trainer_Name, tx.Attended_Number,
                concat(round(Convert((tx.Attended_Number/30)*100, char), 2),  '%') as 'Attdence_Rate' from (
                Select t.ClassDate, t.ClassName, t.Trainer_Name, count(t.MemberID) as 'Attended_Number' from (
                Select bk.MemberID, bk.ClassID, tt.ClassDate, ct.ClassName, concat(tr.FirstName, ' ', tr.LastName) as 'Trainer_Name',
                    tt.ClassCode
                from Booking bk
                left join Timetable tt on bk.ClassID = tt.ClassID
                left join ClassType ct on tt.ClassCode = ct.ClassCode
                left join Trainer tr on tt.TrainerID = tr.TrainerID
                Where ct.ClassCode != 1 and tt.ClassDate >= '2023-01-01' and  tt.ClassDate <= '2023-12-31') t
                Group by t.ClassDate, t.ClassName, t.Trainer_Name) tx
                Where Attended_Number <= 30
                Order by Attended_Number desc) px
group by px.ClassName, px.Trainer_Name
Order by avg(px.Attdence_Rate) desc;"""
        username = session["username"]
        result = db_manager.execute_query(popularity_sql)
        return render_template("managerPopularityView.html",
                                username=username,
                                dbcols=result['dbcols'],
                                dbresult=result['result'],
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))

# Select the specific date to view popularity
@admin.route("/admin/checkpopbydate", methods=['POST'])
def checkpopbydate():
    if "username" in session:
        popularity_selected = """Select px.ClassName, px.Trainer_Name, sum(px.Attended_Number) as 'Attended_Number', concat(convert(round(avg(px.Attdence_Rate), 2), char), '%') as 'Attdence_Rate'
from (
Select  tx.ClassName, tx.Trainer_Name, tx.Attended_Number,
                concat(round(Convert((tx.Attended_Number/30)*100, char), 2),  '%') as 'Attdence_Rate' from (
                Select t.ClassDate, t.ClassName, t.Trainer_Name, count(t.MemberID) as 'Attended_Number' from (
                Select bk.MemberID, bk.ClassID, tt.ClassDate, ct.ClassName, concat(tr.FirstName, ' ', tr.LastName) as 'Trainer_Name',
                    tt.ClassCode
                from Booking bk
                left join Timetable tt on bk.ClassID = tt.ClassID
                left join ClassType ct on tt.ClassCode = ct.ClassCode
                left join Trainer tr on tt.TrainerID = tr.TrainerID
                Where ct.ClassCode != 1 and tt.ClassDate >= %s and  tt.ClassDate <= %s) t
                Group by t.ClassDate, t.ClassName, t.Trainer_Name) tx
                Where Attended_Number <= 30
                Order by Attended_Number desc) px
group by px.ClassName, px.Trainer_Name
Order by avg(px.Attdence_Rate) desc;"""
        username = session["username"]

        startdate = request.form.get("startdate")
        enddate = request.form.get("enddate")
        result = db_manager.execute_query(popularity_selected, (startdate, enddate,))
        return render_template("manageCheckPopularitybyDate.html",
                                username=username,
                                startdate=startdate,
                                enddate=enddate,
                                dbcols=result['dbcols'],
                                dbresult=result['result'],
                                )


# Generate Financial Report - summary
@admin.route("/admin/financialreport", methods=['GET'])
def financialreport():
    if "username" in session:
        financial_sql = """Select ClassName, sum(Class_Fee) as 'Revenue' from (
                    Select sc.SubscriptionID, 'Member Subscription' as 'ClassName',  'Member Subscription' as 'Trainer_Name', sc.SubscriptionStartDate as 'Start_Date',
                    sc.SubscriptionEndDate as 'End_Date', sc.PaymentAmount as 'Class_Fee'
                    from Subscription sc
                    left join Member m on sc.MemberID = m.MemberID
                    Union
                    -- PT training financial
                    Select tt.ClassID, ct.ClassName, concat(tr.FirstName, ' ', tr.LastName) as 'Trainer_Name',
                    tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', 50 as 'Class_Fee'
                    from Timetable tt
                    left join ClassType ct on tt.ClassCode = ct.ClassCode
                    left join Trainer tr on tt.TrainerID = tr.TrainerID
                    Where tt.ClassCode = 1) t
                    Where t.Start_Date >= '2023-02-01' and t.End_Date <= '2023-12-01'
                    Group by ClassName;"""

        total_sql = """Select sum(Class_Fee) as 'Revenue' from (
                    Select sc.SubscriptionID, 'Member Subscription' as 'ClassName',  'Member Subscription' as 'Trainer_Name', sc.SubscriptionStartDate as 'Start_Date',
                    sc.SubscriptionEndDate as 'End_Date', sc.PaymentAmount as 'Class_Fee'
                    from Subscription sc
                    left join Member m on sc.MemberID = m.MemberID
                    Union
                    -- PT training financial
                    Select tt.ClassID, ct.ClassName, concat(tr.FirstName, ' ', tr.LastName) as 'Trainer_Name',
                    tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', 50 as 'Class_Fee'
                    from Timetable tt
                    left join ClassType ct on tt.ClassCode = ct.ClassCode
                    left join Trainer tr on tt.TrainerID = tr.TrainerID
                    Where tt.ClassCode = 1) t
                    Where t.Start_Date >= '2023-01-01' and t.End_Date <= '2023-12-01'"""

        single_pt_sql = """Select t3.Trainer_Name, sum(Class_Fee) from (
            Select tt.ClassID, ct.ClassName, concat(tr.FirstName, ' ', tr.LastName) as 'Trainer_Name',
            tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', 50 as 'Class_Fee'
            from Timetable tt
            left join ClassType ct on tt.ClassCode = ct.ClassCode
            left join Trainer tr on tt.TrainerID = tr.TrainerID
            Where tt.ClassCode = 1) t3
            Where t3.Start_Date >= '2023-02-01' and t3.End_Date <= '2023-03-31'
            group by Trainer_Name"""

        username = session["username"]
        result1 = db_manager.execute_query(financial_sql)
        result2 = db_manager.execute_query(total_sql)
        result3 = db_manager.execute_query(single_pt_sql)
        return render_template("managerFinancialReport.html",
                                username=username,
                                dbcols=result1['dbcols'],
                                dbresult=result1['result'],
                               dbcols_f=result2['dbcols'],
                               dbresult_f=result2['result'],
                               dbcols_single=result3['dbcols'],
                               dbresult_single=result3['result'],
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))

# Select the specific date to filter financial report
@admin.route("/admin/checkfinancebydate", methods=['POST'])
def checkfinancebydate():
    if "username" in session:
        if "username" in session:
            financial_sql_selected = """Select ClassName, sum(Class_Fee) as 'Revenue' from (
                        Select sc.SubscriptionID, 'Member Subscription' as 'ClassName',  'Member Subscription' as 'Trainer_Name', sc.SubscriptionStartDate as 'Start_Date',
                        sc.SubscriptionEndDate as 'End_Date', sc.PaymentAmount as 'Class_Fee'
                        from Subscription sc
                        left join Member m on sc.MemberID = m.MemberID
                        Union
                        -- PT training financial
                        Select tt.ClassID, ct.ClassName, concat(tr.FirstName, ' ', tr.LastName) as 'Trainer_Name',
                        tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', 50 as 'Class_Fee'
                        from Timetable tt
                        left join ClassType ct on tt.ClassCode = ct.ClassCode
                        left join Trainer tr on tt.TrainerID = tr.TrainerID
                        Where tt.ClassCode = 1) t
                        Where t.Start_Date >= %s and t.End_Date <= %s
                        Group by ClassName;"""

            total_sql_selected = """Select sum(Class_Fee) as 'Revenue' from (
                        Select sc.SubscriptionID, 'Member Subscription' as 'ClassName',  'Member Subscription' as 'Trainer_Name', sc.SubscriptionStartDate as 'Start_Date',
                        sc.SubscriptionEndDate as 'End_Date', sc.PaymentAmount as 'Class_Fee'
                        from Subscription sc
                        left join Member m on sc.MemberID = m.MemberID
                        Union
                        -- PT training financial
                        Select tt.ClassID, ct.ClassName, concat(tr.FirstName, ' ', tr.LastName) as 'Trainer_Name',
                        tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', 50 as 'Class_Fee'
                        from Timetable tt
                        left join ClassType ct on tt.ClassCode = ct.ClassCode
                        left join Trainer tr on tt.TrainerID = tr.TrainerID
                        Where tt.ClassCode = 1) t
                        Where t.Start_Date >= %s and t.End_Date <= %s"""

            single_pt_sql_selected = """Select t3.Trainer_Name, sum(Class_Fee) from (
                        Select tt.ClassID, ct.ClassName, concat(tr.FirstName, ' ', tr.LastName) as 'Trainer_Name',
                        tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', 50 as 'Class_Fee'
                        from Timetable tt
                        left join ClassType ct on tt.ClassCode = ct.ClassCode
                        left join Trainer tr on tt.TrainerID = tr.TrainerID
                        Where tt.ClassCode = 1) t3
                        Where t3.Start_Date >= %s and t3.End_Date <= %s
                        group by Trainer_Name"""
        username = session["username"]

        startdate = request.form.get("startdate")
        enddate = request.form.get("enddate")

        result1 = db_manager.execute_query(financial_sql_selected, (startdate, enddate,))
        result2 =db_manager.execute_query(total_sql_selected, (startdate, enddate,))
        result3 = db_manager.execute_query(single_pt_sql_selected, (startdate, enddate,))
        return render_template("manageCheckFinancialbyDate.html",
                                username=username,
                                startdate=startdate,
                                enddate=enddate,
                                dbcols1=result1['dbcols'],
                                dbresult_sld1=result1['result'],
                               dbcols2=result2['dbcols'],
                               dbresult_sld2=result2['result'],
                               dbcols3=result3['dbcols'],
                               dbresult_sld3=result3['result'],
                            )


# Generate Member Attendance Report - summary
@admin.route("/admin/gymusagereport", methods=['GET'])
def gymusagereport():
    if "username" in session:
        usage_sql = """Select opt.TypeOfVisit, sum(opt.Daily_Total) as 'NumberofMemberJoined', sum(opt.Capcity) as 'Total_Capacity', concat(convert(round(avg(opt.ratio), 2), char), '%') as 'UsageRatio'
                    from (
                    Select AT_Start_Date, TypeOfVisit, Daily_Total, Capcity, (Daily_Total/Capcity)*100 as 'ratio'
                    from (
                    Select t.Start_Date, t.End_Date, t.Purpose, count(t.ClassID) as 'Number_PT_Class',
                    Case when t.Purpose = 'Class' then count(t.ClassID)*30
                        when t.Purpose != 'Class' then count(t.ClassID)
                        end as 'Capcity'
                    From (
                    Select tt.ClassID, tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', tt. ClassCode,
                    case when tt.ClassCode = 1 then 'PT Session'
                        when tt.ClassCode != 1 then 'Class'
                        End as 'Purpose'
                    from Timetable tt) t
                    group by t.Start_Date, t.End_Date, t.Purpose) tb
                    right join (Select daily.AT_Start_Date, daily.AT_End_Date, daily.TypeOfVisit, sum(Count) 'Daily_Total' from (
                    Select DATE(at.EnterTime) as 'AT_Start_Date', DATE(at.EnterTime) as 'AT_End_Date', at.TypeOfVisit, 1 as 'Count'
                    From Attendance at) daily
                    group by daily.AT_Start_Date, daily.AT_End_Date, daily.TypeOfVisit) atd
                    on tb.Start_Date = atd.AT_Start_Date and tb.End_Date = atd.AT_End_Date and tb.Purpose = atd.TypeOfVisit
                    Where atd.AT_Start_Date >= '2023-01-01' and atd.AT_End_Date <= '2023-12-31'
                    ) opt
                    group by opt.TypeOfVisit;"""


        total_member_sql = """Select sum(Daily_Total) as 'Total_Member'
                    from (
                    Select t.Start_Date, t.End_Date, t.Purpose, count(t.ClassID) as 'Number_PT_Class',
                    Case when t.Purpose = 'Class' then count(t.ClassID)*30
                        when t.Purpose != 'Class' then count(t.ClassID)
                        end as 'Capcity'
                    From (
                    Select tt.ClassID, tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', tt. ClassCode,
                    case when tt.ClassCode = 1 then 'PT Session'
                        when tt.ClassCode != 1 then 'Class'
                        End as 'Purpose'
                    from Timetable tt) t
                    -- Where t.Start_Date >= '2023-02-01' and t.End_Date<= '2023-02-02'
                    group by t.Start_Date, t.End_Date, t.Purpose) tb
                    right join (Select daily.AT_Start_Date, daily.AT_End_Date, daily.TypeOfVisit, sum(Count) 'Daily_Total' from (
                    Select DATE(at.EnterTime) as 'AT_Start_Date', DATE(at.EnterTime) as 'AT_End_Date', at.TypeOfVisit, 1 as 'Count'
                    From Attendance at) daily
                    group by daily.AT_Start_Date, daily.AT_End_Date, daily.TypeOfVisit) atd
                    on tb.Start_Date = atd.AT_Start_Date and tb.End_Date = atd.AT_End_Date and tb.Purpose = atd.TypeOfVisit
                    Where atd.AT_Start_Date >= '2023-01-01' and atd.AT_End_Date <= '2023-12-31';"""

        username = session["username"]
        result1 = db_manager.execute_query(usage_sql)
        result2 = db_manager.execute_query(total_member_sql)

        return render_template("managerGymAttendanceReport.html",
                                username=username,
                                dbcols_usage=result1['dbcols'],
                                dbresult_usage=result1['result'],
                               dbcols_total=result2['dbcols'],
                               dbresult_total=result2['result']
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))

# Generate Member Attendance Ratio by selected period
@admin.route("/admin/checkattendancebydate", methods=['POST'])
def gymusage_bydate_report():
    if "username" in session:
        usage_sql = """Select opt.TypeOfVisit, sum(opt.Daily_Total) as 'NumberofMemberJoined', sum(opt.Capcity) as 'Total_Capacity', concat(convert(round(avg(opt.ratio), 2), char), '%') as 'UsageRatio'
                    from (
                    Select AT_Start_Date, TypeOfVisit, Daily_Total, Capcity, (Daily_Total/Capcity)*100 as 'ratio'
                    from (
                    Select t.Start_Date, t.End_Date, t.Purpose, count(t.ClassID) as 'Number_PT_Class',
                    Case when t.Purpose = 'Class' then count(t.ClassID)*30
                        when t.Purpose != 'Class' then count(t.ClassID)
                        end as 'Capcity'
                    From (
                    Select tt.ClassID, tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', tt. ClassCode,
                    case when tt.ClassCode = 1 then 'PT Session'
                        when tt.ClassCode != 1 then 'Class'
                        End as 'Purpose'
                    from Timetable tt) t
                    group by t.Start_Date, t.End_Date, t.Purpose) tb
                    right join (Select daily.AT_Start_Date, daily.AT_End_Date, daily.TypeOfVisit, sum(Count) 'Daily_Total' from (
                    Select DATE(at.EnterTime) as 'AT_Start_Date', DATE(at.EnterTime) as 'AT_End_Date', at.TypeOfVisit, 1 as 'Count'
                    From Attendance at) daily
                    group by daily.AT_Start_Date, daily.AT_End_Date, daily.TypeOfVisit) atd
                    on tb.Start_Date = atd.AT_Start_Date and tb.End_Date = atd.AT_End_Date and tb.Purpose = atd.TypeOfVisit
                    Where atd.AT_Start_Date >= %s and atd.AT_End_Date <= %s
                    ) opt
                    group by opt.TypeOfVisit;"""


        total_member_sql = """Select sum(Daily_Total) as 'Total_Member'
                    from (
                    Select t.Start_Date, t.End_Date, t.Purpose, count(t.ClassID) as 'Number_PT_Class',
                    Case when t.Purpose = 'Class' then count(t.ClassID)*30
                        when t.Purpose != 'Class' then count(t.ClassID)
                        end as 'Capcity'
                    From (
                    Select tt.ClassID, tt.ClassDate as 'Start_Date', tt.ClassDate as 'End_Date', tt. ClassCode,
                    case when tt.ClassCode = 1 then 'PT Session'
                        when tt.ClassCode != 1 then 'Class'
                        End as 'Purpose'
                    from Timetable tt) t
                    -- Where t.Start_Date >= '2023-02-01' and t.End_Date<= '2023-02-02'
                    group by t.Start_Date, t.End_Date, t.Purpose) tb
                    right join (Select daily.AT_Start_Date, daily.AT_End_Date, daily.TypeOfVisit, sum(Count) 'Daily_Total' from (
                    Select DATE(at.EnterTime) as 'AT_Start_Date', DATE(at.EnterTime) as 'AT_End_Date', at.TypeOfVisit, 1 as 'Count'
                    From Attendance at) daily
                    group by daily.AT_Start_Date, daily.AT_End_Date, daily.TypeOfVisit) atd
                    on tb.Start_Date = atd.AT_Start_Date and tb.End_Date = atd.AT_End_Date and tb.Purpose = atd.TypeOfVisit
                    Where atd.AT_Start_Date >= %s and atd.AT_End_Date <= %s;"""

        username = session["username"]
        startdate = request.form.get("startdate")
        enddate = request.form.get("enddate")

        result1 = db_manager.execute_query(usage_sql, (startdate, enddate,))
        result2 = db_manager.execute_query(total_member_sql, (startdate, enddate,))

        return render_template("managerGymAttendanceReportByDate.html",
                                username=username,
                                dbcols_u1=result1['dbcols'],
                                dbresult_u1=result1['result'],
                                dbcols_to=result2['dbcols'],
                                dbresult_to=result2['result']
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))


#Add Member Page
@admin.route("/admin/member/addmember")
def addmember():
    if "username" in session:
        username = session["username"]
        return render_template("addmember.html"
                                ,username=username
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))


@admin.route("/admin/member/editmember/process",methods=["POST"])
def editMemberProcess():
    if "username" in session:
        username = session["username"]
        memberID=request.form['memberID']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']
        phone=request.form['phone']
        PhysicalAddress=request.form['PhysicalAddress']
        DOB=request.form['DOB']
        EmergencyName=request.form['EmergencyName']
        EmergencyNumber=request.form['EmergencyNumber']
        Mconditions=request.form['Mconditions']
        GJD=request.form['GJD']
        psw=request.form['psw']
        ReceivingNotifications=request.form['ReceivingNotifications']
        autoFee=request.form['autoFee']
        BankName=request.form['BankName']
        BankAccountHolderName=request.form['BankAccountHolderName']
        BankAccountNumber=request.form['BankAccountNumber']
        MemberStatus=request.form['MemberStatus']
        MemberNotes=request.form['MemberNotes']
        #Add member process
        if memberID=="None":
            sql="""INSERT INTO Member (FirstName, LastName, Email, PhysicalAddress, Phone, DateOfBirth, EmergencyContactName, EmergencyContactNumber,
                        MedicalConditions, GymJoinDate, ReceivingNotifications, MemberPassword, AuthorityOnCollectingFees, BankName, BankAccountHolderName, BankAccountNumber, MemberStatus,MemberNotes)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s,%s, %s,%s, %s, %s, %s,%s)"""
            db_manager.execute_query(sql,(firstname,lastname,email,PhysicalAddress,phone,DOB,EmergencyName,EmergencyNumber,Mconditions,GJD,ReceivingNotifications,psw,autoFee,BankName,BankAccountHolderName,BankAccountNumber,MemberStatus,MemberNotes))
            #render the added new-member detail page
            result = db_manager.execute_query("select * from Member where email=%s",(email,))
            dbresult=result['result']
            #assign memberID variable for later use
            memberID=dbresult[0][0]
            flash("New member has been added successfully!", "successadd")

            return redirect(f"/admin/member/editmember?memberID={memberID}")
        #update member detail process
        else:
            sql="""update Member set FirstName=%s, LastName=%s, Email=%s, PhysicalAddress=%s, Phone=%s, DateOfBirth=%s,
                    EmergencyContactName=%s, EmergencyContactNumber=%s, MedicalConditions=%s, GymJoinDate=%s, ReceivingNotifications=%s,
                    MemberPassword=%s, AuthorityOnCollectingFees=%s, BankName=%s, BankAccountHolderName=%s, BankAccountNumber=%s, MemberStatus=%s,MemberNotes=%s
                    where MemberID=%s"""
            db_manager.execute_query(sql,(firstname,lastname,email,PhysicalAddress,phone,DOB,EmergencyName,EmergencyNumber,Mconditions,GJD,ReceivingNotifications,psw,autoFee,BankName,
                             BankAccountHolderName,BankAccountNumber,MemberStatus,MemberNotes,memberID))
            flash("Details have been updated successfully!", "success")

            return redirect(f"/admin/member/editmember?memberID={memberID}")
    else:
        return redirect(url_for("auth.adminLogin_get"))

# Edit member details page with original member detail data.
@admin.route("/admin/member/editmember")
def editMember():
    if "username" in session:
        username = session["username"]
        memberID=request.args.get("memberID")
        removeReadonly=request.args.get("removeReadonly","")
        result1 = db_manager.execute_query("select * from Member where MemberID=%s",(memberID,))
        dbresult=result1['result']
        #assign the originial values to variables
        firstname=dbresult[0][1]
        lastname=dbresult[0][2]
        email=dbresult[0][3]
        phone=dbresult[0][5]
        PhysicalAddress=dbresult[0][4]
        DOB=dbresult[0][6]
        EmergencyName=dbresult[0][7]
        EmergencyNumber=dbresult[0][8]
        Mconditions=dbresult[0][9]
        GJD=dbresult[0][10]
        psw=dbresult[0][12]
        ReceivingNotifications=dbresult[0][11]
        autoFee=dbresult[0][13]
        BankName=dbresult[0][14]
        BankAccountHolderName=dbresult[0][15]
        BankAccountNumber=dbresult[0][16]
        MemberStatus=dbresult[0][17]
        MemberNotes=dbresult[0][18]
        return render_template("editMember.html",
                                memberID= memberID,
                                username=username,
                                firstname=firstname,
                                lastname=lastname,
                                email=email,
                                phone=phone,
                                PhysicalAddress=PhysicalAddress,
                                DOB=DOB,
                                EmergencyName=EmergencyName,
                                EmergencyNumber=EmergencyNumber,
                                Mconditions=Mconditions,
                                GJD=GJD,
                                psw=psw,
                                ReceivingNotifications=ReceivingNotifications,
                                autoFee=autoFee,
                                BankName=BankName,
                                BankAccountHolderName=BankAccountHolderName,
                                BankAccountNumber=BankAccountNumber,
                                MemberStatus=MemberStatus,
                                MemberNotes=MemberNotes,
                                removeReadonly=removeReadonly
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))


@admin.route("/admin/trainer")
def manageTrainer():
    if "username" in session:
        username = session["username"]
        result1 = db_manager.execute_query("""SELECT TrainerID, FirstName, LastName, Email, Phone, DateOfBirth, DateOfEmployment,
                    TrainerStatus FROM Trainer;""")
        return render_template("manageTrainer.html",
                            dbcols=result1['dbcols'],
                            dbresult=result1['result']
                                ,username=username
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))


# Edit trainer details page with original trainer detail data.
@admin.route("/admin/trainer/edittrainer")
def editTrainer():
    if "username" in session:
        print("##endittrainer args", request.args)
        removeReadonly=request.args.get("removeReadonly","")
        username = session["username"]
        trainerID=request.args.get("trainerID")
        result1 = db_manager.execute_query("select * from Trainer where TrainerID=%s",(trainerID,))
        dbresult=result1['result']
        firstname=dbresult[0][1]
        lastname=dbresult[0][2]
        email=dbresult[0][3]
        phone=dbresult[0][4]
        DOB=dbresult[0][5]
        DOE=dbresult[0][6]
        psw=dbresult[0][7]
        EmergencyName=dbresult[0][8]
        EmergencyNumber=dbresult[0][9]
        Mconditions=dbresult[0][10]
        TrainerStatus=dbresult[0][-1]
        return render_template("edittrainer.html",
                                trainerID=trainerID,
                                username=username,
                                firstname=firstname,
                                lastname=lastname,
                                email=email,
                                phone=phone,
                                DOB=DOB,
                                EmergencyName=EmergencyName,
                                EmergencyNumber=EmergencyNumber,
                                Mconditions=Mconditions,
                                DOE=DOE,
                                psw=psw,
                                TrainerStatus=TrainerStatus,
                                removeReadonly=removeReadonly
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))



@admin.route("/admin/trainer/edittrainer/process",methods=["POST"])
def editTrainerProcess():
    if "username" in session:
        username = session["username"]
        #get userinput member details
        trainerID=request.form['trainerID']
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        email=request.form['email']
        phone=request.form['phone']
        DOB=request.form['DOB']
        DOE=request.form['DOE']
        psw=request.form['psw']
        trainerStatus=request.form['trainerStatus']
        EmergencyName=request.form['EmergencyName']
        EmergencyNumber=request.form['EmergencyNumber']
        Mconditions=request.form['Mconditions']

        #Add trainer process
        if trainerID=="None":
            sql="""INSERT INTO Trainer( FirstName, LastName, Email, Phone, DateOfBirth, DateOfEmployment, TrainerPassword, EmergencyContactName, EmergencyContactNumber, MedicalConditions, TrainerStatus)
                    values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            db_manager.execute_query(sql,(firstname,lastname,email,phone,DOB,DOE,psw,EmergencyName,EmergencyNumber,Mconditions,trainerStatus))
            #render the added new-trainer detail page
            result1 = db_manager.execute_query("select * from Trainer where email=%s",(email,))
            # dbcols=[desc[0] for desc in result1.description]
            # dbresult=result1['result']
            #assign memberID variable for later use
            trainerID=result1['result'][0][0]
            flash("New trainer has been successfully added!", "successAddTrainer")
            return redirect(f"/admin/trainer/edittrainer?trainerID={trainerID}")
        #update trainer detail process
        else:
            sql="""update Trainer set FirstName=%s, LastName=%s, Email=%s, Phone=%s, DateOfBirth=%s,
            DateOfEmployment=%s, TrainerPassword=%s, EmergencyContactName=%s, EmergencyContactNumber=%s, MedicalConditions=%s, TrainerStatus=%s
            where TrainerID=%s"""
            result2 = db_manager.execute_query(sql,(firstname,lastname,email,phone,DOB,DOE,psw,EmergencyName,EmergencyNumber,Mconditions,trainerStatus,trainerID))
            #render the the same trainer page with same trainerID
            result2.execute("select * from Trainer where TrainerID=%s",(trainerID,))
            flash("Details have been updated successfully!", "success")
            return redirect(f"/admin/trainer/edittrainer?trainerID={trainerID}")
    else:
        return redirect(url_for("auth.adminLogin_get"))


#Add a trainer page
@admin.route("/admin/addtrainer")
def addtrainer():
    if "username" in session:
        username = session["username"]

        return render_template("addtrainer.html",
                                username=username
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))


#view trainer class page
@admin.route("/admin/viewTrainerClass")
def viewTrainerClass():
    if "username" in session:
        username = session["username"]

        return render_template("viewTrainerClass.html",
                                username=username
                                )
    else:
        return redirect(url_for("auth.adminLogin_get"))


@admin.route("/admin/weeklyUpdate")
def weeklyUpdate():
    if "username" in session:
        username = session["username"]
        return render_template("weeklyUpdate.html",username=username)
    else:
        return redirect(url_for("auth.adminLogin_get"))


@admin.route("/admin/weeklyUpdatePOST",methods=["POST"])
def weeklyUpdatePOST():
    topic = request.form.get("topic")
    content = request.form.get("content")
    sql = """INSERT INTO weeklyupdate (topic,content)
    VALUES (%s,%s) """
    db_manager.execute_query(sql, (topic,content))
    flash(" You have sent a weekly update to members successfully!")
    return redirect(url_for("weeklyUpdate"))
