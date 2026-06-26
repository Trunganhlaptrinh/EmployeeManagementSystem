# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from controller.employee_controller import EmployeeController
from datetime import datetime
import os

# === CẤU HÌNH APP ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'view', 'templates'),
            static_folder=os.path.join(BASE_DIR, 'view', 'static'))
app.secret_key = 'your-secret-key-here'

controller = EmployeeController()

# === AUTH ROUTES ===

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, message = controller.login(username, password)
        if success:
            user = controller.get_current_user()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['name'] = user['name']
            session['position'] = user['position']
            session['department'] = user['department']
            session['is_admin'] = (user['username'] == 'admin')
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error=message)
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        name = request.form.get('name', '').strip()
        
        from util.validation import Validation
        valid, msg = Validation.validate_register(username, password, confirm_password, name)
        if not valid:
            return render_template('register.html', error=msg)
        
        success, msg = controller.register_user(username, password, name)
        if success:
            return render_template('register.html', success=msg)
        else:
            return render_template('register.html', error=msg)
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    controller.logout()
    return redirect(url_for('login'))

# === DASHBOARD ===

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    today = datetime.now().strftime('%Y-%m-%d')
    month = datetime.now().strftime('%Y-%m')
    
    attendance = controller.get_today_attendance(user_id)
    attendances = controller.get_attendance_history(user_id, month)
    work_days = sum(1 for a in attendances if a[5] == 'present')
    total_days = len(attendances) or 1
    
    leaves = controller.get_my_leaves(user_id)
    approved_leaves = sum(1 for l in leaves if l[5] == 'approved')
    pending_leaves = sum(1 for l in leaves if l[5] == 'pending')
    
    salary_history = controller.get_salary_history(user_id)
    salary = None
    for s in salary_history:
        if s[2] == month:
            salary = f"{s[6]:,.0f}"
            break
    
    return render_template('dashboard.html',
                         user=session,
                         today=today,
                         attendance=attendance,
                         work_days=work_days,
                         total_days=total_days,
                         approved_leaves=approved_leaves,
                         pending_leaves=pending_leaves,
                         salary=salary)

# === ATTENDANCE ===

@app.route('/attendance')
def attendance():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    attendances = controller.get_attendance_history(user_id, month)
    
    return render_template('attendance.html',
                         attendances=attendances,
                         month=month)

@app.route('/attendance/check-in', methods=['POST'])
def check_in():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    success, message = controller.check_in(session['user_id'])
    return redirect(url_for('attendance'))

@app.route('/attendance/check-out', methods=['POST'])
def check_out():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    success, message = controller.check_out(session['user_id'])
    return redirect(url_for('attendance'))

# === LEAVE ===

@app.route('/leave')
def leave():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    leaves = controller.get_my_leaves(session['user_id'])
    return render_template('leave.html', leaves=leaves)

@app.route('/leave/request', methods=['POST'])
def request_leave():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from_date = request.form.get('from_date')
    to_date = request.form.get('to_date')
    reason = request.form.get('reason')
    
    success, message = controller.request_leave(session['user_id'], from_date, to_date, reason)
    return redirect(url_for('leave'))

# === SALARY ===

@app.route('/salary')
def salary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    current_month = datetime.now().strftime('%Y-%m')
    history = controller.get_salary_history(user_id)
    
    return render_template('salary.html',
                         month=current_month,
                         history=history)

@app.route('/salary/calculate', methods=['POST'])
def calculate_salary():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    month = request.form.get('month', datetime.now().strftime('%Y-%m'))
    controller.calculate_salary(session['user_id'], month)
    return redirect(url_for('salary'))

# === ADMIN - QUẢN LÝ USER ===

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or session.get('username') != 'admin':
        return "Bạn không có quyền truy cập", 403
    
    users = controller.get_all_employees()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/create', methods=['GET', 'POST'])
def admin_create_user():
    if 'user_id' not in session or session.get('username') != 'admin':
        return "Bạn không có quyền truy cập", 403
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        position = request.form.get('position', 'Nhân viên')
        department = request.form.get('department', '')
        base_salary = float(request.form.get('base_salary', 0) or 0)
        
        from util.validation import Validation
        valid, msg = Validation.validate_register(username, password, password, name)
        if not valid:
            return render_template('admin_user_form.html', 
                                 error=msg, 
                                 user={'username': username, 'name': name, 
                                       'position': position, 'department': department, 
                                       'base_salary': base_salary},
                                 mode='create')
        
        success, msg = controller.register_user(username, password, name)
        if success:
            conn = controller.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE employees 
                SET position = ?, department = ?, base_salary = ?
                WHERE username = ?
            ''', (position, department, base_salary, username))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_users'))
        else:
            return render_template('admin_user_form.html', error=msg, mode='create')
    
    return render_template('admin_user_form.html', mode='create')

@app.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
def admin_edit_user(user_id):
    if 'user_id' not in session or session.get('username') != 'admin':
        return "Bạn không có quyền truy cập", 403
    
    user_data = controller.db.get_employee_by_id(user_id)
    if not user_data:
        return "User không tồn tại", 404
    
    user = {
        'id': user_data[0],
        'username': user_data[1],
        'name': user_data[3],
        'position': user_data[4] or 'Nhân viên',
        'department': user_data[5] or '',
        'base_salary': user_data[6] or 0
    }
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        position = request.form.get('position', 'Nhân viên')
        department = request.form.get('department', '')
        base_salary = float(request.form.get('base_salary', 0) or 0)
        
        if not name:
            return render_template('admin_user_form.html', 
                                 error="Họ tên không được để trống",
                                 user=user,
                                 mode='edit')
        
        conn = controller.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE employees 
            SET name = ?, position = ?, department = ?, base_salary = ?
            WHERE id = ?
        ''', (name, position, department, base_salary, user_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_users'))
    
    return render_template('admin_user_form.html', user=user, mode='edit')

@app.route('/admin/user/<int:user_id>/delete')
def admin_delete_user(user_id):
    if 'user_id' not in session or session.get('username') != 'admin':
        return "Bạn không có quyền truy cập", 403
    
    user = controller.db.get_employee_by_id(user_id)
    if user and user[1] == 'admin':
        return "Không thể xóa tài khoản admin", 403
    
    conn = controller.db.get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM employees WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_users'))

# === CHẠY APP ===
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)