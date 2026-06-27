SmartEMS - Employee Management System
======================================

Hệ thống quản lý nhân viên với các chức năng: Điểm danh, Nghỉ phép, Lương thưởng, Quản lý hồ sơ.


YÊU CẦU HỆ THỐNG
----------------

- Python 3.8 trở lên (Tải tại: https://www.python.org/downloads/)
- pip (đi kèm với Python)


CÀI ĐẶT
-------

1. Tải dự án

   Cách 1 - Dùng Git:
   git clone https://github.com/yourusername/employee-management.git
   cd employee-management

   Cách 2 - Tải file ZIP:
   - Truy cập repository trên GitHub
   - Nhấn nút Code -> Download ZIP
   - Giải nén file ZIP

2. Cài đặt Python (nếu chưa có)

   Windows:
   - Tải Python từ: https://www.python.org/downloads/
   - Chạy file cài đặt
   - QUAN TRỌNG: Đánh dấu chọn "Add Python to PATH"
   - Nhấn "Install Now"

   macOS:
   brew install python

   Linux (Ubuntu/Debian):
   sudo apt update
   sudo apt install python3 python3-pip

3. Cài đặt thư viện

   Mở terminal trong thư mục dự án và chạy:
   pip install -r requirements.txt

   Nếu gặp lỗi, thử:
   pip3 install -r requirements.txt

4. Kiểm tra cài đặt

   python --version
   pip --version


CHẠY ỨNG DỤNG
-------------

1. Chạy local
   python app.py
   Hoặc:
   python3 app.py

2. Truy cập
   Mở trình duyệt: http://localhost:5000

3. Dừng ứng dụng
   Nhấn Ctrl + C trong terminal.


TÀI KHOẢN MẶC ĐỊNH
------------------

Vai trò   | Username | Password
----------|----------|----------
Admin     | admin    | admin123

Lưu ý: Tài khoản admin được tự động tạo khi chạy lần đầu.


HƯỚNG DẪN SỬ DỤNG
------------------

1. Đăng nhập
   - Truy cập http://localhost:5000
   - Nhập Username và Password
   - Nhấn "Đăng nhập"
