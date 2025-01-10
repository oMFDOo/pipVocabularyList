from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
    QStackedWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from window_position import center_window
from effects import apply_shadow_effect

# 개별 페이지 임포트
from study_page import StudyPage
from word_page import WordPage
from history_page import HistoryPage

class MainWindow(QMainWindow):
    def __init__(self, fonts):
        self.fonts = fonts
        super().__init__()

        self.is_dragging = False
        self.offset = None
        self.word_list = self.load_word_list()  # 단어 데이터 초기화

        self.init_ui()
    
    def load_word_list(self):
        """단어 리스트 로드"""
        import words  # words.py에서 WORDS 데이터를 가져옵니다.
        return words.WORDS

    def init_ui(self):
        self.setWindowTitle("나의 신나는 단어장!") 
        self.resize(1200, 700)
        self.setWindowFlags(Qt.FramelessWindowHint)  # 프레임 제거
        apply_shadow_effect(self)  # 그림자 효과
        center_window(self)       # 화면 중앙 배치

        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border-radius: 8px;
            }
            QFrame#Sidebar {
                background-color: #45b1e9;
                border-top-left-radius: 8px;
                border-bottom-left-radius: 8px;
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

        # 사이드바 버튼
        self.study_button = QPushButton()
        self.word_button = QPushButton()
        self.history_button = QPushButton()

        # 버튼 이미지 설정
        self.update_button_styles(0)  # 초기 상태는 '학습' 활성화

        # 버튼 클릭 시 page 전환
        self.study_button.clicked.connect(lambda: self.change_page(0))
        self.word_button.clicked.connect(lambda: self.change_page(1))
        self.history_button.clicked.connect(lambda: self.change_page(2))

        sidebar_layout.addWidget(self.study_button)
        sidebar_layout.addWidget(self.word_button)
        sidebar_layout.addWidget(self.history_button)
        sidebar_layout.addStretch(1)

        # 메인 레이아웃
        main_layout.addWidget(sidebar_frame, 0)

        # QStackedWidget - 페이지를 담음
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)

        # 페이지들 생성 & stacked_widget에 추가
        self.study_page = StudyPage(self.fonts)
        self.word_page = WordPage()
        self.history_page = HistoryPage()

        self.stacked_widget.addWidget(self.study_page)   # index 0
        self.stacked_widget.addWidget(self.word_page)    # index 1
        self.stacked_widget.addWidget(self.history_page) # index 2

        # 기본 페이지는 '학습'(index 0)
        self.stacked_widget.setCurrentIndex(0)

    def update_button_styles(self, active_index):
        """버튼 스타일 업데이트"""
        button_styles = [
            {
                "active": "assets/study_page_activate_btn.png",
                "inactive": "assets/study_page_deactivate_btn.png",
            },
            {
                "active": "assets/podcast_page_activate_btn.png",
                "inactive": "assets/podcast_page_deactivate_btn.png",
            },
            {
                "active": "assets/log_page_activate_btn.png",
                "inactive": "assets/log_page_deactivate_btn.png",
            },
        ]

        buttons = [self.study_button, self.word_button, self.history_button]

        for i, button in enumerate(buttons):
            image_path = button_styles[i]["active"] if i == active_index else button_styles[i]["inactive"]
            button.setIcon(QIcon(image_path))  # 이미지를 QIcon으로 설정
            button.setIconSize(QSize(70, 70))  # 아이콘 크기 설정
            button.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: none;
                    min-width: 70px; /* 버튼 크기 조정 */
                    max-width: 70px;
                    min-height: 70px;
                    max-height: 70px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)

    def change_page(self, index):
        """사이드바 버튼 누를 때 스택 위젯 페이지 전환"""
        self.stacked_widget.setCurrentIndex(index)
        self.update_button_styles(index)

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
