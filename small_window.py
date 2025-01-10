# small_window.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal

from window_position import move_to_bottom_right, move_to_bottom_left
from effects import apply_shadow_effect

class SmallWindow(QMainWindow):
    open_main_window_signal = pyqtSignal()  # 메인 창 열기 요청 신호

    def __init__(self, fonts):
        super().__init__()
        self.fonts = fonts
        self.word_list = []  # 초기 단어장은 비어 있음
        self.current_index = 0

        self.is_dragging = False
        self.offset = None

        # 예문 표시 여부 상태: 기본 True(표시)
        self.is_example_shown = True

        # 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_next_word)
        # 타이머는 단어장이 설정될 때 시작됩니다.

        self.setup_ui()

    def setup_ui(self):
        """작은 화면 UI 구성"""
        # 타이틀바 제거 + 최상단 유지
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        apply_shadow_effect(self)

        # 초기 위치을 좌하단으로 설정 (필요 시 변경 가능)
        move_to_bottom_left(self)
        # move_to_bottom_right(self)  # 필요 시 교체

        self.setStyleSheet("""
            QMainWindow {
                background-color: white;
                border-radius: 15px;
            }
        """)

        container = QWidget(self)
        layout = QGridLayout(container)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(5)

        # 홈 버튼 (메인 창으로 돌아가기)
        home_button = QPushButton(self)
        home_button.setIcon(QIcon("assets/go_home_back_btn.png"))
        home_button.setIconSize(QSize(20, 20))
        home_button.setFixedSize(20, 20)
        home_button.setStyleSheet("border: none;")
        home_button.clicked.connect(self.request_open_main_window)
        layout.addWidget(home_button, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # 예문 표시 토글 버튼
        self.toggle_example_button = QPushButton(self)
        self.toggle_example_button.setStyleSheet("border: none;")
        self.toggle_example_button.setFixedSize(20, 20)
        self.toggle_example_button.setIconSize(QSize(20, 20))
        self.toggle_example_button.setIcon(QIcon("assets/hide_example.png"))
        self.toggle_example_button.setToolTip("예문 표시 토글")
        self.toggle_example_button.clicked.connect(self.toggle_example)
        layout.addWidget(self.toggle_example_button, 0, 1, Qt.AlignCenter | Qt.AlignVCenter)

        # 단어 정보(현재 / 총 개수)
        self.word_info_label = QLabel(self)
        self.word_info_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.word_info_label.setStyleSheet("font-family: NanumSquareL; font-size: 13px; padding-right: 3px;")
        layout.addWidget(self.word_info_label, 0, 2, Qt.AlignRight)

        # 이전 단어 버튼
        prev_button = QPushButton(self)
        prev_button.setIcon(QIcon("assets/word_previous_btn.png"))
        prev_button.setIconSize(QSize(20, 20))
        prev_button.setFixedSize(20, 20)
        prev_button.setStyleSheet("border: none;")
        prev_button.clicked.connect(self.show_prev_word)
        layout.addWidget(prev_button, 1, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # 단어 표시 라벨
        self.word_display = QLabel(self)
        self.word_display.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.word_display.setWordWrap(True)
        self.word_display.setStyleSheet("color: black; font-size: 16px;")
        layout.addWidget(self.word_display, 1, 1, Qt.AlignCenter)

        # 예문 표시 라벨
        self.example_display = QLabel(self)
        self.example_display.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.example_display.setWordWrap(True)
        self.example_display.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.example_display, 2, 1, Qt.AlignCenter)

        # 다음 단어 버튼
        next_button = QPushButton(self)
        next_button.setIcon(QIcon("assets/word_next_btn.png"))
        next_button.setIconSize(QSize(20, 20))
        next_button.setFixedSize(20, 20)
        next_button.setStyleSheet("border: none;")
        next_button.clicked.connect(self.show_next_word)
        layout.addWidget(next_button, 1, 2, Qt.AlignRight | Qt.AlignVCenter)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 3)
        layout.setRowStretch(2, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 3)
        layout.setColumnStretch(2, 1)

        self.setCentralWidget(container)

        # 초기 단어 세팅 (단어장이 설정될 때)
        # self.update_word_display()  # 단어장이 없으므로 호출하지 않음

    def set_word_list(self, word_list):
        """단어장을 설정하고 초기 상태로 업데이트"""
        self.word_list = word_list
        self.current_index = 0
        self.update_word_display()
        self.timer.start(5000)  # 타이머 시작

    # ============ 기능 메서드들 ============ #
    def auto_next_word(self):
        """5초마다 다음 단어로 넘어감"""
        if not self.word_list:
            return
        if self.current_index < len(self.word_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.update_word_display()

    def show_prev_word(self):
        if not self.word_list:
            return
        if self.current_index > 0:
            self.current_index -= 1
        else:
            self.current_index = len(self.word_list) - 1  # 뒤로 돌렸을 때 마지막으로
        self.update_word_display()
        self.timer.start(5000)  # 타이머 리셋

    def show_next_word(self):
        if not self.word_list:
            return
        if self.current_index < len(self.word_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.update_word_display()
        self.timer.start(5000)  # 타이머 리셋

    def toggle_example(self):
        """예문 표시 여부를 토글"""
        self.is_example_shown = not self.is_example_shown

        if self.is_example_shown:
            # 예문이 보이는 상태 -> 버튼 아이콘: hide_example
            self.toggle_example_button.setIcon(QIcon("assets/hide_example.png"))
            # self.resize(330, 110)  # 예문 표시 시 원래 크기
        else:
            # 예문이 숨겨진 상태 -> 버튼 아이콘: show_example
            self.toggle_example_button.setIcon(QIcon("assets/show_example.png"))
            # self.resize(330, 110)  # 예문 숨길 시 창 크기 줄이기

        self.update_word_display()

    def update_word_display(self):
        """현재 단어 및 정보 표시"""
        if not self.word_list:
            self.word_display.setText("단어장이 설정되지 않았습니다.")
            self.example_display.setText("")
            self.word_info_label.setText("0/0")
            return

        word_data = self.word_list[self.current_index]

        # 딕셔너리 키로 접근
        word = word_data.get('word', "")
        meaning = word_data.get('meaning', "")
        example = word_data.get('example', "")

        pretendard_bold = self.fonts.get("Pretendard-Bold.otf", "Arial")
        pretendard_regular = self.fonts.get("Pretendard-Regular.otf", "Arial")

        # 단어와 뜻 표시
        self.word_display.setText(
            f"<h2 style='margin: 0; font-family: {pretendard_bold}; font-size: 20px;'>{word}</h2>"
            f"<p style='margin: 0 0 3px 0; font-family: {pretendard_regular}; font-size: 14px;'>{meaning}</p>"
        )

        # 예문 표시 여부에 따라 처리
        if self.is_example_shown and example.startswith('-'):
            # 예문을 '-'로 시작하고 '+'로 분리
            if '+' in example:
                parts = example[1:].split('+', 1)  # '-' 제거 후 분리
                if len(parts) == 2:
                    eng_example = parts[0].strip()
                    kor_example = parts[1].strip()
                    example_text = f"{eng_example}\n{kor_example}"
                else:
                    example_text = example  # '+'가 없는 경우 그대로
            else:
                example_text = example  # '+'가 없는 경우 그대로
            self.example_display.setText(example_text)
        else:
            self.example_display.setText("")

        self.word_info_label.setText(f"{self.current_index + 1}/{len(self.word_list)}")

    def request_open_main_window(self):
        """큰 창 열기 요청 신호 발생"""
        self.timer.stop()  # 타이머 정지
        self.open_main_window_signal.emit()

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
