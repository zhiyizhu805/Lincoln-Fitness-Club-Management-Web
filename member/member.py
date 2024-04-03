from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from datetime import date, datetime
from member.model import Member, Booking

member = Blueprint(
    "member",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/member/static",
    url_prefix="",
)

currentDate = date.today()

######   My Profile   ######
@member.route("/myProfile")
def myProfile():
    if "username" in session:
        username = session["username"]
        my_profile = Member(session["username"]).getMemberDetails()
        return render_template(
            "myProfile.html", username=username, select_result=my_profile
        )
    else:
        return redirect(url_for("auth.home"))


@member.route("/myProfile/edit")
def myProfileEditGet():
    if "username" in session:
        username = session["username"]
        my_profile = Member(session["username"]).getMemberDetails()
        return render_template(
            "myProfileEdit.html", username=username, select_result=my_profile
        )
    else:
        return redirect(url_for("auth.home"))


@member.route("/myProfileEditPOST", methods=["POST"])
def myProfileEdit():
    if "username" in session:
        formData = request.form.to_dict()
        member = Member(session["username"])
        member.getMemberDetails()
        member.updateProfile(formData)
        flash("Details have been successfully updated")
        return redirect(url_for("member.myProfile"))
    else:
        return redirect(url_for("auth.home"))


######   My Booking   ######
@member.route("/myBooking")
def myBooking():
    if "username" in session:
        username = session["username"]
        member = Member(session["username"])
        member.getMemberDetails()
        dateChosen = request.args.get("dateChosen", "")
        # if user input is empty,show current date class booking record
        if dateChosen == "":
            dateChosen = currentDate
            WeekNum = int(currentDate.strftime("%W"))
        else:
            dateChosen = datetime.strptime(dateChosen, "%Y-%m-%d").date()
            WeekNum = int(dateChosen.strftime("%W"))
        ExpireClassID = Booking().getExpiredClasses(WeekNum)
        datesForChosenWeek = Booking().getCorrespondingDates(WeekNum)
        myBookingsByWeeknum = member.getMyBookingsByWeeknum(WeekNum)
        return render_template(
            "myBooking.html",
            username=username,
            dbcols=myBookingsByWeeknum["dbcols"],
            dbresult=myBookingsByWeeknum["result"],
            dateChosen=dateChosen,
            dbresultDate=datesForChosenWeek,
            MemberID=member.member_id,
            ExpireClassID=ExpireClassID,
        )
    else:
        return redirect(url_for("auth.home"))


######   My Message   ######
@member.route("/myMessage")
def myMessage():
    if "username" in session:
        username = session["username"]
        member = Member(session["username"])
        member.getMemberDetails()
        memberJoinDay_int = member.gym_join_date.strftime("%d")
        weeklyupdate = member.getWeeklyUpdate()
        messageList = member.getMyMessages()
        return render_template(
            "myMessage.html",
            username=username,
            messageList=messageList,
            memberIsReceivingNotifation=member.receiving_notifications,
            weeklyupdate=weeklyupdate,
            memberStatus=member.member_status,
            current_time=datetime.now(),
            today_date_int=int( datetime.now().day),
            memberJoinDay_int=int(memberJoinDay_int),
        )
    else:
        return redirect(url_for("auth.home"))


######   My Membership   ######
@member.route("/membership")
def membership():
    if "username" in session:
        username = session["username"]
        return render_template("membership.html", username=username)
    else:
        return render_template("membership.html")


@member.route("/membership/mySubscription")
def mySubscription():
    if "username" in session:
        member = Member(session["username"])
        member_details = member.getMemberDetails()
        ExpiryDate = member.getSubscriptionEndDate()
        if ExpiryDate != None:
            if ExpiryDate >= currentDate and member.authority_on_collecting_fees == "No":
                daystoExpiry = abs(ExpiryDate - currentDate).days
                validperiodNotice = (
                    f" Your subscription status will become inactive on {ExpiryDate}."
                )
                daysRemain = f"Your current subscription still has a validity of {daystoExpiry} days and you will not be auto charged for the next month"
                return render_template(
                    "mySubscription.html",
                    username=session["username"],
                    select_result=member_details,
                    validperiodNotice=validperiodNotice,
                    daysRemain=daysRemain,
                )

            elif ExpiryDate >= currentDate and member.authority_on_collecting_fees == "Yes":
                DeductionNotice = (
                    f"You subscription will be auto renewed on {ExpiryDate}."
                )
                return render_template(
                    "mySubscription.html",
                    username=session["username"],
                    select_result=member_details,
                    DeductionNotice=DeductionNotice,
                )
            elif ExpiryDate < currentDate:
                ExpiryNotice = f" Your account has expired on {ExpiryDate}."
                return render_template(
                    "mySubscription.html",
                    username=session["username"],
                    select_result=member_details,
                    ExpiryNotice=ExpiryNotice,
                    ExpiryDate=ExpiryDate,
                    MemberStatus=member.member_status,
                )
        else:
            if member.member_status == "Inactive":
                flash(
                    "You have never activated a subscription before. Please contact the manager to activate your first subscription.",
                    "ContactManager",
                )
                return redirect("/membership")

    else:
        return redirect(url_for("auth.home"))


@member.route("/membership/CancelSubscription", methods=["POST"])
def CancelSubscription():
    if "username" in session:
        member = Member(session["username"])
        member.getMemberDetails()
        TaskToDo = request.form["TaskToDo"]
        ExpiryDate = member.getSubscriptionEndDate()
        delta = ExpiryDate - currentDate

        if TaskToDo == "Deactivate":
            member.deactivateSubscription()
            flash(
                "You have successfully cancelled the Auto-renew for your subscription!",
                "cancelSubSuccess",
            )

        elif TaskToDo == "Reactivate":
            member.activateSubscription()
            flash(
                "You have successfully reactivated the auto-renew for your subscription!",
                "ReActSuccess",
            )

        return redirect("/membership/mySubscription")
    else:
        return render_template("membership.html")


