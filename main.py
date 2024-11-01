import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import mysql.connector
from tkinter import font as tkfont
import bcrypt
from datetime import datetime
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class InventoryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ thống Quản lý Kho")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")

        # Kết nối database
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="inventory_management"
        )
        self.cursor = self.conn.cursor()

        # Font styles
        self.title_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.label_font = tkfont.Font(family="Helvetica", size=12)
        self.button_font = tkfont.Font(family="Helvetica", size=10, weight="bold")

        self.current_user = None
        self.current_role = None

        self.show_login()

    def show_login(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        login_frame = tk.Frame(self.root, bg="#f0f0f0")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(login_frame, text="Đăng nhập", font=self.title_font, bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(login_frame, text="Tên đăng nhập:", font=self.label_font, bg="#f0f0f0").grid(row=1, column=0, pady=5)
        self.username_entry = tk.Entry(login_frame, font=self.label_font)
        self.username_entry.grid(row=1, column=1, pady=5)

        tk.Label(login_frame, text="Mật khẩu:", font=self.label_font, bg="#f0f0f0").grid(row=2, column=0, pady=5)
        self.password_entry = tk.Entry(login_frame, font=self.label_font, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        login_button = tk.Button(login_frame, text="Đăng nhập", command=self.login, font=self.button_font, bg="#4CAF50", fg="white")
        login_button.grid(row=3, column=0, columnspan=2, pady=10)

        register_button = tk.Button(login_frame, text="Đăng ký", command=self.show_register, font=self.button_font, bg="#2196F3", fg="white")
        register_button.grid(row=4, column=0, columnspan=2, pady=10)

    def show_register(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        register_frame = tk.Frame(self.root, bg="#f0f0f0")
        register_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(register_frame, text="Đăng ký", font=self.title_font, bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=10)

        tk.Label(register_frame, text="Tên đăng nhập:", font=self.label_font, bg="#f0f0f0").grid(row=1, column=0, pady=5)
        self.reg_username_entry = tk.Entry(register_frame, font=self.label_font)
        self.reg_username_entry.grid(row=1, column=1, pady=5)

        tk.Label(register_frame, text="Mật khẩu:", font=self.label_font, bg="#f0f0f0").grid(row=2, column=0, pady=5)
        self.reg_password_entry = tk.Entry(register_frame, font=self.label_font, show="*")
        self.reg_password_entry.grid(row=2, column=1, pady=5)

        tk.Label(register_frame, text="Xác nhận mật khẩu:", font=self.label_font, bg="#f0f0f0").grid(row=3, column=0, pady=5)
        self.reg_confirm_password_entry = tk.Entry(register_frame, font=self.label_font, show="*")
        self.reg_confirm_password_entry.grid(row=3, column=1, pady=5)

        tk.Label(register_frame, text="Vai trò:", font=self.label_font, bg="#f0f0f0").grid(row=4, column=0, pady=5)
        self.reg_role_var = tk.StringVar(register_frame)
        self.reg_role_var.set("Nhân viên kho")  # default value
        role_options = ["Nhân viên kho", "Quản lý kho", "Quản lý phần mềm"]
        role_menu = tk.OptionMenu(register_frame, self.reg_role_var, *role_options)
        role_menu.grid(row=4, column=1, pady=5)

        register_button = tk.Button(register_frame, text="Đăng ký", command=self.register, font=self.button_font, bg="#4CAF50", fg="white")
        register_button.grid(row=5, column=0, columnspan=2, pady=10)

        back_button = tk.Button(register_frame, text="Quay lại", command=self.show_login, font=self.button_font, bg="#f44336", fg="white")
        back_button.grid(row=6, column=0, columnspan=2, pady=10)

    def register(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_password_entry.get()
        role = self.reg_role_var.get()

        if not username or not password or not confirm_password:
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
            return

        if password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu không khớp")
            return

        # Check if username already exists
        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if self.cursor.fetchone():
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại")
            return

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new user into database
        try:
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                                (username, hashed_password, role))
            self.conn.commit()
            messagebox.showinfo("Thành công", "Đăng ký thành công")
            self.show_login()
        except mysql.connector.Error as err:
            messagebox.showerror("Lỗi", f"Đăng ký thất bại: {err}")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = self.cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            self.current_user = user[0]
            self.current_role = user[3]
            self.log_activity(f"Đăng nhập")
            self.create_main_window()
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng")

    def create_main_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title and user info
        title_frame = tk.Frame(main_frame, bg="#f0f0f0")
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="ew")
        title_frame.grid_columnconfigure(1, weight=1)

        title_label = tk.Label(title_frame, text=f"Hệ thống Quản lý Kho - {self.current_role}", font=self.title_font, bg="#f0f0f0", fg="#333333")
        title_label.grid(row=0, column=0, sticky="w")

        user_label = tk.Label(title_frame, text=f"Xin chào, {self.get_username()}", font=self.label_font, bg="#f0f0f0", fg="#666666")
        user_label.grid(row=0, column=1, sticky="e")

        logout_button = tk.Button(title_frame, text="Đăng xuất", command=self.logout, font=self.button_font, bg="#f44336", fg="white")
        logout_button.grid(row=0, column=2, sticky="e", padx=(10, 0))

        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg="#f0f0f0")
        buttons_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 20))

        # Buttons based on user role
        buttons = self.get_buttons_for_role()

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(buttons_frame, text=text, command=command, font=self.button_font, bg="#4CAF50", fg="white", padx=10, pady=5)
            btn.grid(row=i, column=0, sticky="ew", pady=5)

        # Table frame
        table_frame = tk.Frame(main_frame, bg="white")
        table_frame.grid(row=1, column=1, rowspan=2, sticky="nsew")

        # Create Treeview
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Tên", "Số lượng", "Vị trí"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tên", text="Tên")
        self.tree.heading("Số lượng", text="Số lượng")
        self.tree.heading("Vị trí", text="Vị trí")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Configure grid weights
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Load initial data
        self.load_data()

    def get_username(self):
        self.cursor.execute("SELECT username FROM users WHERE id = %s", (self.current_user,))
        return self.cursor.fetchone()[0]

    def logout(self):
        self.log_activity("Đăng xuất")
        self.current_user = None
        self.current_role = None
        self.show_login()

    def get_buttons_for_role(self):
        if self.current_role == "Nhân viên kho":
            return [
                ("Nhập hàng", self.import_goods),
                ("Xuất hàng", self.export_goods),
                ("Kiểm kê kho", self.inventory_check),
                ("Quản lý vị trí", self.manage_locations),
                ("Báo cáo sự cố", self.report_issue),
                ("Xem nhiệm vụ", self.view_tasks)
            ]
        elif self.current_role == "Quản lý kho":
            return [
                ("Giám sát hoạt động", self.monitor_activities),
                ("Quản lý tồn kho", self.manage_inventory),
                ("Phân công nhiệm vụ", self.assign_tasks),
                ("Xử lý sự cố", self.handle_issues),
                ("Tạo báo cáo", self.generate_report),
                ("Quản lý nhà cung cấp", self.manage_suppliers)
            ]
        elif self.current_role == "Quản lý phần mềm":
            return [
                ("Quản lý người dùng", self.manage_users),
                ("Cấu hình hệ thống", self.configure_system),
                ("Xem nhật ký", self.view_logs),
                ("Sao lưu dữ liệu", self.backup_data),
                ("Quản lý quyền truy cập", self.manage_permissions)
            ]

    def load_data(self):
        # Clear existing data
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Fetch data from database
        self.cursor.execute("SELECT * FROM inventory")
        rows = self.cursor.fetchall()

        # Insert data into treeview
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def import_goods(self):
        product_name = simpledialog.askstring("Nhập hàng", "Tên sản phẩm:")
        if product_name:
            quantity = simpledialog.askinteger("Nhập hàng", f"Số lượng {product_name}:")
            if quantity:
                location = simpledialog.askstring("Nhập hàng", f"Vị trí lưu trữ cho {product_name}:")
                if location:
                    self.cursor.execute("INSERT INTO inventory (name, quantity, location) VALUES (%s, %s, %s)",
                                        (product_name, quantity, location))
                    self.conn.commit()
                    self.load_data()
                    self.log_activity(f"Nhập hàng: {quantity} {product_name}")
                    messagebox.showinfo("Thành công", f"Đã nhập {quantity} {product_name} vào kho tại vị trí {location}")

    def  export_goods(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            product_id = item['values'][0]
            product_name = item['values'][1]
            current_quantity = item['values'][2]
            
            quantity = simpledialog.askinteger("Xuất hàng", f"Số lượng {product_name} cần xuất:")
            if quantity and quantity <= current_quantity:
                self.cursor.execute("UPDATE inventory SET quantity = quantity - %s WHERE id = %s",
                                    (quantity, product_id))
                self.conn.commit()
                self.load_data()
                self.log_activity(f"Xuất hàng: {quantity} {product_name}")
                messagebox.showinfo("Thành công", f"Đã xuất {quantity} {product_name} từ kho")
            elif quantity:
                messagebox.showerror("Lỗi", "Số lượng xuất vượt quá số lượng trong kho")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần xuất")

    def inventory_check(self):
        check_window = tk.Toplevel(self.root)
        check_window.title("Kiểm kê kho")
        check_window.geometry("600x400")

        tk.Label(check_window, text="Kiểm kê kho", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(check_window, columns=("ID", "Tên", "Số lượng hệ thống", "Số lượng thực tế"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Tên", text="Tên")
        tree.heading("Số lượng hệ thống", text="Số lượng hệ thống")
        tree.heading("Số lượng thực tế", text="Số lượng thực tế")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("SELECT id, name, quantity FROM inventory")
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=(row[0], row[1], row[2], ""))

        def update_actual_quantity():
            for item in tree.get_children():
                actual_quantity = tree.item(item)['values'][3]
                if actual_quantity:
                    self.cursor.execute("UPDATE inventory SET quantity = %s WHERE id = %s",
                                        (actual_quantity, tree.item(item)['values'][0]))
            self.conn.commit()
            self.load_data()
            self.log_activity("Cập nhật kiểm kê kho")
            messagebox.showinfo("Thành công", "Đã cập nhật số lượng thực tế")
            check_window.destroy()

        update_button = tk.Button(check_window, text="Cập nhật số lượng thực tế", command=update_actual_quantity)
        update_button.pack(pady=10)

    def manage_locations(self):
        location_window = tk.Toplevel(self.root)
        location_window.title("Quản lý vị trí")
        location_window.geometry("600x400")

        tk.Label(location_window, text="Quản lý vị trí", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(location_window, columns=("ID", "Tên", "Vị trí"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Tên", text="Tên")
        tree.heading("Vị trí", text="Vị trí")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("SELECT id, name, location FROM inventory")
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        def update_location():
            selected_item = tree.selection()
            if selected_item:
                item = tree.item(selected_item)
                product_id = item['values'][0]
                new_location = simpledialog.askstring("Cập nhật vị trí", "Nhập vị trí mới:")
                if new_location:
                    self.cursor.execute("UPDATE inventory SET location = %s WHERE id = %s",
                                        (new_location, product_id))
                    self.conn.commit()
                    self.load_data()
                    self.log_activity(f"Cập nhật vị trí sản phẩm ID {product_id}")
                    messagebox.showinfo("Thành công", "Đã cập nhật vị trí")
                    location_window.destroy()
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần cập nhật vị trí")

        update_button = tk.Button(location_window, text="Cập nhật vị trí", command=update_location)
        update_button.pack(pady=10)

    def report_issue(self):
        issue = simpledialog.askstring("Báo cáo sự cố", "Mô tả sự cố:")
        if issue:
            self.cursor.execute("INSERT INTO issues (description, reported_by) VALUES (%s, %s)",
                                (issue, self.current_user))
            self.conn.commit()
            self.log_activity("Báo cáo sự cố")
            messagebox.showinfo("Thành công", "Đã ghi nhận sự cố")

    def view_tasks(self):
        task_window = tk.Toplevel(self.root)
        task_window.title("Xem nhiệm vụ")
        task_window.geometry("600x400")

        tk.Label(task_window, text="Nhiệm vụ của bạn", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(task_window, columns=("ID", "Mô tả", "Trạng thái", "Ngày giao"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Mô tả", text="Mô tả")
        tree.heading("Trạng thái", text="Trạng thái")
        tree.heading("Ngày giao", text="Ngày giao")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("SELECT id, description, status, assigned_at FROM tasks WHERE staff_id = %s", (self.current_user,))
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        def update_task_status():
            selected_item = tree.selection()
            if selected_item:
                item = tree.item(selected_item)
                task_id = item['values'][0]
                new_status = simpledialog.askstring("Cập nhật trạng thái", "Nhập trạng thái mới (Chưa hoàn thành/Đang thực hiện/Đã hoàn thành):")
                if new_status in ["Chưa hoàn thành", "Đang thực hiện", "Đã hoàn thành"]:
                    self.cursor.execute("UPDATE tasks SET status = %s WHERE id = %s", (new_status, task_id))
                    self.conn.commit()
                    self.log_activity(f"Cập nhật trạng thái nhiệm vụ ID {task_id}")
                    messagebox.showinfo("Thành công", "Đã cập nhật trạng thái nhiệm vụ")
                    task_window.destroy()
                else:
                    messagebox.showerror("Lỗi", "Trạng thái không hợp lệ")
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhiệm vụ cần cập nhật")

        update_button = tk.Button(task_window, text="Cập nhật trạng thái", command=update_task_status)
        update_button.pack(pady=10)

    def monitor_activities(self):
        activity_window = tk.Toplevel(self.root)
        activity_window.title("Giám sát hoạt động")
        activity_window.geometry("800x600")

        tk.Label(activity_window, text="Giám sát hoạt động", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(activity_window, columns=("ID", "Hoạt động", "Người thực hiện", "Thời gian"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Hoạt động", text="Hoạt động")
        tree.heading("Người thực hiện", text="Người thực hiện")
        tree.heading("Thời gian", text="Thời gian")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("""
            SELECT a.id, a.action, u.username, a.timestamp 
            FROM activities a 
            JOIN users u ON a.user_id = u.id 
            ORDER BY a.timestamp DESC 
            LIMIT 100
        """)
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

    def manage_inventory(self):
        inventory_window = tk.Toplevel(self.root)
        inventory_window.title("Quản lý tồn kho")
        inventory_window.geometry("800x600")

        tk.Label(inventory_window, text="Quản lý tồn kho", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(inventory_window, columns=("ID", "Tên", "Số lượng", "Vị trí", "Giá trị"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Tên", text="Tên")
        tree.heading("Số lượng", text="Số lượng")
        tree.heading("Vị trí", text="Vị trí")
        tree.heading("Giá trị", text="Giá trị")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("SELECT id, name, quantity, location, price FROM inventory")
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], f"{row[2] * row[4]:.2f}"))

        def add_new_product():
            name = simpledialog.askstring("Thêm sản phẩm mới", "Tên sản phẩm:")
            if name:
                quantity = simpledialog.askinteger("Thêm sản phẩm mới", "Số lượng:")
                if quantity is not None:
                    location = simpledialog.askstring("Thêm sản phẩm mới", "Vị trí:")
                    if location:
                        price = simpledialog.askfloat("Thêm sản phẩm mới", "Giá:")
                        if price is not None:
                            self.cursor.execute("INSERT INTO inventory (name, quantity, location, price) VALUES (%s, %s, %s, %s)",
                                                (name, quantity, location, price))
                            self.conn.commit()
                            self.log_activity(f"Thêm sản phẩm mới: {name}")
                            messagebox.showinfo("Thành công", "Đã thêm sản phẩm mới")
                            inventory_window.destroy()
                            self.manage_inventory()

        add_button = tk.Button(inventory_window, text="Thêm sản phẩm mới", command=add_new_product)
        add_button.pack(pady=10)

    def assign_tasks(self):
        task_window = tk.Toplevel(self.root)
        task_window.title("Phân công nhiệm vụ")
        task_window.geometry("600x400")

        tk.Label(task_window, text="Phân công nhiệm vụ", font=self.title_font).pack(pady=10)

        self.cursor.execute("SELECT id, username FROM users WHERE role = 'Nhân viên kho'")
        staff = self.cursor.fetchall()

        staff_var = tk.StringVar(task_window)
        staff_var.set(staff[0][1] if staff else "")

        staff_menu = tk.OptionMenu(task_window, staff_var, *[s[1] for s in staff])
        staff_menu.pack(pady=5)

        task_entry = tk.Entry(task_window, font=self.label_font, width=50)
        task_entry.pack(pady=5)

        def assign_task():
            selected_staff = staff_var.get()
            task = task_entry.get()
            if selected_staff and task:
                staff_id = next(s[0] for s in staff if s[1] == selected_staff)
                self.cursor.execute("INSERT INTO tasks (staff_id, description) VALUES (%s, %s)",
                                    (staff_id, task))
                self.conn.commit()
                self.log_activity(f"Phân công nhiệm vụ cho {selected_staff}")
                messagebox.showinfo("Thành công", f"Đã phân công nhiệm vụ cho {selected_staff}")
                task_window.destroy()
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên và nhập nhiệm vụ")

        assign_button = tk.Button(task_window, text="Phân công", command=assign_task)
        assign_button.pack(pady=10)

    def handle_issues(self):
        issue_window = tk.Toplevel(self.root)
        issue_window.title("Xử lý sự cố")
        issue_window.geometry("800x600")

        tk.Label(issue_window, text="Xử lý sự cố", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(issue_window, columns=("ID", "Mô tả", "Người báo cáo", "Trạng thái", "Thời gian"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Mô tả", text="Mô tả")
        tree.heading("Người báo cáo", text="Người báo cáo")
        tree.heading("Trạng thái", text="Trạng thái")
        tree.heading("Thời gian", text="Thời gian")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("""
            SELECT i.id, i.description, u.username, i.status, i.timestamp 
            FROM issues i 
            JOIN users u ON i.reported_by = u.id
            ORDER BY i.timestamp DESC
        """)
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        def resolve_issue():
            selected_item = tree.selection()
            if selected_item:
                item = tree.item(selected_item)
                issue_id = item['values'][0]
                self.cursor.execute("UPDATE issues SET status = 'Đã xử lý' WHERE id = %s", (issue_id,))
                self.conn.commit()
                self.log_activity(f"Xử lý sự cố ID {issue_id}")
                messagebox.showinfo("Thành công", "Đã xử lý sự cố")
                issue_window.destroy()
                self.handle_issues()
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn sự cố cần xử lý")

        resolve_button = tk.Button(issue_window, text="Xử lý sự cố", command=resolve_issue)
        resolve_button.pack(pady=10)

    def generate_report(self):
        report_window = tk.Toplevel(self.root)
        report_window.title("Tạo báo cáo")
        report_window.geometry("400x300")

        tk.Label(report_window, text="Tạo báo cáo", font=self.title_font).pack(pady=10)

        report_types = ["Báo cáo tồn kho", "Báo cáo nhập xuất", "Báo cáo sự cố", "Báo cáo hoạt động"]
        report_var = tk.StringVar(report_window)
        report_var.set(report_types[0])

        report_menu = tk.OptionMenu(report_window, report_var, *report_types)
        report_menu.pack(pady=5)

        def generate():
            report_type = report_var.get()
            if report_type == "Báo cáo tồn kho":
                self.generate_inventory_report()
            elif report_type == "Báo cáo nhập xuất":
                self.generate_import_export_report()
            elif report_type == "Báo cáo sự cố":
                self.generate_issue_report()
            elif report_type == "Báo cáo hoạt động":
                self.generate_activity_report()
            report_window.destroy()

        generate_button = tk.Button(report_window, text="Tạo báo cáo", command=generate)
        generate_button.pack(pady=10)

    def generate_inventory_report(self):
        self.cursor.execute("SELECT name, quantity, price FROM inventory")
        data = self.cursor.fetchall()

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Tên sản phẩm", "Số lượng", "Giá", "Giá trị tồn kho"])
                for row in data:
                    writer.writerow([row[0], row[1], row[2], row[1] * row[2]])
            self.log_activity("Tạo báo cáo tồn kho")
            messagebox.showinfo("Thành công", f"Đã tạo báo cáo tồn kho: {filename}")

    def generate_import_export_report(self):
        self.cursor.execute("""
            SELECT a.action, i.name, a.quantity, a.timestamp 
            FROM activities a 
            JOIN inventory i ON a.product_id = i.id 
            WHERE a.action IN ('Nhập hàng', 'Xuất hàng')
            ORDER BY a.timestamp DESC
        """)
        data = self.cursor.fetchall()

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Hoạt động", "Sản phẩm", "Số lượng", "Thời gian"])
                writer.writerows(data)
            self.log_activity("Tạo báo cáo nhập xuất")
            messagebox.showinfo("Thành công", f"Đã tạo báo cáo nhập xuất: {filename}")

    def generate_issue_report(self):
        self.cursor.execute("""
            SELECT i.description, u.username, i.status, i.timestamp 
            FROM issues i 
            JOIN users u ON i.reported_by = u.id
            ORDER BY i.timestamp DESC
        """)
        data = self.cursor.fetchall()

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Mô tả sự cố", "Người báo cáo", "Trạng thái", "Thời gian"])
                writer.writerows(data)
            self.log_activity("Tạo báo cáo sự cố")
            messagebox.showinfo("Thành công", f"Đã tạo báo cáo sự cố: {filename}")

    def generate_activity_report(self):
        self.cursor.execute("""
            SELECT a.action, u.username, a.timestamp 
            FROM activities a 
            JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
        """)
        data = self.cursor.fetchall()

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Hoạt động", "Người thực hiện", "Thời gian"])
                writer.writerows(data)
            self.log_activity("Tạo báo cáo hoạt động")
            messagebox.showinfo("Thành công", f"Đã tạo báo cáo hoạt động: {filename}")

    def manage_suppliers(self):
        supplier_window = tk.Toplevel(self.root)
        supplier_window.title("Quản lý nhà cung cấp")
        supplier_window.geometry("800x600")

        tk.Label(supplier_window, text="Quản lý nhà cung cấp", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(supplier_window, columns=("ID", "Tên", "Địa chỉ", "Số điện thoại", "Email"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Tên", text="Tên")
        tree.heading("Địa chỉ", text="Địa chỉ")
        tree.heading("Số điện thoại", text="Số điện thoại")
        tree.heading("Email", text="Email")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("SELECT * FROM suppliers")
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        def add_supplier():
            name = simpledialog.askstring("Thêm nhà cung cấp", "Tên nhà cung cấp:")
            if name:
                address = simpledialog.askstring("Thêm nhà cung cấp", "Địa chỉ:")
                phone = simpledialog.askstring("Thêm nhà cung cấp", "Số điện thoại:")
                email = simpledialog.askstring("Thêm nhà cung cấp", "Email:")
                self.cursor.execute("INSERT INTO suppliers (name, address, phone, email) VALUES (%s, %s, %s, %s)",
                                    (name, address, phone, email))
                self.conn.commit()
                self.log_activity(f"Thêm nhà cung cấp: {name}")
                messagebox.showinfo("Thành công", "Đã thêm nhà cung cấp mới")
                supplier_window.destroy()
                self.manage_suppliers()

        def edit_supplier():
            selected_item = tree.selection()
            if selected_item:
                item = tree.item(selected_item)
                supplier_id = item['values'][0]
                name = simpledialog.askstring("Sửa nhà cung cấp", "Tên nhà cung cấp:", initialvalue=item['values'][1])
                if name:
                    address = simpledialog.askstring("Sửa nhà cung cấp", "Địa chỉ:", initialvalue=item['values'][2])
                    phone = simpledialog.askstring("Sửa nhà cung cấp", "Số điện thoại:", initialvalue=item['values'][3])
                    email = simpledialog.askstring("Sửa nhà cung cấp", "Email:", initialvalue=item['values'][4])
                    self.cursor.execute("UPDATE suppliers SET name = %s, address = %s, phone = %s, email = %s WHERE id = %s",
                                        (name, address, phone, email, supplier_id))
                    self.conn.commit()
                    self.log_activity(f"Sửa thông tin nhà cung cấp ID {supplier_id}")
                    messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhà cung cấp")
                    supplier_window.destroy()
                    self.manage_suppliers()
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhà cung cấp cần sửa")

        add_button = tk.Button(supplier_window, text="Thêm nhà cung cấp", command=add_supplier)
        add_button.pack(side=tk.LEFT, padx=10, pady=10)

        edit_button = tk.Button(supplier_window, text="Sửa nhà cung cấp", command=edit_supplier)
        edit_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def manage_users(self):
        user_window = tk.Toplevel(self.root)
        user_window.title("Quản lý người dùng")
        user_window.geometry("800x600")

        tk.Label(user_window, text="Quản lý người dùng", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(user_window, columns=("ID", "Tên đăng nhập", "Vai trò"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Tên đăng nhập", text="Tên đăng nhập")
        tree.heading("Vai trò", text="Vai trò")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("SELECT id, username, role FROM users")
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        def add_user():
            username = simpledialog.askstring("Thêm người dùng", "Tên đăng nhập:")
            if username:
                password = simpledialog.askstring("Thêm người dùng", "Mật khẩu:", show="*")
                role = simpledialog.askstring("Thêm người dùng", "Vai trò (Nhân viên kho/Quản lý kho/Quản lý phần mềm):")
                if password and role in ["Nhân viên kho", "Quản lý kho", "Quản lý phần mềm"]:
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                    self.cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                                        (username, hashed_password, role))
                    self.conn.commit()
                    self.log_activity(f"Thêm người dùng: {username}")
                    messagebox.showinfo("Thành công", "Đã thêm người dùng mới")
                    user_window.destroy()
                    self.manage_users()
                else:
                    messagebox.showerror("Lỗi", "Mật khẩu không được để trống và vai trò phải hợp lệ")

        def edit_user():
            selected_item = tree.selection()
            if selected_item:
                item = tree.item(selected_item)
                user_id = item['values'][0]
                new_role = simpledialog.askstring("Sửa người dùng", "Vai trò mới (Nhân viên kho/Quản lý kho/Quản lý phần mềm):", initialvalue=item['values'][2])
                if new_role in ["Nhân viên kho", "Quản lý kho", "Quản lý phần mềm"]:
                    self.cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
                    self.conn.commit()
                    self.log_activity(f"Sửa vai trò người dùng ID {user_id}")
                    messagebox.showinfo("Thành công", "Đã cập nhật vai trò người dùng")
                    user_window.destroy()
                    self.manage_users()
                else:
                    messagebox.showerror("Lỗi", "Vai trò không hợp lệ")
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng cần sửa")

        add_button = tk.Button(user_window, text="Thêm người dùng", command=add_user)
        add_button.pack(side=tk.LEFT, padx=10, pady=10)

        edit_button = tk.Button(user_window, text="Sửa người dùng", command=edit_user)
        edit_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def configure_system(self):
        config_window = tk.Toplevel(self.root)
        config_window.title("Cấu hình hệ thống")
        config_window.geometry("400x300")

        tk.Label(config_window, text="Cấu hình hệ thống", font=self.title_font).pack(pady=10)

        # Đọc cấu hình hiện tại
        self.cursor.execute("SELECT * FROM system_config")
        config = self.cursor.fetchone()

        tk.Label(config_window, text="Số lượng cảnh báo tồn kho thấp:").pack()
        low_stock_entry = tk.Entry(config_window)
        low_stock_entry.insert(0, str(config[1]))
        low_stock_entry.pack()

        tk.Label(config_window, text="Thời gian tự động sao lưu (giờ):").pack()
        backup_time_entry = tk.Entry(config_window)
        backup_time_entry.insert(0, str(config[2]))
        backup_time_entry.pack()

        def save_config():
            low_stock = int(low_stock_entry.get())
            backup_time = int(backup_time_entry.get())
            self.cursor.execute("UPDATE system_config SET low_stock_threshold = %s, auto_backup_interval = %s",
                                (low_stock, backup_time))
            self.conn.commit()
            self.log_activity("Cập nhật cấu hình hệ thống")
            messagebox.showinfo("Thành công", "Đã cập nhật cấu hình hệ thống")
            config_window.destroy()

        save_button = tk.Button(config_window, text="Lưu cấu hình", command=save_config)
        save_button.pack(pady=10)

    def view_logs(self):
        log_window = tk.Toplevel(self.root)
        log_window.title("Xem nhật ký hệ thống")
        log_window.geometry("800x600")

        tk.Label(log_window, text="Nhật ký hệ thống", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(log_window, columns=("ID", "Hoạt động", "Người dùng", "Thời gian"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Hoạt động", text="Hoạt động")
        tree.heading("Người dùng", text="Người dùng")
        tree.heading("Thời gian", text="Thời gian")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("""
            SELECT a.id, a.action, u.username, a.timestamp 
            FROM activities a 
            JOIN users u ON a.user_id = u.id 
            ORDER BY a.timestamp DESC 
            LIMIT 1000
        """)
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        def export_logs():
            filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["ID", "Hoạt động", "Người dùng", "Thời gian"])
                    for item in tree.get_children():
                        writer.writerow(tree.item(item)['values'])
                self.log_activity("Xuất nhật ký hệ thống")
                messagebox.showinfo("Thành công", f"Đã xuất nhật ký hệ thống: {filename}")

        export_button = tk.Button(log_window, text="Xuất nhật ký", command=export_logs)
        export_button.pack(pady=10)

    def backup_data(self):
        backup_window = tk.Toplevel(self.root)
        backup_window.title("Sao lưu dữ liệu")
        backup_window.geometry("400x300")

        tk.Label(backup_window, text="Sao lưu dữ liệu", font=self.title_font).pack(pady=10)

        def perform_backup():
            filename = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql")])
            if filename:
                try:
                    os.system(f"mysqldump -u root -p inventory_management > {filename}")
                    self.log_activity("Sao lưu dữ liệu")
                    messagebox.showinfo("Thành công", f"Đã sao lưu dữ liệu: {filename}")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể sao lưu dữ liệu: {str(e)}")

        backup_button = tk.Button(backup_window, text="Thực hiện sao lưu", command=perform_backup)
        backup_button.pack(pady=10)

        def restore_backup():
            filename = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql")])
            if filename:
                try:
                    os.system(f"mysql -u root -p inventory_management < {filename}")
                    self.log_activity("Khôi phục dữ liệu")
                    messagebox.showinfo("Thành công", "Đã khôi phục dữ liệu")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể khôi phục dữ liệu: {str(e)}")

        restore_button = tk.Button(backup_window, text="Khôi phục từ bản sao lưu", command=restore_backup)
        restore_button.pack(pady=10)

    def manage_permissions(self):
        permission_window = tk.Toplevel(self.root)
        permission_window.title("Quản lý quyền truy cập")
        permission_window.geometry("800x600")

        tk.Label(permission_window, text="Quản lý quyền truy cập", font=self.title_font).pack(pady=10)

        tree = ttk.Treeview(permission_window, columns=("ID", "Tên đăng nhập", "Vai trò", "Quyền"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Tên đăng nhập", text="Tên đăng nhập")
        tree.heading("Vai trò", text="Vai trò")
        tree.heading("Quyền", text="Quyền")
        tree.pack(fill=tk.BOTH, expand=True)

        self.cursor.execute("""
            SELECT u.id, u.username, u.role, GROUP_CONCAT(p.permission_name SEPARATOR ', ') as permissions
            FROM users u
            LEFT JOIN user_permissions up ON u.id = up.user_id
            LEFT JOIN permissions p ON up.permission_id = p.id
            GROUP BY u.id
        """)
        rows = self.cursor.fetchall()

        for row in rows:
            tree.insert("", tk.END, values=row)

        def edit_permissions():
            selected_item = tree.selection()
            if selected_item:
                item = tree.item(selected_item)
                user_id = item['values'][0]
                username = item['values'][1]

                permission_edit_window = tk.Toplevel(permission_window)
                permission_edit_window.title(f"Sửa quyền cho {username}")
                permission_edit_window.geometry("400x300")

                self.cursor.execute("SELECT id, permission_name FROM permissions")
                all_permissions = self.cursor.fetchall()

                permission_vars = {}
                for permission in all_permissions:
                    var = tk.BooleanVar()
                    cb = tk.Checkbutton(permission_edit_window, text=permission[1], variable=var)
                    cb.pack()
                    permission_vars[permission[0]] = var

                self.cursor.execute("SELECT permission_id FROM user_permissions WHERE user_id = %s", (user_id,))
                user_permissions = [row[0] for row in self.cursor.fetchall()]

                for permission_id in user_permissions:
                    if permission_id in permission_vars:
                        permission_vars[permission_id].set(True)

                def save_permissions():
                    self.cursor.execute("DELETE FROM user_permissions WHERE user_id = %s", (user_id,))
                    for permission_id, var in permission_vars.items():
                        if var.get():
                            self.cursor.execute("INSERT INTO user_permissions (user_id, permission_id) VALUES (%s, %s)",
                                                (user_id, permission_id))
                    self.conn.commit()
                    self.log_activity(f"Cập nhật quyền cho người dùng ID {user_id}")
                    messagebox.showinfo("Thành công", "Đã cập nhật quyền truy cập")
                    permission_edit_window.destroy()
                    permission_window.destroy()
                    self.manage_permissions()

                save_button = tk.Button(permission_edit_window, text="Lưu quyền", command=save_permissions)
                save_button.pack(pady=10)

            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn người dùng cần sửa quyền")

        edit_button = tk.Button(permission_window, text="Sửa quyền", command=edit_permissions)
        edit_button.pack(pady=10)

    def log_activity(self, action):
        self.cursor.execute("INSERT INTO activities (user_id, action) VALUES (%s, %s)",
                            (self.current_user, action))
        self.conn.commit()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManagementSystem(root)
    root.mainloop()