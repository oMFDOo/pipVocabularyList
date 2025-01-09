from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QTableWidget, QTableWidgetItem,
    QRadioButton, QButtonGroup, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal

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
                background-color: #ffffff;
                border: 1px solid #ccc;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 15px;
            }
            QLineEdit {
                height: 30px;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(3)
        main_layout.setContentsMargins(3, 3, 3, 3)

        # (1) 상단 타이틀, 설명
        title_label = QLabel("학습하기")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        desc_label = QLabel("외우고 싶은 단어장과 학습 방식을 선택하세요.")
        main_layout.addWidget(title_label)
        main_layout.addWidget(desc_label)

        # (2) 가운데 영역: 왼쪽(주제별 추천 단어), 오른쪽(세부 정보)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(3)

        # 2-1) 왼쪽 리스트
        left_box_layout = QVBoxLayout()
        left_label = QLabel("주제별 추천 단어")
        self.list_widget = QListWidget()
        # 단어장 제목 리스트 출력
        for date_str in ["2025.01.12일자 단어!", "2024.12.28", "2024.10.36", "오늘은 열심히 공부!"]:
            self.list_widget.addItem(date_str)
        self.add_button = QPushButton("+")
        self.add_button.setFixedWidth(40)

        left_box_layout.addWidget(left_label)
        left_box_layout.addWidget(self.list_widget)
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
