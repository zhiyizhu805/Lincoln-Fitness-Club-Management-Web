from database import db_manager
from datetime import datetime

class Trainer:
    def __init__(self,email = None):
        self.email = email
        self.today = datetime.today()
        
    def getTrainerStatus(self):
        result = db_manager.execute_query("SELECT MemberStatus FROM Member WHERE Email=%s", (self.email,))["result"]
        trainerStatus = result[0][0]
        return trainerStatus
    
    def getTrainerList(self):
        sql_trainer = "SELECT TrainerID, FirstName, LastName FROM Trainer WHERE TrainerStatus='Active' ORDER BY FirstName "
        trainerList = db_manager.execute_query(sql_trainer)["result"]
        return trainerList
    
    def getTrainerTablelist(self):
        sql_timetable = """SELECT Timetable.TrainerID, Timetable.ClassDate, Timetable.StartTime, Timetable.EndTime, DAYOFWEEK(Timetable.ClassDate), Timetable.ClassID
                        FROM Timetable
                        WHERE  Timetable.ClassCode = 1 AND DATE(Timetable.ClassDate) > %s
                        ORDER BY Timetable.ClassDate"""
        timetableList = db_manager.execute_query(sql_timetable, (self.today,))["result"]
        return timetableList
    
    def getExistedSessionDate(self):
        sql_existed_session = """SELECT Timetable.ClassID, Timetable.ClassCode, Timetable.ClassDate FROM Timetable
                                INNER JOIN Booking ON Timetable.ClassID = Booking.ClassID
                                WHERE IsPaid=1  AND Timetable.ClassCode=1 AND DATE(Timetable.ClassDate) > %s """
        existedSessionData = db_manager.execute_query(sql_existed_session, (self.today,))["result"]
        existedSessionList = []
        for existedSession in existedSessionData:
            existedSessionList.append(existedSession[0])
        return existedSessionList
    

    
    