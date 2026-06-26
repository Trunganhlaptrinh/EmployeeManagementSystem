# model/database.py
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='employee.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Bảng nhân viên
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                position TEXT,
                department TEXT,
                base_salary REAL DEFAULT 0
            )
        ''')
        
        # Bảng điểm danh
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                date TEXT,
                check_in TEXT,
                check_out TEXT,
                status TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Bảng nghỉ phép
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                from_date TEXT,
                to_date TEXT,
                reason TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Bảng lương
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                month TEXT,
                base_salary REAL,
                bonus REAL,
                deduction REAL,
                total REAL,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')
        
        # Thêm tài khoản admin mặc định
        cursor.execute('''
            INSERT OR IGNORE INTO employees 
            (username, password, name, position, department, base_salary) 
            VALUES ('admin', 'admin123', 'Admin', 'Manager', 'IT', 10000000)
        ''')
        
        conn.commit()
        conn.close()
    
    # === EMPLOYEE METHODS ===
    def get_employee_by_username(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    def get_employee_by_id(self, emp_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employees WHERE id = ?', (emp_id,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    def get_all_employees(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM employees')
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    # === ATTENDANCE METHODS ===
    def check_in(self, employee_id):
        today = datetime.now().strftime('%Y-%m-%d')
        check_in_time = datetime.now().strftime('%H:%M:%S')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Kiểm tra đã check-in chưa
        cursor.execute('''
            SELECT * FROM attendances 
            WHERE employee_id = ? AND date = ?
        ''', (employee_id, today))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return False, "Already checked in today"
        
        cursor.execute('''
            INSERT INTO attendances (employee_id, date, check_in, status)
            VALUES (?, ?, ?, ?)
        ''', (employee_id, today, check_in_time, 'present'))
        
        conn.commit()
        conn.close()
        return True, "Check-in successful"
    
    def check_out(self, employee_id):
        today = datetime.now().strftime('%Y-%m-%d')
        check_out_time = datetime.now().strftime('%H:%M:%S')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE attendances 
            SET check_out = ? 
            WHERE employee_id = ? AND date = ?
        ''', (check_out_time, employee_id, today))
        
        conn.commit()
        conn.close()
        return True, "Check-out successful"
    
    def get_attendance_today(self, employee_id):
        today = datetime.now().strftime('%Y-%m-%d')
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM attendances 
            WHERE employee_id = ? AND date = ?
        ''', (employee_id, today))
        row = cursor.fetchone()
        conn.close()
        return row
    
    def get_attendance_history(self, employee_id, month=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if month:
            cursor.execute('''
                SELECT * FROM attendances 
                WHERE employee_id = ? AND date LIKE ?
                ORDER BY date DESC
            ''', (employee_id, f'{month}%'))
        else:
            cursor.execute('''
                SELECT * FROM attendances 
                WHERE employee_id = ? 
                ORDER BY date DESC LIMIT 30
            ''', (employee_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    # === LEAVE METHODS ===
    def request_leave(self, employee_id, from_date, to_date, reason):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leaves (employee_id, from_date, to_date, reason)
            VALUES (?, ?, ?, ?)
        ''', (employee_id, from_date, to_date, reason))
        conn.commit()
        conn.close()
        return True, "Leave request submitted"
    
    def get_leave_requests(self, employee_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if employee_id:
            cursor.execute('''
                SELECT * FROM leaves WHERE employee_id = ? 
                ORDER BY from_date DESC
            ''', (employee_id,))
        else:
            cursor.execute('SELECT * FROM leaves ORDER BY from_date DESC')
        rows = cursor.fetchall()
        conn.close()
        return rows
    
    def approve_leave(self, leave_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE leaves SET status = 'approved' WHERE id = ?
        ''', (leave_id,))
        conn.commit()
        conn.close()
        return True, "Leave approved"
    
    def reject_leave(self, leave_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE leaves SET status = 'rejected' WHERE id = ?
        ''', (leave_id,))
        conn.commit()
        conn.close()
        return True, "Leave rejected"
    
    # === SALARY METHODS ===
    def calculate_salary(self, employee_id, month):
        emp = self.get_employee_by_id(employee_id)
        if not emp:
            return None
        
        base_salary = emp[6]  # base_salary column
        
        # Đếm số ngày làm việc trong tháng
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM attendances 
            WHERE employee_id = ? AND date LIKE ? AND status = 'present'
        ''', (employee_id, f'{month}%'))
        work_days = cursor.fetchone()[0]
        
        # Đếm số ngày nghỉ có phép trong tháng
        cursor.execute('''
            SELECT COUNT(*) FROM leaves 
            WHERE employee_id = ? AND status = 'approved' 
            AND (from_date LIKE ? OR to_date LIKE ?)
        ''', (employee_id, f'{month}%', f'{month}%'))
        leave_days = cursor.fetchone()[0]
        conn.close()
        
        # Tính lương (giả định 26 ngày công/tháng)
        daily_rate = base_salary / 26
        bonus = work_days * 50000  # Thưởng 50k/ngày công
        deduction = leave_days * daily_rate  # Trừ lương ngày nghỉ
        
        total = base_salary + bonus - deduction
        
        # Lưu vào bảng salaries
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO salaries 
            (employee_id, month, base_salary, bonus, deduction, total)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (employee_id, month, base_salary, bonus, deduction, total))
        conn.commit()
        conn.close()
        
        return {
            'base_salary': base_salary,
            'work_days': work_days,
            'leave_days': leave_days,
            'bonus': bonus,
            'deduction': deduction,
            'total': total
        }
    
    def get_salary_history(self, employee_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM salaries 
            WHERE employee_id = ? 
            ORDER BY month DESC
        ''', (employee_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    # model/database.py - Thêm vào cuối class Database

    def create_user(self, username, password, name, position='Nhân viên', department='', base_salary=0):
        """Tạo tài khoản user mới"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Kiểm tra username đã tồn tại chưa
        cursor.execute('SELECT * FROM employees WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Username đã tồn tại"
        
        # Thêm user mới (mặc định position là 'Nhân viên')
        cursor.execute('''
            INSERT INTO employees (username, password, name, position, department, base_salary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, password, name, position, department, base_salary))
        
        conn.commit()
        conn.close()
        return True, "Tạo tài khoản thành công!"