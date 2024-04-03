from database import db_manager


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
        
    def checkMemberPassword(self,email,member_password):
        sql = """SELECT * FROM Member WHERE Email = %s AND MemberPassword = %s """
        result = db_manager.execute_query(sql, (email,member_password))['result']
        if result:
            return True
        else: 
            return False
         
    def fetchMemberDetails(self):
        sql = """SELECT * FROM Member WHERE Email = %s"""
        result = db_manager.execute_query(sql, (self.email,))['result']
        print('result',result)
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
            return True
        return False
    
    def resetPassword(self,newPassword):
        sql = """UPDATE Member SET MemberPassword = %s WHERE Email = %s """
        db_manager.execute_query(sql, (newPassword, self.email),commit=True)

