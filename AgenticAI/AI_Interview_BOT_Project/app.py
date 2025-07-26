from PyQt5.QtWidgets import QApplication
from interview_bot import InterviewBot
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InterviewBot()
    window.show()
    sys.exit(app.exec_())