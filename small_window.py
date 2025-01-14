import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFontMetrics
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal

# 위치, 효과, TTS 관련 유틸 (사용자 환경에 맞게 import 경로 수정)
from window_position import move_to_bottom_left
from effects import apply_shadow_effect
from tts_utils import play_tts_in_background


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

        # TTS 활성/비활성 상태 (True: 음성 재생 O, False: 음성 재생 X)
        self.is_tts_on = True

        # 자동 넘어가기 활성/비활성 상태 (True: 자동 넘어가기 O, False: 없음)
        self.is_auto_on = True

        # 7초마다 다음 단어로 넘어가는 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.auto_next_word)

        self.setup_ui()

    def setup_ui(self):
        """작은 화면 UI 구성"""
        # 타이틀바 제거 + 최상단 유지
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        apply_shadow_effect(self)

        # 초기 위치 좌하단
        move_to_bottom_left(self)
        # 만약 우하단으로 이동하고 싶다면 move_to_bottom_right(self) 사용

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

        # -----------------------------
        # 1. 홈 버튼 (메인 창으로 돌아가기)
        home_button = QPushButton(self)
        home_button.setIcon(QIcon("assets/go_home_back_btn.png"))
        home_button.setIconSize(QSize(20, 20))
        home_button.setFixedSize(20, 20)
        home_button.setStyleSheet("border: none;")
        home_button.clicked.connect(self.request_open_main_window)
        layout.addWidget(home_button, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)

        center_btn_layout = QHBoxLayout()
        
        # -----------------------------
        # 2. 예문 표시 토글 버튼
        self.toggle_example_button = QPushButton(self)
        self.toggle_example_button.setStyleSheet("border: none;")
        self.toggle_example_button.setFixedSize(20, 20)
        self.toggle_example_button.setIconSize(QSize(20, 20))
        self.toggle_example_button.setIcon(QIcon("assets/hide_example.png"))
        self.toggle_example_button.setToolTip("예문 표시 토글")
        self.toggle_example_button.clicked.connect(self.toggle_example)
        center_btn_layout.addWidget(self.toggle_example_button)

        # -----------------------------
        # 3. TTS(음성) 활성/비활성 토글 버튼
        self.sound_toggle_button = QPushButton(self)
        self.sound_toggle_button.setStyleSheet("border: none;")
        self.sound_toggle_button.setFixedSize(20, 20)
        self.sound_toggle_button.setIconSize(QSize(20, 20))
        # 초기 상태: is_tts_on = True -> sound_activate_btn.png
        self.sound_toggle_button.setIcon(QIcon("assets/sound_activate_btn.png"))
        self.sound_toggle_button.setToolTip("TTS 음성 켜기/끄기")
        self.sound_toggle_button.clicked.connect(self.toggle_tts_sound)
        center_btn_layout.addWidget(self.sound_toggle_button)

        # -----------------------------
        # 4. 자동 넘어가기 활성/비활성 토글 버튼
        self.auto_toggle_button = QPushButton(self)
        self.auto_toggle_button.setStyleSheet("border: none;")
        self.auto_toggle_button.setFixedSize(20, 20)
        self.auto_toggle_button.setIconSize(QSize(20, 20))
        # 초기 상태: is_auto_on = True -> auto_activate_btn.png
        self.auto_toggle_button.setIcon(QIcon("assets/auto_activate_btn.png"))
        self.auto_toggle_button.setToolTip("자동 넘어가기 켜기/끄기")
        self.auto_toggle_button.clicked.connect(self.toggle_auto_next)
        center_btn_layout.addWidget(self.auto_toggle_button)

        
        center_btn_layout.addStretch()
        layout.addLayout(center_btn_layout, 0, 1, Qt.AlignCenter)

        # -----------------------------
        # 5. 단어 정보(현재 / 총 개수) 라벨
        self.word_info_label = QLabel(self)
        self.word_info_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.word_info_label.setStyleSheet("font-family: NanumSquareL; font-size: 13px; padding-right: 3px;")
        layout.addWidget(self.word_info_label, 0, 2, Qt.AlignRight)

        # -----------------------------
        # 6. 이전 단어 버튼
        prev_button = QPushButton(self)
        prev_button.setIcon(QIcon("assets/word_previous_btn.png"))
        prev_button.setIconSize(QSize(20, 20))
        prev_button.setFixedSize(20, 20)
        prev_button.setStyleSheet("border: none;")
        prev_button.clicked.connect(self.show_prev_word)
        layout.addWidget(prev_button, 1, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # -----------------------------
        # 7. 단어 표시 라벨
        self.word_display = QLabel(self)
        self.word_display.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.word_display.setWordWrap(True)
        self.word_display.setStyleSheet("color: black; font-size: 16px;")
        layout.addWidget(self.word_display, 1, 1, 1, 4, Qt.AlignCenter)  
        # span을 1행 4열로 늘려서 중앙에 좀 더 넓게 배치

        # -----------------------------
        # 8. 예문 표시 라벨
        self.example_display = QLabel(self)
        self.example_display.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.example_display.setWordWrap(False)
        self.example_display.setStyleSheet("color: gray; font-size: 12px;")
        self.example_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.example_display, 2, 1, 1, 4, Qt.AlignCenter) 
        # 마찬가지로 span 조절

        # -----------------------------
        # 9. 다음 단어 버튼
        next_button = QPushButton(self)
        next_button.setIcon(QIcon("assets/word_next_btn.png"))
        next_button.setIconSize(QSize(20, 20))
        next_button.setFixedSize(20, 20)
        next_button.setStyleSheet("border: none;")
        next_button.clicked.connect(self.show_next_word)
        layout.addWidget(next_button, 1, 5, Qt.AlignRight | Qt.AlignVCenter)

        # -----------------------------
        # 레이아웃 행/열 크기 조정
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 3)
        layout.setRowStretch(2, 1)

        # 0~5열을 사용
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 1)
        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 1)
        layout.setColumnStretch(5, 1)

        self.setCentralWidget(container)

    def set_word_list(self, word_list):
        """단어장을 설정하고 초기 상태로 업데이트"""
        self.word_list = word_list
        self.current_index = 0
        self.update_word_display()

        # auto_next가 켜져 있으면 타이머 시작
        if self.is_auto_on:
            self.timer.start(7000)  # 7초 간격

    # =====================
    #   토글 메서드들
    # =====================
    def toggle_example(self):
        """예문 표시 여부를 토글"""
        self.is_example_shown = not self.is_example_shown
        if self.is_example_shown:
            # 예문이 보이는 상태 -> 버튼 아이콘: hide_example
            self.toggle_example_button.setIcon(QIcon("assets/hide_example.png"))
        else:
            # 예문 숨김 상태 -> 버튼 아이콘: show_example
            self.toggle_example_button.setIcon(QIcon("assets/show_example.png"))
        self.update_word_display()

    def toggle_tts_sound(self):
        """TTS(음성) 재생 여부를 토글"""
        self.is_tts_on = not self.is_tts_on
        if self.is_tts_on:
            self.sound_toggle_button.setIcon(QIcon("assets/sound_activate_btn.png"))
        else:
            self.sound_toggle_button.setIcon(QIcon("assets/sound_mute_btn.png"))

    def toggle_auto_next(self):
        """단어 자동 넘기기 여부를 토글"""
        self.is_auto_on = not self.is_auto_on
        if self.is_auto_on:
            self.auto_toggle_button.setIcon(QIcon("assets/auto_activate_btn.png"))
            self.timer.start(7000)  # 다시 타이머 시작
        else:
            self.auto_toggle_button.setIcon(QIcon("assets/auto_deactivate_btn.png"))
            self.timer.stop()

    # =====================
    #   단어 이동 메서드들
    # =====================
    def auto_next_word(self):
        """7초마다 다음 단어로 넘어감 (자동 모드 활성 시)"""
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
            # 뒤로 돌리면 마지막 단어로
            self.current_index = len(self.word_list) - 1
        self.update_word_display()

        # auto 모드가 켜져 있으면 타이머 리셋
        if self.is_auto_on:
            self.timer.start(7000)

    def show_next_word(self):
        if not self.word_list:
            return
        if self.current_index < len(self.word_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.update_word_display()

        # auto 모드가 켜져 있으면 타이머 리셋
        if self.is_auto_on:
            self.timer.start(7000)

    # =====================
    #   단어 표시 갱신
    # =====================
    def update_word_display(self):
        """현재 단어 및 정보 표시 (TTS 재생 포함)"""
        if not self.word_list:
            self.word_display.setText("단어장이 설정되지 않았습니다.")
            self.example_display.setText("")
            self.word_info_label.setText("0/0")
            return

        word_data = self.word_list[self.current_index]

        word = word_data.get('word', "")
        meaning = word_data.get('meaning', "")
        example = word_data.get('example', "")

        pretendard_bold = self.fonts.get("Pretendard-Bold.otf", "Arial")
        pretendard_regular = self.fonts.get("Pretendard-Regular.otf", "Arial")

        # 단어/뜻 표시
        self.word_display.setText(
            f"<h2 style='margin: 0; font-family: {pretendard_bold}; font-size: 20px;'>{word}</h2>"
            f"<p style='margin: 0 0 3px 0; font-family: {pretendard_regular}; font-size: 14px;'>{meaning}</p>"
        )

        # 예문 표시
        if self.is_example_shown and example.startswith('-'):
            if '+' in example:
                parts = example[1:].split('+', 1)  # '-' 제거 후 split
                if len(parts) == 2:
                    eng_example = parts[0].strip()
                    kor_example = parts[1].strip()
                    example_text = f"{eng_example}\n{kor_example}"
                else:
                    example_text = example
            else:
                example_text = example
            self.example_display.setText(example_text)
        else:
            self.example_display.setText("")

        # 단어 정보 라벨 (ex. 1/10)
        self.word_info_label.setText(f"{self.current_index + 1}/{len(self.word_list)}")

        # TTS 재생 (is_tts_on == True 일 때만)
        if self.is_tts_on:
            # 영어 단어 읽기
            play_tts_in_background(word, lang='en')
            # 영어 읽은 후 1.7초 후에 한국어 뜻 읽기
            QTimer.singleShot(1500, lambda: play_tts_in_background(meaning, lang='ko'))

        # 창 크기 조정
        self.adjust_window_size()

    # =====================
    #   창 크기 조정
    # =====================
    def adjust_window_size(self):
        """예문 텍스트 길이에 따라 창의 너비를 조정"""
        base_width = 330
        max_width = 370  # 필요에 따라 조정

        example_font = self.example_display.font()
        metrics = QFontMetrics(example_font)

        example_text = self.example_display.text().replace('\n', ' ')
        text_width = metrics.horizontalAdvance(example_text) + 20  # 여백 추가

        required_width = max(base_width, text_width)
        required_width = min(required_width, max_width)

        if self.width() != required_width:
            self.setFixedWidth(required_width)

    # =====================
    #   메인 창 열기 요청
    # =====================
    def request_open_main_window(self):
        """큰 창 열기 요청 신호 발생"""
        self.timer.stop()
        self.open_main_window_signal.emit()

    # =====================
    #   윈도우 드래그 이동
    # =====================
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
