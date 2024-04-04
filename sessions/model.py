from database import db_manager
from datetime import timedelta, date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

class Class:
    def __init__(self,class_id = None,class_name = None,trainer_fullname = None,class_date = None,class_weekday = None,class_starttime = None,class_endtime = None,class_datetime = None,trainer_id = None,class_code = None,space_remaining = None,space_capacity = None,class_desc = None):
        self.class_id = class_id
        self.class_name = class_name
        self.trainer_fullname = trainer_fullname
        self.class_date = class_date
        self.class_weekday = class_weekday
        self.class_starttime = class_starttime
        self.class_endtime = class_endtime
        self.class_datetime = class_datetime
        self.trainer_id = trainer_id
        self.class_code = class_code
        self.space_remaining = space_remaining
        self.space_capacity = space_capacity
        self.class_desc = class_desc
        self.getClassInfoByID()
        
    def getClassInfoByID(self):
        if self.class_id == None:
            return False
        result = db_manager.execute_query(
                    """
                                select distinct t.ClassID,c.ClassName,concat(tr.Firstname,' ',tr.LastName) as 'Trainer Name',DATE_FORMAT(t.ClassDate,'%d-%b-%Y'),WeekDayTable.WeekDay,t.StartTime,t.EndTime,CONCAT(ClassDate, ' ', StartTime) AS 'DateTime',tr.TrainerID,c.ClassCode,
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
                    (self.class_id,),
                )
        classInfoByID = result["result"]
        self.class_id = classInfoByID[0][0]
        self.class_name = classInfoByID[0][1]
        self.trainer_fullname = classInfoByID[0][2]
        self.class_date = classInfoByID[0][3]
        self.class_weekday = classInfoByID[0][4]
        self.class_starttime = classInfoByID[0][5]
        self.class_endtime = classInfoByID[0][6]
        self.class_datetime = classInfoByID[0][7]
        self.trainer_id = classInfoByID[0][-5]
        self.class_code = classInfoByID[0][-4]
        self.space_remaining = classInfoByID[0][-3]
        self.space_capacity = classInfoByID[0][-2]
        self.class_desc = classInfoByID[0][-1]
        return classInfoByID
    
    

class Timetable:
    def __init__(self):
        self.currentDate = date.today()
        self.currentTime = datetime.now(pytz.timezone('Pacific/Auckland')).strftime("%Y-%m-%d %H:%M:%S")
    
    def getMaxAvailableDate(self):
        three_weeks = timedelta(weeks=3)
        maxdate = self.currentDate + three_weeks
        return maxdate
    
    def getWeeknumByDateChosen(self,dateChosen):
        if dateChosen=="" :
            dateChosen=self.currentDate
            weekNum=int(self.currentDate.strftime("%W"))
        else:
            dateChosen=datetime.strptime(dateChosen, '%Y-%m-%d').date()
            weekNum=int(dateChosen.strftime("%W"))
        weekNum=f"{weekNum}%"
        return weekNum
    
    def getExpiredClasses(self,WeekNum):
        expiredClassInfo = db_manager.execute_query("SELECT * FROM Timetable WHERE CONCAT(ClassDate, ' ', StartTime) < %s AND WEEKOFYEAR(ClassDate) = %s",(self.currentTime,WeekNum))['result']
        ExpireClassID=[ str(x[0]) for x in expiredClassInfo]
        return ExpireClassID
    
    def getCorrespondingDates(self,WeekNum):
        WeekNum=f"{WeekNum}%"
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
            """,(WeekNum,))
        return dbresultDate['result'][0]
    
    def getGroupSessionsTimetableByWeeknum(self,weekNum):
        result = db_manager.execute_query("""
                SELECT Timetable.StartTime, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
                FROM
                (SELECT DISTINCT StartTime FROM Timetable) AS Timetable
                LEFT JOIN
                (SELECT
                t.StartTime,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Monday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',t.ClassCode,',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END) AS Monday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Tuesday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',t.ClassCode,',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END) AS Tuesday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Wednesday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',t.ClassCode,',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END) AS Wednesday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Thursday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',t.ClassCode,',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END) AS Thursday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Friday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',t.ClassCode,',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END) AS Friday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Saturday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',t.ClassCode,',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END) AS Saturday,
                MAX(CASE WHEN WeekDayTable.WeekDay = 'Sunday' THEN CONCAT(t.ClassID,',',c.ClassName,',',concat(tr.Firstname,' ',tr.LastName),',',t.ClassCode,',',c.Capacity-ifnull(RemainTable.TotalBooked,0),',',c.Capacity) ELSE NULL END) AS Sunday
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
                WEEKOFYEAR(t.ClassDate) Like %s
                and c.ClassCode!=1
                GROUP BY t.StartTime) AS Table2
                ON Timetable.StartTime = Table2.StartTime
                ORDER BY Timetable.StartTime;
                                        """,(weekNum,))
        dbresult=result['result']
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
            'dbcols':result['dbcols'],
            'result':listdb
        }
        
    def getPersonClassTimetableByWeeknum(self,weekNum):
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
            (weekNum,),
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
        return {
            'dbcols':dbcols,
            'result':listdb
        }
        
    
class NoticeSender:
    def __init__(self, member_id = None,class_id = None):
        self.member_id = member_id
        self.current_time = datetime.now()
        self.related_classinfo = Class(class_id)
    
    def sendBookingNotice(self):
        db_manager.execute_query(
                    f"INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s, 'ClassBooked', 'You have booked {self.related_classinfo.class_name}({self.related_classinfo.class_datetime}) successfully!')",
                    (self.member_id, self.current_time),
                    commit=True,
                )
        if self.related_classinfo.class_code == 1:
            db_manager.execute_query(
                "INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s, 'Deduction', 'You have made a payment with $50')",
                (self.member_id, self.current_time),
                commit=True,
            )
    

    def sendCancelBookingNotice(self):
        db_manager.execute_query(
                f"INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s,'CancelClass', '{self.related_classinfo.class_name}({self.related_classinfo.class_datetime}) has been cancelled successfully.')",
                (self.member_id, self.current_time),
                commit=True,
            )
    def sendRefundNotice(self):
        db_manager.execute_query(
            f"INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s,'Refund', 'We have refunded you $50 for {self.related_classinfo.class_name}({self.related_classinfo.class_datetime})')",
            (self.member_id, self.current_time),
            commit=True,
        )
    
    def sendNoRefundNotice(self):
        db_manager.execute_query(
                f"INSERT into Notice(MemberID,NoticeDate,NoticeSubject,Content) VALUES( %s, %s,'Refund', 'The cancellation of {self.related_classinfo.class_name}({self.related_classinfo.class_datetime}) is ineligible for a refund due to it occurring within seven days of the scheduled date.')",
                (self.member_id, self.current_time),
                commit=True,
            ) 
        
                
        
