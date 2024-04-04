from database import db_manager
from datetime import  date,datetime
from dateutil.relativedelta import relativedelta
import pytz

class Member:
    def __init__(self, email = None, member_password = None, member_id = None,first_name=None, last_name=None, physical_address=None, phone=None, date_of_birth=None, emergency_contact_name=None, emergency_contact_number=None, medical_conditions=None, gym_join_date=None, receiving_notifications=None, authority_on_collecting_fees=None, bank_name=None, bank_account_holder_name=None, bank_account_number=None, member_status=None, member_notes=None):
        self.email = email
        self.member_password = member_password
        self.member_id = member_id
        self.first_name = first_name
        self.last_name = last_name
        self.physical_address = physical_address
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.emergency_contact_name = emergency_contact_name
        self.emergency_contact_number = emergency_contact_number
        self.medical_conditions = medical_conditions
        self.gym_join_date = gym_join_date
        self.receiving_notifications = receiving_notifications
        self.authority_on_collecting_fees = authority_on_collecting_fees
        self.bank_name = bank_name
        self.bank_account_holder_name = bank_account_holder_name
        self.bank_account_number = bank_account_number
        self.member_status = member_status
        self.member_notes = member_notes

         
    def getMemberDetails(self):
        sql = """SELECT * FROM Member WHERE Email = %s"""
        result = db_manager.execute_query(sql, (self.email,))['result']
        if result:
            self.member_id = result[0][0]
            self.first_name = result[0][1]
            self.last_name = result[0][2]
            self.email = result[0][3]
            self.physical_address = result[0][4]
            self.phone = result[0][5]
            self.date_of_birth = result[0][6]
            self.emergency_contact_name = result[0][7]
            self.emergency_contact_number = result[0][8]
            self.medical_conditions = result[0][9]
            self.gym_join_date = result[0][10]
            self.receiving_notifications = result[0][11]
            self.member_password = result[0][12]
            self.authority_on_collecting_fees = result[0][13]
            self.bank_name = result[0][14]
            self.bank_account_holder_name = result[0][-4]
            self.bank_account_number = result[0][-3]
            self.member_status = result[0][-2]
            self.member_notes = result[0][-1]
            return result[0]
        return False
    
    
    def updateProfile(self,formData):
        sql="""update Member set FirstName=%s, LastName=%s,Email=%s, PhysicalAddress=%s, Phone=%s, DateOfBirth=%s,
        EmergencyContactName=%s, EmergencyContactNumber=%s, MedicalConditions=%s, ReceivingNotifications=%s,
        AuthorityOnCollectingFees=%s, BankName=%s, BankAccountHolderName=%s, BankAccountNumber=%s ,MemberNotes=%s
        where memberID=%s"""
        db_manager.execute_query(sql,(formData['firstname'],formData['lastname'],formData['email'],formData['physicaladdress'],formData['phone'],formData['birthdate'],formData['emergencycontactname'],formData['emergencycontactnumber'],formData['medicalconditions'],formData['receivingnotifications'],formData['authorityoncollectingfees'],formData['bankname'],formData['bankaccountholdername'],formData['bankaccountnumber'],formData['notes'],formData['memberID']),commit=True)
        self.getMemberDetails()
        
    def getWeeklyUpdate(self):
        sql_weeklyupdate = (
            """SELECT * FROM weeklyupdate ORDER BY updateTime DESC LIMIT 1 """
        )
        weeklyupdate = db_manager.execute_query(sql_weeklyupdate)["result"]
        return weeklyupdate
    
    def getMyMessages(self):
        sql_notice = """SELECT NoticeSubject, Content, NoticeDate FROM Notice
                WHERE MemberID=%s
                ORDER BY NoticeDate DESC
                LIMIT 60 """
        messageList = db_manager.execute_query(sql_notice, (self.member_id,))["result"]
        return messageList
    
    def getSubscriptionEndDate(self):
        end_subscription_date = db_manager.execute_query(
            """select distinct max(SubscriptionEndDate) from Subscription
                    where memberID=%s""",
            (self.member_id,),
        )["result"][0][0]
        return end_subscription_date
    
    def deactivateSubscription(self):
        db_manager.execute_query(
        """UPDATE Member SET AuthorityOnCollectingFees ="No"
                where MemberID=%s """,
        (self.member_id,),
        commit=True,
        )
        self.getMemberDetails()
        
    def activateSubscription(self):
        ExpiryDate = self.getSubscriptionEndDate()
        Today = date.today()
        db_manager.execute_query(
                """UPDATE Member SET MemberStatus = 'Active', AuthorityOnCollectingFees ="Yes"
                            where MemberID=%s """,
                (self.member_id,),
                commit=True,
            )
        if ExpiryDate < Today:
            # get new expiry date
            NewExpiryDate = Today + relativedelta(months=1)
            # insert new subscription data into db
            db_manager.execute_query(
                """INSERT INTO Subscription (MemberID, SubscriptionStartDate, SubscriptionEndDate, PaymentAmount, IsPaid)
                            VALUES(%s,%s,%s,100,1)""",
                (self.member_id, Today, NewExpiryDate),
                commit=True,
            )
        self.getMemberDetails()
        
  
class Booking:
    def __init__(self,member_id = None):
       self.member_id = member_id
       self.currentTime = datetime.now(pytz.timezone('Pacific/Auckland')).strftime("%Y-%m-%d %H:%M:%S")
    
    def getMyBookingsByWeeknum(self,WeekNum):
        result = db_manager.execute_query("""
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
                ORDER BY Timetable.StartTime;""",(self.member_id,WeekNum))
        dbcols=result['dbcols']
        dbresult=result['result']
        print('dbresult',dbresult)
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
        return {
            'dbcols': dbcols,
            'result':listdb
        }
       
    def getMyBookedGroupSessionsIDs(self):
        result = db_manager.execute_query("SELECT ClassID FROM Booking WHERE MemberID = %s",(self.member_id,))
        result=result['result']
        myBookedGroupSessionsIDs=[ str(x[0]) for x in result]
        return myBookedGroupSessionsIDs
    
    def addBookingByID(self,classID):
        db_manager.execute_query(
                    "insert into Booking (MemberID,ClassID,IsPaid,BookingStatus) values(%s,%s,'0','Current')",
                    (self.member_id, classID),
                    commit=True,
                )
        
    def addPTsessionByID(self,classID):
        sql_addBooking = """INSERT INTO Booking(MemberID,ClassID,IsPaid,BookingStatus)
                            VALUES(%s,%s,%s,%s) """
        db_manager.execute_query(
            sql_addBooking, (self.member_id, classID, 1, "Current"), commit=True
        )
    
    def cancelBookingReleaseSpace(self,classID):
        sql = """DELETE FROM Booking
                WHERE MemberID = %s AND ClassID = %s """
        db_manager.execute_query(sql, (self.member_id, classID), commit=True)
        
        
    # def cancelBookingNotReleaseSpace(self,classID):
    #     sql = """update Booking set BookingStatus='Cancelled'
    #             where ClassID=%s and MemberID=%s"""
    #     db_manager.execute_query(sql, (classID, self.member_id), commit=True)  
