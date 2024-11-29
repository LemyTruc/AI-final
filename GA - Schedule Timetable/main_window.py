import json
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QSpinBox, QDoubleSpinBox, QPushButton, QWidget, QLabel, QMessageBox, QLineEdit, QTabWidget, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView
from genetic_algorithm import genetic_algorithm, Room, CourseClass

class ScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trình tạo lịch học cho sinh viên")
        self.setGeometry(100, 100, 800, 600)
        self.total_slots = 30
        self.generations = 100
        self.population_size = 50
        self.crossover_rate = 0.7
        self.mutation_rate = 0.1

        self.load_data()

        self.init_ui()

    def load_data(self):
        with open('data.json', 'r') as f:
            data = json.load(f)
        
        self.rooms = [Room(**room) for room in data['rooms']]
        self.courses = [CourseClass(**course) for course in data['courses']]
        
    def save_data(self):
        data = {
            "rooms": [room.__dict__ for room in self.rooms],
            "courses": [course.__dict__ for course in self.courses]
        }
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

    def init_ui(self):
        self.tabs = QTabWidget()
        self.data_tab = QWidget()
        self.schedule_tab = QWidget()

        self.tabs.addTab(self.data_tab, "Dữ Liệu")
        self.tabs.addTab(self.schedule_tab, "Lịch Học")

        self.init_data_tab()
        self.init_schedule_tab()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_data_tab(self):
        layout = QVBoxLayout()

        # Add Room and Add Course sections side by side
        form_layout = QHBoxLayout()

        # Room form
        room_form_layout = QFormLayout()
        self.room_name_input = QLineEdit()
        self.room_seats_input = QSpinBox()
        self.room_seats_input.setMaximum(100)
        self.room_is_lab_input = QComboBox()
        self.room_is_lab_input.addItems(["Không", "Có"])
        self.room_campus_input = QLineEdit()

        room_form_layout.addRow("Tên phòng:", self.room_name_input)
        room_form_layout.addRow("Số ghế:", self.room_seats_input)
        room_form_layout.addRow("Phòng thực hành:", self.room_is_lab_input)
        room_form_layout.addRow("Cơ sở:", self.room_campus_input)

        add_room_button = QPushButton("Thêm phòng")
        add_room_button.clicked.connect(self.add_room)
        room_form_layout.addWidget(add_room_button)

        # Course form
        course_form_layout = QFormLayout()
        self.course_name_input = QLineEdit()
        self.max_students_input = QSpinBox()
        self.max_students_input.setMaximum(100)
        self.course_duration_input = QSpinBox()
        self.course_duration_input.setMaximum(10)
        self.course_requires_lab_input = QComboBox()
        self.course_requires_lab_input.addItems(["Không", "Có"])
        self.course_teacher_input = QLineEdit()
        self.course_department_input = QLineEdit()
        self.course_campus_input = QLineEdit()
        course_form_layout.addRow("Tên khóa học:", self.course_name_input)
        course_form_layout.addRow("Số lượng sinh viên tối đa:", self.max_students_input)
        course_form_layout.addRow("Thời lượng:", self.course_duration_input)
        course_form_layout.addRow("Phòng thực hành:", self.course_requires_lab_input)
        course_form_layout.addRow("Giảng viên:", self.course_teacher_input)
        course_form_layout.addRow("Khoa:", self.course_department_input)
        course_form_layout.addRow("Cơ sở:", self.course_campus_input)

        add_course_button = QPushButton("Thêm khóa học")
        add_course_button.clicked.connect(self.add_course)
        course_form_layout.addWidget(add_course_button)

        form_layout.addLayout(room_form_layout)
        form_layout.addLayout(course_form_layout)

        # Room data table
        self.room_table = QTableWidget()
        self.room_table.setColumnCount(5)
        self.room_table.setHorizontalHeaderLabels(["ID", "Tên Phòng", "Số Ghế", "Phòng Thực Hành", "Cơ Sở"])
        self.room_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.load_room_data()

        # Course data table
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(7)
        self.course_table.setHorizontalHeaderLabels(["ID", "Tên Khóa Học", "Thời Lượng", "Phòng Thực hành", "Giảng viên", "Khoa", "Cơ Sở"])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.load_course_data()

        layout.addLayout(form_layout)
        layout.addWidget(QLabel("Phòng"))
        layout.addWidget(self.room_table)
        layout.addWidget(QLabel("Khóa Học"))
        layout.addWidget(self.course_table)

        self.data_tab.setLayout(layout)

    def update_room_dropdown(self):
        self.course_room_input.clear()
        for room in self.rooms:
            self.course_room_input.addItem(room.name, room.id)

    def init_schedule_tab(self):
        layout = QVBoxLayout()
        self.schedule_grid = QGridLayout()
        self.setup_schedule_grids()

        form_layout = QHBoxLayout()  # Change to QHBoxLayout for horizontal layout

        self.gen_spin = QSpinBox()
        self.gen_spin.setValue(self.generations)
        form_layout.addWidget(QLabel("Số Thế Hệ:"))
        form_layout.addWidget(self.gen_spin)

        self.pop_spin = QSpinBox()
        self.pop_spin.setValue(self.population_size)
        form_layout.addWidget(QLabel("Kích Thước Quần Thể:"))
        form_layout.addWidget(self.pop_spin)

        self.crossover_spin = QDoubleSpinBox()
        self.crossover_spin.setRange(0, 1)
        self.crossover_spin.setSingleStep(0.01)
        self.crossover_spin.setValue(self.crossover_rate)
        form_layout.addWidget(QLabel("Tỷ Lệ Lai Ghép:"))
        form_layout.addWidget(self.crossover_spin)

        self.mutation_spin = QDoubleSpinBox()
        self.mutation_spin.setRange(0, 1)
        self.mutation_spin.setSingleStep(0.01)
        self.mutation_spin.setValue(self.mutation_rate)
        form_layout.addWidget(QLabel("Tỷ Lệ Đột Biến:"))
        form_layout.addWidget(self.mutation_spin)

        run_button = QPushButton("Chạy Thuật Toán Di Truyền")
        run_button.clicked.connect(self.run_ga)

        layout.addLayout(form_layout)
        layout.addLayout(self.schedule_grid)
        layout.addWidget(run_button)

        self.schedule_tab.setLayout(layout)

    def load_room_data(self):
        self.room_table.setRowCount(len(self.rooms))
        for row, room in enumerate(self.rooms):
            self.room_table.setItem(row, 0, QTableWidgetItem(str(room.id)))
            self.room_table.setItem(row, 1, QTableWidgetItem(room.name))
            self.room_table.setItem(row, 2, QTableWidgetItem(str(room.seats)))
            self.room_table.setItem(row, 3, QTableWidgetItem(str(room.is_lab)))
            self.room_table.setItem(row, 4, QTableWidgetItem(room.campus))

    def load_course_data(self):
        self.course_table.setRowCount(len(self.courses))
        for row, course in enumerate(self.courses):
            self.course_table.setItem(row, 0, QTableWidgetItem(str(course.id)))
            self.course_table.setItem(row, 1, QTableWidgetItem(course.name))
            self.course_table.setItem(row, 2, QTableWidgetItem(str(course.duration)))
            self.course_table.setItem(row, 3, QTableWidgetItem(str(course.requires_lab)))
            self.course_table.setItem(row, 4, QTableWidgetItem(course.teacher))
            self.course_table.setItem(row, 5, QTableWidgetItem(course.department))
            self.course_table.setItem(row, 6, QTableWidgetItem(course.campus))

    def setup_schedule_grids(self):
        days = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu"]
        for col, day in enumerate(days):
            self.schedule_grid.addWidget(QLabel(day), 0, col + 1)

        for row in range(1, 7):
            self.schedule_grid.addWidget(QLabel(f"Tiết {row}"), row, 0)
            for col in range(1, 6):
                frame = QLabel("")
                frame.setStyleSheet("border: 1px solid black; min-width: 200px;  min-height: 100px; font-size: 12px;  padding: 5px; ")
                self.schedule_grid.addWidget(frame, row, col)

    def display_schedule(self, schedule):
        for i in range(1, 7):
            for j in range(1, 6):
                frame = self.schedule_grid.itemAtPosition(i, j).widget()
                if frame:
                    frame.setText("")

        for course, slot in schedule.classes.items():
            day = (slot % 5) + 1
            period = (slot // 5) + 1
            frame = self.schedule_grid.itemAtPosition(period, day).widget()
            if frame:
                room = next((r for r in self.rooms if r.id == course.room_id), None)
                room_name = room.name if room else "N/A"
                frame.setText(f"Tên khoá học: {course.name}\nGiảng viên: {course.teacher}\nKhoa: {course.department}\nCơ sở: {course.campus}\nPhòng: {room_name}\nThời lượng: ({course.duration} tiết)")

    def run_ga(self):
        self.generations = self.gen_spin.value()
        self.population_size = self.pop_spin.value()
        self.crossover_rate = self.crossover_spin.value()
        self.mutation_rate = self.mutation_spin.value()

        best_schedule = genetic_algorithm(self.courses, self.rooms, self.total_slots, self.generations, self.population_size, self.crossover_rate, self.mutation_rate)
        self.display_schedule(best_schedule)
        QMessageBox.information(self, "Kết quả", f"Điểm lịch học tốt nhất: {best_schedule.score}")

    def add_room(self):
        # Validate input
        if not self.room_name_input.text() or not self.room_campus_input.text():
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng điền đầy đủ thông tin phòng.")
            return

        # Determine next room ID
        if self.rooms:
            new_id = max(room.id for room in self.rooms) + 1
        else:
            new_id = 1

        # Create new room
        new_room = Room(
            id=new_id, 
            name=self.room_name_input.text(), 
            seats=self.room_seats_input.value(), 
            is_lab=self.room_is_lab_input.currentText() == "Có", 
            campus=self.room_campus_input.text()
        )
        self.rooms.append(new_room)

        # Refresh room data in table and save
        self.load_room_data()
        self.save_data()

        # Update room dropdown in course form
        self.update_room_dropdown()

        # Clear input fields
        self.room_name_input.clear()
        self.room_seats_input.setValue(0)
        self.room_is_lab_input.setCurrentIndex(0)
        self.room_campus_input.clear()

        QMessageBox.information(self, "Thành công", "Phòng đã được thêm thành công!")

    def add_course(self):
        # Validate input
        if not self.course_name_input.text() or not self.course_teacher_input.text() or not self.course_department_input.text() or not self.course_campus_input.text():
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng điền đầy đủ thông tin khóa học.")
            return

        # Determine next course ID
        if self.courses:
            new_id = max(course.id for course in self.courses) + 1
        else:
            new_id = 1

        # Create new course
        new_course = CourseClass(
            id=new_id, 
            name=self.course_name_input.text(), 
            department=self.course_department_input.text(),
            max_students=self.max_students_input.value(),
            duration=self.course_duration_input.value(), 
            requires_lab=self.course_requires_lab_input.currentText() == "Có", 
            teacher=self.course_teacher_input.text(), 
            campus=self.course_campus_input.text(),
            room_id=None  # Let the genetic algorithm assign the room
        )

        # Add the new course to the list
        self.courses.append(new_course)

        # Clear input fields
        self.course_name_input.clear()
        self.course_teacher_input.clear()
        self.course_department_input.clear()
        self.course_campus_input.clear()
        self.max_students_input.setValue(0)
        self.course_duration_input.setValue(0)
        self.course_requires_lab_input.setCurrentIndex(0)

        QMessageBox.information(self, "Thành công", "Khóa học đã được thêm thành công!")