import os
import shutil
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QTableWidget, QTableWidgetItem,
    QRadioButton, QButtonGroup, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

# 수정된 wordbook_manager 모듈 임포트
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
    # 작은 창 열기 요청 신호 (단어장 리스트를 전달)
    open_small_window_signal = pyqtSignal(list)

    def __init__(self, fonts=None, word_list=None, parent=None):
        super().__init__(parent)
        self.fonts = fonts
        self.word_list = word_list

        # 단어장 데이터를 저장할 딕셔너리
        self.wordbooks = {}         # {title: [ {word, meaning, example}, ... ], ... }
        # 단어장 단어 수를 저장할 딕셔너리
        self.word_counts = {}       # {title: count, ... }
        # 각 단어장의 실제 파일 경로를 저장할 딕셔너리 (저장 시 사용)
        self.wordbook_paths = {}    # {title: file_path, ... }

        self.setup_ui()
        self.load_initial_wordbooks()

    def setup_ui(self):
        """'학습' 페이지 레이아웃 구성"""
        self.setStyleSheet("""
            QPushButton {
                color: #fff;
                background-color: #45b1e9;
                border: 1px solid #ffffffff;
                border-radius: 6px;
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
                height: 20px;
                border: 2px solid #45b1e9;
                border-radius: 6px;
                padding: 5px;
                font-family: 'Pretendard'; 
                font-size: 14px;
            }
            QTableWidget {
                border: 2px solid #45b1e9;
                border-radius: 6px;
            }
            QListWidget {
                border: 2px solid #45b1e9;
                border-radius: 6px;
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
        self.open_subject_button.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        left_label = QLabel("💙 내 단어")
        left_label.setStyleSheet("font-family: 'esamanru Bold'; font-size: 23px;")

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-family: 'Pretendard'; font-size: 14px;")
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.itemClicked.connect(self.display_wordbook)

        self.add_button = QPushButton("단어 불러오기")
        add_button_font = QFont("Pretendard")
        self.add_button.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.add_button.setFont(add_button_font)
        self.add_button.setFixedWidth(250)
        self.add_button.setMaximumWidth(250)
        self.add_button.clicked.connect(self.add_wordbook)

        left_box_layout.addWidget(left_label)
        left_box_layout.addWidget(self.list_widget)
        left_box_layout.addWidget(self.open_subject_button)
        left_box_layout.addWidget(self.add_button, alignment=Qt.AlignRight)

        # 2-2) 오른쪽 세부 정보
        right_box_layout = QVBoxLayout()
        right_box_layout.setSpacing(3)

        # (2-2-1) 제목(단어장 이름) 입력 + 저장 버튼
        date_layout = QHBoxLayout()
        # '학습할 단어장을 선택해주세요.' 대신 '선택된 단어장 제목'을 보여줌
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("학습할 단어장을 선택해주세요.")
        self.date_edit.setReadOnly(True)  # 사용자가 수정하지 못하도록 설정

        # 저장 버튼: 테이블 수정한 내용 파일로 저장
        self.save_button = QPushButton("저장")
        self.save_button.setStyleSheet("font-family: 'Pretendard'; font-size: 14px;")
        self.save_button.clicked.connect(self.save_wordbook)

        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(self.save_button)

        # (2-2-2) 테이블 (영단어/뜻/예문 3개 컬럼)
        self.word_table = QTableWidget()
        self.word_table.setColumnCount(3)
        self.word_table.setHorizontalHeaderLabels(["영단어", "뜻", "예문"])
        self.word_table.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.word_table.setRowCount(0)  # 초기에는 빈 테이블

        # (2-2-3) 표출 순서 라디오버튼
        radio_layout = QHBoxLayout()
        radio_label = QLabel("표출 순서 ")
        radio_label.setStyleSheet("font-family: 'esamanru Light'; font-size: 16px; color: #45b1e9;")
        self.eng_first_radio = QRadioButton("영단어 - 뜻")
        self.meaning_first_radio = QRadioButton("뜻 - 영단어")
        self.eng_first_radio.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.meaning_first_radio.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
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
        voice_label = QLabel("음성 언어 ")
        voice_label.setStyleSheet("font-family: 'esamanru Light'; font-size: 16px; color: #45b1e9;")
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["미국-여성", "영국-남성", "한국-여성"])
        self.voice_combo.setStyleSheet("""
            font-family: 'Pretendard';
            font-size: 14px;
            background-color: #fff;
            border: solid 1px #45b1e9;
            padding: 5px 15px 5px 15px;
        """)
        voice_layout.addWidget(voice_label)
        voice_layout.addWidget(self.voice_combo)
        voice_layout.addStretch()

        # (2-2-5) 학습 시작 버튼
        self.start_button = QPushButton("학습 시작")
        self.start_button.setStyleSheet("font-family: 'Pretendard ExtraBold'; font-size: 20px;")
        self.start_button.clicked.connect(self.request_open_small_window)

        # 오른쪽 레이아웃에 순서대로 배치
        right_box_layout.addLayout(date_layout)
        right_box_layout.addWidget(self.word_table)
        right_box_layout.addLayout(radio_layout)
        right_box_layout.addLayout(voice_layout)
        right_box_layout.addWidget(self.start_button, alignment=Qt.AlignRight)

        # Middle layout 합치기
        middle_layout.addLayout(left_box_layout, 1)
        middle_layout.addLayout(right_box_layout, 4)

        main_layout.addLayout(middle_layout)

    def load_initial_wordbooks(self):
        """초기 단어장 로드 (words 디렉토리에서 _wordbook.txt만)"""
        words_directory = os.path.join(os.path.dirname(__file__), 'words')
        loaded_wordbooks, loaded_word_counts = load_wordbooks(words_directory)
        self.wordbooks = loaded_wordbooks
        self.word_counts = loaded_word_counts

        # 이미 존재하는 _wordbook.txt 파일은 title-파일경로 매핑 (재귀 탐색으로 얻은 경로)
        for root, dirs, files in os.walk(words_directory):
            for filename in files:
                if filename.endswith('_wordbook.txt'):
                    # 제목에서 '_wordbook' 제거
                    title = os.path.splitext(filename)[0]
                    if title.endswith('_wordbook'):
                        title = title[:-len('_wordbook')]
                    file_path = os.path.join(root, filename)
                    self.wordbook_paths[title] = file_path

        # 로드된 단어장들을 리스트에 표시
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
        """
        단어장 파일을 로드하고 리스트에 추가.
        프로그램 재시작 후에도 유지하도록 
        words/YYMMDD_HHMM/ (예: 250112_1754) 폴더에 복사해둔다 (이미 없으면).
        파일 이름은 자동으로 `_wordbook.txt` 형태로 맞춰 저장한다.
        """
        # (1) 날짜 폴더 생성: 예) 2025년 1월 12일 17시 54분 -> '250112_1754'
        date_folder_name = datetime.now().strftime('%y%m%d_%H%M')
        words_dir = os.path.join(os.path.dirname(__file__), 'words', date_folder_name)
        if not os.path.exists(words_dir):
            os.makedirs(words_dir, exist_ok=True)

        # (2) 현재 선택한 파일의 원래 이름(확장자 제외)을 가져옴
        basename = os.path.splitext(os.path.basename(file_path))[0]

        # (3) _wordbook.txt 형식으로 새 파일명 생성
        #     이미 _wordbook 으로 끝난다면, 또 붙이지 않고 그대로 쓸 수도 있음
        if not basename.endswith('_wordbook'):
            new_filename = f"{basename}_wordbook.txt"
        else:
            new_filename = f"{basename}.txt"

        new_path = os.path.join(words_dir, new_filename)

        # (4) 파일 복사
        try:
            shutil.copyfile(file_path, new_path)
        except Exception as e:
            QMessageBox.warning(self, "오류", f"파일 복사 중 오류 발생: {e}")
            return

        # (5) 복사된 파일을 파싱하여 wordbooks에 로드
        words, word_count = parse_wordbook(new_path)
        if word_count == 0:
            QMessageBox.warning(self, "오류", f"'{os.path.basename(file_path)}' 파일을 로드할 수 없습니다.")
            return

        # 타이틀은 파일명에서 '_wordbook'을 제거한 부분
        title = os.path.splitext(new_filename)[0]
        if title.endswith('_wordbook'):
            title = title[:-len('_wordbook')]

        # 이미 존재하는 타이틀인지 확인
        if title in self.wordbooks:
            QMessageBox.information(self, "정보", f"'{title}' 단어장은 이미 추가되었습니다.")
            return

        # wordbooks, word_counts, wordbook_paths에 정보 저장
        self.wordbooks[title] = words
        self.word_counts[title] = word_count
        self.wordbook_paths[title] = new_path

        # 리스트에 UI 아이템 추가
        item_widget = WordbookListItem(title, word_count)
        list_item = QListWidgetItem(self.list_widget)
        list_item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, item_widget)

    def display_wordbook(self, item):
        """리스트에서 단어장을 선택했을 때 단어 테이블에 표시하고, 제목을 date_edit에 입력"""
        list_item_widget = self.list_widget.itemWidget(item)
        title = list_item_widget.title_label.text()

        # 제목 라인에디트에 표시
        self.date_edit.setText(title)

        words = self.wordbooks.get(title, [])
        self.word_table.setRowCount(len(words))

        for row_idx, word_data in enumerate(words):
            # (1) 영단어/뜻
            if self.eng_first_radio.isChecked():
                eng = word_data.get('word', "")
                kor = word_data.get('meaning', "")
            else:
                eng = word_data.get('meaning', "")
                kor = word_data.get('word', "")

            self.word_table.setItem(row_idx, 0, QTableWidgetItem(eng))
            self.word_table.setItem(row_idx, 1, QTableWidgetItem(kor))

            # (2) 예문 처리:
            example_raw = word_data.get('example', "").strip()  # 예: "-hello +안녕"
            if example_raw.startswith('-'):
                example_raw = example_raw[1:].strip()  # 맨 앞 '-' 제거
            self.word_table.setItem(row_idx, 2, QTableWidgetItem(example_raw))

        self.word_table.resizeColumnsToContents()

    def update_word_table_order(self):
        """표출 순서 변경 시 단어 테이블 업데이트"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        self.display_wordbook(selected_items[0])

    def save_wordbook(self):
        """
        현재 선택된 단어장의 테이블 내용을 다시 파일로 저장.
        """
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "경고", "먼저 단어장을 선택하세요.")
            return

        list_item_widget = self.list_widget.itemWidget(selected_items[0])
        title = list_item_widget.title_label.text()

        if title not in self.wordbooks or title not in self.wordbook_paths:
            QMessageBox.warning(self, "경고", "해당 단어장의 정보를 찾을 수 없습니다.")
            return

        original_words = self.wordbooks[title]
        updated_words = []

        for row_idx in range(self.word_table.rowCount()):
            eng_item = self.word_table.item(row_idx, 0)
            kor_item = self.word_table.item(row_idx, 1)
            ex_item = self.word_table.item(row_idx, 2)

            if not eng_item or not kor_item or not ex_item:
                continue

            eng_text = eng_item.text().strip()
            kor_text = kor_item.text().strip()
            ex_text = ex_item.text().strip()

            # 라디오버튼에 따라 실제 word/meaning 위치를 다시 맞춰준다
            if self.eng_first_radio.isChecked():
                word_str = eng_text
                meaning_str = kor_text
            else:
                word_str = kor_text
                meaning_str = eng_text

            # 예문이 비어있지 않다면 맨 앞에 '-' 붙여서 저장
            if ex_text:
                ex_final = "-" + ex_text
            else:
                ex_final = ""

            updated_words.append({
                'word': word_str,
                'meaning': meaning_str,
                'example': ex_final
            })

        # 파일 경로
        file_path = self.wordbook_paths[title]
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for wd in updated_words:
                    f.write(wd['word'] + "\n")
                    f.write(wd['meaning'] + "\n")
                    if wd['example']:
                        f.write(wd['example'] + "\n")

            self.wordbooks[title] = updated_words
            self.word_counts[title] = len(updated_words)

            QMessageBox.information(self, "저장 완료", f"'{title}' 단어장이 저장되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"단어장을 저장하는 중 오류가 발생했습니다: {e}")

    def request_open_small_window(self):
        """작은 창 열기 요청 신호 발생 (현재 선택된 단어장 전달)"""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "경고", "먼저 단어장을 선택하세요.")
            return
        list_item_widget = self.list_widget.itemWidget(selected_items[0])
        title = list_item_widget.title_label.text()
        word_list = self.wordbooks.get(title, [])
        if not word_list:
            QMessageBox.warning(self, "경고", "선택된 단어장이 비어 있습니다.")
            return
        self.open_small_window_signal.emit(word_list)
