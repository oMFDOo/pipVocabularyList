# ui_manager.py
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel
from window_position import center_window, move_to_bottom_right

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("나의 신나는 단어장!")
        self.resize(1000, 800)  # 초기 창 크기 설정

        # 초기 화면 세팅
        self.is_initial = True  # 초기 화면 여부
        self.setup_initial_screen()  # 초기 화면 구성
        center_window(self)  # 창 중앙 배치

    def setup_initial_screen(self):
        """초기 화면 구성"""
        self.clear_screen()  # 기존 위젯 제거

        # 우하단 이동 버튼
        self.move_button = QPushButton("학습 시작", self)
        self.move_button.setGeometry(50, 50, 200, 50)
        self.move_button.show()  # 버튼을 화면에 표시
        self.move_button.clicked.connect(self.switch_to_bottom_right)

        # 초기 화면 표시
        self.label = QLabel("초기 화면", self)
        self.label.setGeometry(100, 120, 100, 30)
        self.label.show()

    def setup_bottom_right_screen(self):
        """우하단 화면 구성"""
        self.clear_screen()  # 기존 위젯 제거

        # 뒤로가기 버튼 생성
        self.back_button = QPushButton("뒤로가기", self)
        self.back_button.setGeometry(50, 50, 200, 50)
        self.back_button.show()  # 버튼을 화면에 표시
        self.back_button.clicked.connect(self.switch_to_initial)

        # 우하단 화면 표시
        message = "동적으로 설정된 학습 화면"
        self.label = QLabel(message, self)
        self.label.setGeometry(100, 120, 100, 30)
        self.label.show()

    def clear_screen(self):
        """화면에 있는 기존 위젯 모두 제거"""
        for widget in self.findChildren(QPushButton):
            widget.deleteLater()
        for widget in self.findChildren(QLabel):
            widget.deleteLater()

    def switch_to_bottom_right(self):
        """우하단 화면으로 전환"""
        self.is_initial = False
        move_to_bottom_right(self)  # 창 위치 이동
        self.setup_bottom_right_screen()  # 화면 구성 변경

    def switch_to_initial(self):
        """초기 화면으로 전환"""
        self.is_initial = True
        center_window(self)  # 창 위치 이동
        self.setup_initial_screen()  # 화면 구성 변경
