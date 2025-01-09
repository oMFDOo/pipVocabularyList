from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from window_position import center_window
from effects import apply_shadow_effect

# 신호 정의
class BigWindow(QMainWindow):
    open_small_window_signal = pyqtSignal()  # 작은 창 열기 요청 신호

    def __init__(self, fonts, word_list):
        super().__init__()
        self.fonts = fonts
        self.word_list = word_list

        self.is_dragging = False
        self.offset = None

        # UI 설정
        self.setup_ui()

    def setup_ui(self):
        """큰 화면 UI 설정 (현재는 초기화면 정도만)"""
        self.setWindowTitle("나의 신나는 단어장! - 큰 화면")
        self.resize(1000, 800)
        self.setWindowFlags(Qt.FramelessWindowHint)
        apply_shadow_effect(self)
        center_window(self)

        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border-radius: 15px;
            }
        """)

        # '학습 시작' 버튼
        self.move_button = QPushButton("학습 시작", self)
        self.move_button.setGeometry(50, 50, 200, 50)
        self.move_button.clicked.connect(self.request_open_small_window)

        # 간단한 라벨
        self.label = QLabel("초기 화면", self)
        self.label.setGeometry(100, 120, 100, 30)

    def request_open_small_window(self):
        """작은 창 열기 요청 신호 발생"""
        self.open_small_window_signal.emit()

    # ============ 윈도우 이동 관련 (드래그) ============ #
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.offset = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
