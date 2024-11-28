from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
import sys
from main_window import ScheduleApp

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    schedule_app = ScheduleApp()
    schedule_app.show()
    sys.exit(app.exec())