from PyQt5.QtWidgets import QMainWindow, QPushButton, QGridLayout, QWidget, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
from custom_widgets import ColorBlock
from effects import apply_shadow_effect
from window_position import center_window, move_to_bottom_right, move_to_bottom_left


class MainWindow(QMainWindow):
    def __init__(self, fonts):
        super().__init__()
        self.setWindowTitle("나의 신나는 단어장!")
        self.resize(1000, 800)
        
        # 전달받은 폰트 저장
        self.fonts = fonts

        self.is_dragging = False
        self.offset = None

        # 타이틀바 제거 및 그림자 효과 추가
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)  # 배경 투명 설정
        apply_shadow_effect(self)

        # 초기 화면 세팅
        self.is_initial = True
        self.setup_initial_screen()
        center_window(self)

    def setup_initial_screen(self):
        """초기 화면 구성"""
        self.clear_screen()

        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border-radius: 15px;
            }
        """)

        self.move_button = QPushButton("학습 시작", self)
        self.move_button.setGeometry(50, 50, 200, 50)
        self.move_button.clicked.connect(self.switch_to_bottom_left)
        self.move_button.show()

        self.label = QLabel("초기 화면", self)
        self.label.setGeometry(100, 120, 100, 30)
        self.label.show()

    def setup_bottom_right_screen(self):
        """작은 창 구성 (단어장 기능 포함)"""
        self.clear_screen()

        # 창 스타일 유지
        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border-radius: 15px;  /* 창 곡률 */
            }
        """)

        # 단어 데이터 및 현재 인덱스
        self.words = [
            {"word": "cherish", "meaning": "소중히 여기다", "example": "Ugi, I cherish every moment with you. \n우기야, 너와 함께하는 모든 순간이 소중해."},
            {"word": "devotion", "meaning": "헌신", "example": "My devotion to you grows stronger every day. \n우기에 대한 내 헌신은 매일 더 강해져."},
            {"word": "serendipity", "meaning": "우연한 행운", "example": "Meeting you was pure serendipity. \n너를 만난 건 정말 우연한 행운이었어!"},
            {"word": "gratitude", "meaning": "감사", "example": "I feel immense gratitude for having you in my life. \n내 삶에 우기가 있어서 정말 감사해!"},
            {"word": "eternity", "meaning": "영원", "example": "I wish our love could last for all eternity. \n우리의 사랑이 영원히 계속되길 바래!"}
        ]

        self.current_index = 0  # 현재 단어의 인덱스

        # QWidget으로 작은 화면 구성
        container = QWidget(self)
        layout = QGridLayout(container)

        # 레이아웃 여백 및 간격 제거
        layout.setContentsMargins(3, 3, 3, 3)  # 여백 설정
        layout.setSpacing(5)  # 위젯 간 간격 설정

        # 1번 칸: 홈 버튼
        home_button = QPushButton(self)
        home_button.setIcon(QIcon("go_home_back_btn.png"))
        home_button.setIconSize(QSize(20, 20))
        home_button.setFixedSize(20, 20)
        home_button.setStyleSheet("border: none;")
        home_button.clicked.connect(self.switch_to_initial)
        layout.addWidget(home_button, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # 2번 칸: 비어 있음
        layout.addWidget(QWidget(), 0, 1)  # 빈 위젯 추가
        
        # 3번 칸: 현재 단어 번호와 총 단어 개수
        self.word_info_label = QLabel(self)
        self.word_info_label.setAlignment(Qt.AlignRight)
        self.word_info_label.setStyleSheet("font-family: NanumSquareL; font-size: 16px; padding-right: 3px;")
        layout.addWidget(self.word_info_label, 0, 2, Qt.AlignRight)


        # 4번 칸: 이전 단어 보기 버튼
        prev_button = QPushButton(self)
        prev_button.setIcon(QIcon("word_previous_btn.png"))
        prev_button.setIconSize(QSize(20, 20))
        prev_button.setFixedSize(20, 20)
        prev_button.setStyleSheet("border: none;")
        # prev_button.setStyleSheet("background-color: #FFFF33; border: none; border-radius: 25px;")
        prev_button.clicked.connect(self.show_prev_word)
        layout.addWidget(prev_button, 1, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # 5번 칸: 현재 단어 표시
        self.word_display = QLabel(self)
        # self.word_display.setAlignment(Qt.AlignCenter)
        self.word_display.setAlignment(Qt.AlignTop | Qt.AlignCenter)  # 텍스트 상단 정렬
        self.word_display.setWordWrap(True)
        self.word_display.setStyleSheet("""
            color: black; 
            font-size: 16px;
        """)
        layout.addWidget(self.word_display, 1, 1, Qt.AlignCenter)

        # 6번 칸: 다음 단어 보기 버튼
        next_button = QPushButton(self)
        next_button.setIcon(QIcon("word_next_btn.png"))
        next_button.setIconSize(QSize(20, 20))
        next_button.setFixedSize(20, 20)
        next_button.setStyleSheet("border: none;")
        # next_button.setStyleSheet("background-color: #33FFFF; border: none; border-radius: 25px;")
        next_button.clicked.connect(self.show_next_word)
        layout.addWidget(next_button, 1, 2, Qt.AlignRight | Qt.AlignVCenter)

        # 레이아웃 비율 설정
        layout.setRowStretch(0, 1)  # 첫 번째 행
        layout.setRowStretch(1, 3)  # 두 번째 행
        layout.setColumnStretch(0, 1)  # 좌측
        layout.setColumnStretch(1, 3)  # 중앙
        layout.setColumnStretch(2, 1)  # 우측

        self.setCentralWidget(container)
    
        # 초기 단어 표시
        self.update_word_display()


    def clear_screen(self):
        """기존 화면 위젯 모두 제거"""
        for widget in self.findChildren(QWidget):
            widget.deleteLater()  # 모든 위젯 삭제
        self.setCentralWidget(None)  # 중앙 위젯 초기화

    def switch_to_bottom_right(self):
        self.is_initial = False
        move_to_bottom_right(self)
        self.setup_bottom_right_screen()
        
    def switch_to_bottom_left(self):
        self.is_initial = False
        move_to_bottom_left(self)
        self.setup_bottom_right_screen()

    def switch_to_initial(self):
        self.is_initial = True
        center_window(self)
        self.setup_initial_screen()
    
    # 마우스 설정
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

    # 단어 표출 설정
    def show_prev_word(self):
        """이전 단어 보기"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_word_display()

    def show_next_word(self):
        """다음 단어 보기"""
        if self.current_index < len(self.words) - 1:
            self.current_index += 1
            self.update_word_display()

    def update_word_display(self):
        """현재 단어 및 정보 표시"""
        # 현재 단어 데이터 가져오기
        word_data = self.words[self.current_index]
        
        # 필요한 폰트 가져오기
        nanum_regular = self.fonts.get("NanumSquareR.ttf", "Arial")
        nanum_light = self.fonts.get("NanumSquareL.ttf", "Arial")

        # 중앙 단어 표시 업데이트
        self.word_display.setText(
            f"<h3 style='margin: 0; font-family: {nanum_regular}; font-size: 20px;'>{word_data['word']}</h3>"
            f"<p style='margin: 0 0 3px 0; font-family: {nanum_regular}; font-size: 16px;'>{word_data['meaning']}</p>"
            f"<pre style='margin: 0; font-family: {nanum_regular}; font-size: 12px;'>{word_data['example']}</pre>"
        )
        
        # 상단 인덱스 정보 업데이트
        self.word_info_label.setText(f"{self.current_index + 1}/{len(self.words)}")