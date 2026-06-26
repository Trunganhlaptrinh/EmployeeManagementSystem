# controller/employee_controller.py
from model.database import Database
from util.validation import Validation
from datetime import datetime

class EmployeeController:
    def __init__(self):
        self.db = Database()
        self.valid = Validation()
        self.current_user = None
    
    # === AUTH ===
    def login(self, username, password):
        # Validate
        valid, msg = self.valid.validate_username(username)
        if not valid:
            return False, msg
        valid, msg = self.valid.validate_password(password)
        if not valid:
            return False, msg
        
        # Check in database
        user = self.db.get_employee_by_username(username)
        if not user:
            return False, "Username not found"
        
        if user[2] != password:  # password column
            return False, "Incorrect password"
        
        self.current_user = {
            'id': user[0],
            'username': user[1],
            'name': user[3],
            'position': user[4],
            'department': user[5],
            'base_salary': user[6]
        }
        return True, "Login successful"

    def register_user(self, username, password, name):
        """Đăng ký tài khoản user mới"""
        # Hash password trong thực tế, nhưng đơn giản hóa
        return self.db.create_user(username, password, name)
    
    def logout(self):
        self.current_user = None
        return True, "Logout successful"
    
    def get_current_user(self):
        return self.current_user
    
    # === EMPLOYEE ===
    def get_all_employees(self):
        rows = self.db.get_all_employees()
        employees = []
        for row in rows:
            employees.append({
                'id': row[0],
                'username': row[1],
                'name': row[3],
                'position': row[4],
                'department': row[5],
                'base_salary': row[6]
            })
        return employees
    
    # === ATTENDANCE ===
    def check_in(self, employee_id):
        return self.db.check_in(employee_id)
    
    def check_out(self, employee_id):
        return self.db.check_out(employee_id)
    
    def get_today_attendance(self, employee_id):
        return self.db.get_attendance_today(employee_id)
    
    def get_attendance_history(self, employee_id, month=None):
        return self.db.get_attendance_history(employee_id, month)
    
    # === LEAVE ===
    def request_leave(self, employee_id, from_date, to_date, reason):
        # Validate dates
        valid, msg = self.valid.validate_date(from_date)
        if not valid:
            return False, msg
        valid, msg = self.valid.validate_date(to_date)
        if not valid:
            return False, msg
        
        if from_date > to_date:
            return False, "From date must be before to date"
        
        if self.valid.is_empty(reason):
            return False, "Reason cannot be empty"
        
        return self.db.request_leave(employee_id, from_date, to_date, reason)
    
    def get_my_leaves(self, employee_id):
        return self.db.get_leave_requests(employee_id)
    
    def get_all_leave_requests(self):
        return self.db.get_leave_requests()
    
    def approve_leave(self, leave_id):
        return self.db.approve_leave(leave_id)
    
    def reject_leave(self, leave_id):
        return self.db.reject_leave(leave_id)
    
    # === SALARY ===
    def calculate_salary(self, employee_id, month):
        valid, msg = self.valid.validate_month(month)
        if not valid:
            return False, msg
        result = self.db.calculate_salary(employee_id, month)
        if result is None:
            return False, "Employee not found"
        return True, result
    
    def get_salary_history(self, employee_id):
        return self.db.get_salary_history(employee_id)