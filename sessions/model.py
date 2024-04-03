from database import db_manager
from datetime import timedelta, date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

class Timetable:
    def __init__(self,member_id = None):
        self.member_id = member_id
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