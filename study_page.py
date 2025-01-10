from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QTableWidget, QTableWidgetItem,
    QRadioButton, QButtonGroup, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class StudyPage(QWidget):
    # 작은 창 열기 요청 신호 -> 만약 필요하다면
    open_small_window_signal = pyqtSignal()

    def __init__(self, fonts=None, word_list=None, parent=None):
        super().__init__(parent)
        self.fonts = fonts
        self.word_list = word_list

        self.setup_ui()

    def setup_ui(self):
        """'학습' 페이지 레이아웃 구성"""
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QPushButton {
                color: #fff;
                background-color: #45b1e9;
                border: 1px solid #00000000;
                border-radius: 5px;
                padding: 10px;
                width: 100%;
            }
            QPushButton:hover {
                background-color:#229bd8;
            }
            QLabel {
                font-size: 15px;
            }
            QLineEdit {
                height: 30px;
                border: 2px solid #45b1e9;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget {
                border: 2px solid #45b1e9;
                border-radius: 5px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(3)
        main_layout.setContentsMargins(15, 5, 30, 30)

        # (1) 상단 타이틀, 설명
        main_layout.addSpacing(20)
        title_label = QLabel("학습하기")
        title_label_font = QFont("esamanru Bold")
        title_label.setFont(title_label_font)
        title_label.setStyleSheet("color: #458EE9; font-size: 30px;")
        desc_label_font = QFont("Pretendard Light")
        desc_label = QLabel("외우고 싶은 단어장과 학습 방식을 선택하세요.")
        desc_label.setFont(desc_label_font)
        desc_label.setStyleSheet("margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)

        # (2) 가운데 영역: 왼쪽(주제별 단어 추천받기), 오른쪽(세부 정보)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(5)

        # 2-1) 왼쪽 리스트
        left_box_layout = QVBoxLayout()
        
        self.open_subject_button = QPushButton("주제별 단어 추천받기")
        # date_layout.addWidget(self.open_subject_button)
        left_label = QLabel("💙 내 단어")
        left_label.setFont(title_label_font)
        self.list_widget = QListWidget()
        # 단어장 제목 리스트 출력
        for date_str in ["한 번 보고 바로 잊어버림ㅎㅎ", "이건 외워야지!!", "수능 실전 VOCA 37-54p", "시험 전날 벼락치기 단어 모음", "왜 이걸 몰랐지?", "김밍키 추천 인생 단어 리스트", "외워봤자 못쓰는 지옥의 단어장", "평소엔 안 외우던 생소한 ", "영화 자막에서 건져 올린 ", "내 영어 약점 분석 결과 정리", "선생님이 강조한 필수 ", "어디서 주워들은 고급진 ", "시험 망치고 나서야 정리한 ", "한동안 단어장만 들여다본 결과물", "지금 외워도 늦지 않을 "]:
            self.list_widget.addItem(date_str)
        self.add_button = QPushButton("+")
        self.add_button.setFixedWidth(35)

        left_box_layout.addWidget(left_label)
        left_box_layout.addWidget(self.list_widget)
        left_box_layout.addWidget(self.open_subject_button)
        left_box_layout.addWidget(self.add_button, alignment=Qt.AlignRight)

        # 2-2) 오른쪽 세부 정보
        right_box_layout = QVBoxLayout()
        right_box_layout.setSpacing(3)

        # (2-2-1) 날짜 입력 + 저장 버튼
        date_layout = QHBoxLayout()
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("2025.01.12")
        self.save_button = QPushButton("저장")
        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(self.save_button)

        # (2-2-2) 테이블
        self.word_table = QTableWidget()
        self.word_table.setColumnCount(2)
        self.word_table.setHorizontalHeaderLabels(["영단어", "뜻"])
        self.word_table.setRowCount(5)  # 예시
        example_data = [
            ("apple", "사과 (n)"),
            ("car", "자동차"),
            ("watch", "보다"),
            ("can", "캔"),
            ("do", "도 하는데"),
        ]
        for row, (eng, kor) in enumerate(example_data):
            self.word_table.setItem(row, 0, QTableWidgetItem(eng))
            self.word_table.setItem(row, 1, QTableWidgetItem(kor))

        # (2-2-3) 표출 순서 라디오버튼
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(20)
        radio_label = QLabel("표출 순서:")
        self.eng_first_radio = QRadioButton("영단어 - 뜻")
        self.meaning_first_radio = QRadioButton("뜻 - 영단어")
        self.eng_first_radio.setChecked(True)

        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.eng_first_radio)
        self.radio_group.addButton(self.meaning_first_radio)

        radio_layout.addWidget(radio_label)
        radio_layout.addWidget(self.eng_first_radio)
        radio_layout.addWidget(self.meaning_first_radio)
        radio_layout.addStretch()

        # (2-2-4) 음성 언어 콤보박스
        voice_layout = QHBoxLayout()
        voice_label = QLabel("음성 언어:")
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["미국-여성", "영국-남성", "한국-여성"])
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.voice_combo)
        voice_layout.addStretch()

        # (2-2-5) 학습 시작 버튼
        self.start_button = QPushButton("학습 시작")
        self.start_button.clicked.connect(self.request_open_small_window)

        # 오른쪽 레이아웃에 순서대로 배치
        right_box_layout.addLayout(date_layout)
        right_box_layout.addWidget(self.word_table)
        right_box_layout.addLayout(radio_layout)
        right_box_layout.addLayout(voice_layout)
        right_box_layout.addWidget(self.start_button, alignment=Qt.AlignRight)

        # Middle layout 합치기
        middle_layout.addLayout(left_box_layout, 2)
        middle_layout.addLayout(right_box_layout, 5)

        main_layout.addLayout(middle_layout)

    def request_open_small_window(self):
        """작은 창 열기 요청 신호 발생"""
        self.open_small_window_signal.emit()
