import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy
)
from PyQt5.QtGui import QIcon, QFontMetrics
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal

# 위치, 효과, TTS 관련 유틸 (사용자 환경에 맞게 import 경로 수정)
from window_position import move_to_bottom_left
from effects import apply_shadow_effect
from tts_utils import play_tts_in_background  # TTS 함수 import

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

        # TTS 활성/비활성 상태 (True: 단어, 뜻 TTS 재생 O, False: 재생 X)
        self.is_tts_on = True

        # 예문 TTS 활성/비활성 상태 (True: 예문 TTS 재생 O, False: 재생 X)
        self.is_example_tts_on = False

        # 자동 넘어가기 활성/비활성 상태 (True: 자동 넘어가기 O, False: 없음)
        self.is_auto_on = True

        # 자동 다음 단어 간격: 예문 TTS 활성 시 14000ms, 비활성 시 7000ms
        self.auto_interval = 14000 if self.is_example_tts_on else 7000

        # 타이머: 지정된 간격마다 다음 단어로 넘어감
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
        # 2. 예문 표시 토글 버튼 (예문 텍스트 보이기/숨기기)
        self.toggle_example_button = QPushButton(self)
        self.toggle_example_button.setStyleSheet("border: none;")
        self.toggle_example_button.setFixedSize(20, 20)
        self.toggle_example_button.setIconSize(QSize(20, 20))
        self.toggle_example_button.setIcon(QIcon("assets/hide_example.png"))
        self.toggle_example_button.setToolTip("예문 표시 토글")
        self.toggle_example_button.clicked.connect(self.toggle_example)
        center_btn_layout.addWidget(self.toggle_example_button)

        # -----------------------------
        # 3. TTS(단어/뜻) 활성/비활성 토글 버튼
        self.sound_toggle_button = QPushButton(self)
        self.sound_toggle_button.setStyleSheet("border: none;")
        self.sound_toggle_button.setFixedSize(20, 20)
        self.sound_toggle_button.setIconSize(QSize(20, 20))
        self.sound_toggle_button.setIcon(QIcon("assets/sound_activate_btn.png"))
        self.sound_toggle_button.setToolTip("단어/뜻 TTS 켜기/끄기")
        self.sound_toggle_button.clicked.connect(self.toggle_tts_sound)
        center_btn_layout.addWidget(self.sound_toggle_button)
        
        # -----------------------------
        # 4. 예문 TTS 활성/비활성 토글 버튼
        self.example_sound_toggle_button = QPushButton(self)
        self.example_sound_toggle_button.setStyleSheet("border: none;")
        self.example_sound_toggle_button.setFixedSize(20, 20)
        self.example_sound_toggle_button.setIconSize(QSize(20, 20))
        self.example_sound_toggle_button.setIcon(QIcon("assets/example_sound_mute_btn.png"))
        self.example_sound_toggle_button.setToolTip("예문 TTS 켜기/끄기")
        self.example_sound_toggle_button.clicked.connect(self.toggle_example_tts)
        center_btn_layout.addWidget(self.example_sound_toggle_button)

        # -----------------------------
        # 5. 자동 넘어가기 활성/비활성 토글 버튼
        self.auto_toggle_button = QPushButton(self)
        self.auto_toggle_button.setStyleSheet("border: none;")
        self.auto_toggle_button.setFixedSize(20, 20)
        self.auto_toggle_button.setIconSize(QSize(20, 20))
        self.auto_toggle_button.setIcon(QIcon("assets/auto_activate_btn.png"))
        self.auto_toggle_button.setToolTip("자동 넘어가기 켜기/끄기")
        self.auto_toggle_button.clicked.connect(self.toggle_auto_next)
        center_btn_layout.addWidget(self.auto_toggle_button)

        center_btn_layout.addStretch()
        layout.addLayout(center_btn_layout, 0, 1, Qt.AlignCenter)

        # -----------------------------
        # 6. 단어 정보(현재 / 총 개수) 라벨
        self.word_info_label = QLabel(self)
        self.word_info_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.word_info_label.setStyleSheet("font-family: NanumSquareL; font-size: 13px; padding-right: 3px;")
        layout.addWidget(self.word_info_label, 0, 2, Qt.AlignRight)

        # -----------------------------
        # 7. 이전 단어 버튼
        prev_button = QPushButton(self)
        prev_button.setIcon(QIcon("assets/word_previous_btn.png"))
        prev_button.setIconSize(QSize(20, 20))
        prev_button.setFixedSize(20, 20)
        prev_button.setStyleSheet("border: none;")
        prev_button.clicked.connect(self.show_prev_word)
        layout.addWidget(prev_button, 1, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # -----------------------------
        # 8. 단어 표시 라벨
        self.word_display = QLabel(self)
        self.word_display.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.word_display.setWordWrap(True)
        self.word_display.setStyleSheet("color: black; font-size: 16px;")
        layout.addWidget(self.word_display, 1, 1, 1, 4, Qt.AlignCenter)  
        # (1행 4열로 배치)

        # -----------------------------
        # 9. 예문 표시 라벨
        self.example_display = QLabel(self)
        self.example_display.setAlignment(Qt.AlignTop | Qt.AlignCenter)
        self.example_display.setWordWrap(False)
        self.example_display.setStyleSheet("color: gray; font-size: 12px;")
        self.example_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.example_display, 2, 1, 1, 4, Qt.AlignCenter)

        # -----------------------------
        # 10. 다음 단어 버튼
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

        # 0~5열 사용
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

        # auto_next가 켜져 있으면 타이머 시작 (설정된 인터벌 사용)
        if self.is_auto_on:
            self.timer.start(self.auto_interval)

    # =====================
    #   토글 메서드들
    # =====================
    def toggle_example(self):
        """예문 표시 여부를 토글 (예문 텍스트 보이기/숨기기)"""
        self.is_example_shown = not self.is_example_shown
        if self.is_example_shown:
            self.toggle_example_button.setIcon(QIcon("assets/hide_example.png"))
        else:
            self.toggle_example_button.setIcon(QIcon("assets/show_example.png"))
        self.update_word_display()

    def toggle_tts_sound(self):
        """단어/뜻 TTS 재생 여부 토글"""
        self.is_tts_on = not self.is_tts_on
        if self.is_tts_on:
            self.sound_toggle_button.setIcon(QIcon("assets/sound_activate_btn.png"))
        else:
            self.sound_toggle_button.setIcon(QIcon("assets/sound_mute_btn.png"))

    def toggle_example_tts(self):
        """예문 TTS 재생 여부 토글 및 자동 다음 간격 조정"""
        self.is_example_tts_on = not self.is_example_tts_on
        if self.is_example_tts_on:
            self.example_sound_toggle_button.setIcon(QIcon("assets/example_sound_activate_btn.png"))
            self.auto_interval = 14000
        else:
            self.example_sound_toggle_button.setIcon(QIcon("assets/example_sound_mute_btn.png"))
            self.auto_interval = 7000
        # 자동 모드가 켜진 경우 타이머 간격 재설정
        if self.is_auto_on:
            self.timer.start(self.auto_interval)

    def toggle_auto_next(self):
        """자동 넘어가기 여부 토글"""
        self.is_auto_on = not self.is_auto_on
        if self.is_auto_on:
            self.auto_toggle_button.setIcon(QIcon("assets/auto_activate_btn.png"))
            self.timer.start(self.auto_interval)
        else:
            self.auto_toggle_button.setIcon(QIcon("assets/auto_deactivate_btn.png"))
            self.timer.stop()

    # =====================
    #   단어 이동 메서드들
    # =====================
    def auto_next_word(self):
        """설정된 간격마다 다음 단어로 넘어감 (자동 모드 활성 시)"""
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
            self.current_index = len(self.word_list) - 1
        self.update_word_display()

        # 자동 모드가 켜져 있으면 타이머 리셋 (설정된 간격 사용)
        if self.is_auto_on:
            self.timer.start(self.auto_interval)

    def show_next_word(self):
        if not self.word_list:
            return
        if self.current_index < len(self.word_list) - 1:
            self.current_index += 1
        else:
            self.current_index = 0
        self.update_word_display()

        # 자동 모드가 켜져 있으면 타이머 리셋
        if self.is_auto_on:
            self.timer.start(self.auto_interval)

    # =====================
    #   단어 표시 갱신
    # =====================
    def update_word_display(self):
        """현재 단어 및 정보 표시 (TTS 재생 포함)
           - 단어: 즉시 TTS 재생
           - 뜻: 2000ms 후 TTS 재생
           - 예문: (예문 TTS가 활성일 경우) 6000ms 후 영어, 9000ms 후 한글 TTS 재생
           단, 예문은 '-'로 시작하며 '+' 구분자가 있는 경우 처리함.
        """
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

        # 예문 텍스트 표시 (예문이 '-'로 시작하면 처리)
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

        # 단어 정보 (현재/총 개수)
        self.word_info_label.setText(f"{self.current_index + 1}/{len(self.word_list)}")

        # TTS 재생 (TTS가 활성화 되어 있을 때만)
        if self.is_tts_on:
            # 단어 영어 읽기 즉시 실행
            play_tts_in_background(word, lang='en')
            # 2000ms 후에 단어 뜻(한글) 읽기
            QTimer.singleShot(2000, lambda: play_tts_in_background(meaning, lang='ko'))

            # 예문 TTS (예문 TTS가 활성이고, 예문이 '-'로 시작하며 '+' 구분자가 있는 경우)
            if self.is_example_tts_on and example and example.startswith('-') and '+' in example:
                parts = example[1:].split('+', 1)
                if len(parts) == 2:
                    eng_example = parts[0].strip()
                    kor_example = parts[1].strip()
                    # 6000ms 후에 예문 영어 읽기
                    QTimer.singleShot(6000, lambda: play_tts_in_background(eng_example, lang='en'))
                    # 9000ms 후에 예문 한글 읽기
                    QTimer.singleShot(9000, lambda: play_tts_in_background(kor_example, lang='ko'))

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
