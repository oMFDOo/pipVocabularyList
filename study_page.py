# study_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QTableWidget, QTableWidgetItem,
    QRadioButton, QButtonGroup, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import os

# wordbook_manager 모듈 임포트
from wordbook_manager import load_wordbooks, parse_wordbook

class WordbookListItem(QWidget):
    def __init__(self, title, word_count, parent=None):
        super().__init__(parent)
        
        self.title_label = QLabel(title)
        self.count_label = QLabel(f"({word_count})")
        
        # 스타일 설정 (필요에 따라 수정 가능)
        self.title_label.setStyleSheet("font-size: 12px;")
        self.count_label.setStyleSheet("font-size: 8px; color: gray;")
        
        layout = QHBoxLayout()
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.count_label)
        
        self.setLayout(layout)

class StudyPage(QWidget):
    # 작은 창 열기 요청 신호 -> 만약 필요하다면
    open_small_window_signal = pyqtSignal()

    def __init__(self, fonts=None, word_list=None, parent=None):
        super().__init__(parent)
        self.fonts = fonts
        self.word_list = word_list
        self.wordbooks = {}    # 단어장 데이터를 저장할 딕셔너리
        self.word_counts = {}  # 단어장 단어 수를 저장할 딕셔너리

        self.setup_ui()
        self.load_initial_wordbooks()

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
        left_label = QLabel("💙 내 단어")
        left_label.setFont(title_label_font)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.itemClicked.connect(self.display_wordbook)

        # '추가' 버튼 연결
        self.add_button = QPushButton("+")
        self.add_button.setFixedWidth(35)
        self.add_button.clicked.connect(self.add_wordbook)

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
        self.word_table.setRowCount(0)  # 초기에는 빈 테이블

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
        self.radio_group.buttonClicked.connect(self.update_word_table_order)

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

    def load_initial_wordbooks(self):
        """초기 단어장 로드 (words 디렉토리에서)"""
        words_directory = os.path.join(os.path.dirname(__file__), 'words')
        loaded_wordbooks, loaded_word_counts = load_wordbooks(words_directory)
        self.wordbooks = loaded_wordbooks
        self.word_counts = loaded_word_counts

        for title, count in self.word_counts.items():
            item_widget = WordbookListItem(title, count)
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

    def add_wordbook(self):
        """단어장 파일을 추가하는 기능 (파일 다이얼로그 사용)"""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "단어장 파일 추가",
            "",
            "Text Files (*.txt);;All Files (*)",
            options=options
        )
        if file_paths:
            for file_path in file_paths:
                self.load_and_add_wordbook(file_path)

    def load_and_add_wordbook(self, file_path):
        """단어장 파일을 로드하고 리스트에 추가"""
        words, word_count = parse_wordbook(file_path)
        if word_count == 0:
            QMessageBox.warning(self, "오류", f"'{os.path.basename(file_path)}' 파일을 로드할 수 없습니다.")
            return
        
        title = os.path.splitext(os.path.basename(file_path))[0]
        if title in self.wordbooks:
            QMessageBox.information(self, "정보", f"'{title}' 단어장은 이미 추가되었습니다.")
            return

        self.wordbooks[title] = words
        self.word_counts[title] = word_count

        item_widget = WordbookListItem(title, word_count)
        list_item = QListWidgetItem(self.list_widget)
        list_item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, item_widget)

    def display_wordbook(self, item):
        """리스트에서 단어장을 선택했을 때 단어 테이블에 표시"""
        row = self.list_widget.row(item)
        list_item_widget = self.list_widget.itemWidget(item)
        title = list_item_widget.title_label.text()
        words = self.wordbooks.get(title, [])
        
        self.word_table.setRowCount(len(words))
        for row_idx, (eng, kor) in enumerate(words):
            if self.eng_first_radio.isChecked():
                self.word_table.setItem(row_idx, 0, QTableWidgetItem(eng))
                self.word_table.setItem(row_idx, 1, QTableWidgetItem(kor))
            else:
                self.word_table.setItem(row_idx, 0, QTableWidgetItem(kor))
                self.word_table.setItem(row_idx, 1, QTableWidgetItem(eng))
        
        self.word_table.resizeColumnsToContents()

    def update_word_table_order(self):
        """표출 순서 변경 시 단어 테이블 업데이트"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        self.display_wordbook(selected_items[0])

    def request_open_small_window(self):
        """작은 창 열기 요청 신호 발생"""
        self.open_small_window_signal.emit()
