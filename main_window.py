# main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget
)
from PyQt5.QtCore import Qt
from window_position import center_window
from effects import apply_shadow_effect

# 개별 페이지 임포트
from study_page import StudyPage
from word_page import WordPage
from history_page import HistoryPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_dragging = False
        self.offset = None
        self.word_list = self.load_word_list()  # 단어 데이터 초기화
        
        self.init_ui()
    
    def load_word_list(self):
        """단어 리스트 로드"""
        # words.WORDS에서 데이터를 불러옵니다. (예: {"word": "apple", "meaning": "사과"} 형식)
        import words  # words.py에서 WORDS 데이터를 가져옵니다.
        return words.WORDS

    def init_ui(self):
        self.setWindowTitle("나의 신나는 단어장!") 
        self.resize(1000, 800)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 프레임 제거
        apply_shadow_effect(self)  # 그림자 효과
        center_window(self)       # 화면 중앙 배치

        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border-radius: 15px;
            }
            QFrame#Sidebar {
                background-color: #E8F0FE;
                border-top-left-radius: 15px;
                border-bottom-left-radius: 15px;
            }
            QPushButton {
                background-color: #ffffff;
                border: none;
                padding: 10px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)

        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # 사이드바
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(3, 60, 3, 10)
        sidebar_layout.setSpacing(10)

        # 사이드바 버튼 (학습, 단어장, 학습 이력)
        self.study_button = QPushButton("학습")
        self.word_button = QPushButton("단어장")
        self.history_button = QPushButton("학습 이력")

        # 버튼 클릭 시 page 전환
        self.study_button.clicked.connect(lambda: self.change_page(0))
        self.word_button.clicked.connect(lambda: self.change_page(1))
        self.history_button.clicked.connect(lambda: self.change_page(2))

        sidebar_layout.addWidget(self.study_button)
        sidebar_layout.addWidget(self.word_button)
        sidebar_layout.addWidget(self.history_button)
        sidebar_layout.addStretch(1)

        # 메인 레이아웃 (좌: 사이드바, 우: 스택위젯)
        main_layout.addWidget(sidebar_frame, 0)

        # QStackedWidget - 페이지를 담음
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)

        # 페이지들 생성 & stacked_widget에 추가
        self.study_page = StudyPage()
        self.word_page = WordPage()
        self.history_page = HistoryPage()

        self.stacked_widget.addWidget(self.study_page)   # index 0
        self.stacked_widget.addWidget(self.word_page)    # index 1
        self.stacked_widget.addWidget(self.history_page) # index 2

        # 기본 페이지는 '학습'(index 0)
        self.stacked_widget.setCurrentIndex(0)

    def change_page(self, index):
        """사이드바 버튼 누를 때 스택 위젯 페이지 전환"""
        self.stacked_widget.setCurrentIndex(index)

    # ======== 마우스 드래그로 창 이동 ======== #
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
