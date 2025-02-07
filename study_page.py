import os
import shutil
import random  # 단어 섞기를 위해 추가
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QLineEdit, QTableWidget, QTableWidgetItem,
    QRadioButton, QButtonGroup, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon

from wordbook_manager import load_wordbooks, parse_wordbook
from wordbook_editor import WordbookEditorDialog


class WordbookListItem(QWidget):
    """
    리스트에 보여질 아이템 위젯 (제목, 단어 개수)
    """
    def __init__(self, title, word_count, parent=None):
        super().__init__(parent)
        self.title_label = QLabel(title)
        self.count_label = QLabel(f"({word_count})")

        # 스타일 (필요 시 수정)
        self.title_label.setStyleSheet("font-size: 12px;")
        self.count_label.setStyleSheet("font-size: 8px; color: gray;")

        layout = QHBoxLayout()
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.count_label)
        self.setLayout(layout)


class StudyPage(QWidget):
    """
    - 내 단어장 목록(좌측 QListWidget)
    - 선택한 단어장 내용(QTableWidget) 편집 (행 추가/삭제 가능 + '단어 섞기' 버튼)
    - 새 단어장 추가 (직접 입력), 기존 단어장 파일 불러오기, 단어장 삭제
    - 단어장 제목 변경 시 파일 rename 처리
    """
    open_small_window_signal = pyqtSignal(list)  # 작은 창 열기 요청 신호

    def __init__(self, fonts=None, word_list=None, parent=None):
        super().__init__(parent)
        self.fonts = fonts
        self.word_list = word_list

        # 내부 데이터
        self.wordbooks = {}       # {title: [ {word, meaning, example}, ... ], ...}
        self.word_counts = {}     # {title: count, ...}
        self.wordbook_paths = {}  # {title: file_path, ...}

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

        # (2) 가운데 영역: 왼쪽(단어장 리스트), 오른쪽(세부 정보)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(5)

        # 2-1) 왼쪽: 내 단어장 리스트
        left_box_layout = QVBoxLayout()

        # [수정] 주제별 단어 추천받기 버튼 주석 처리
        # self.open_subject_button = QPushButton("주제별 단어 추천받기")
        # self.open_subject_button.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")

        left_label = QLabel("💙 내 단어")
        left_label.setStyleSheet("font-family: 'esamanru Bold'; font-size: 23px;")

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("font-family: 'Pretendard'; font-size: 14px; height: 200px; width: 100px;")
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.itemClicked.connect(self.display_wordbook)

        # (2-1-A) 기존: 파일로 단어장 불러오기
        self.add_file_button = QPushButton("단어장 불러오기")
        self.add_file_button.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.add_file_button.clicked.connect(self.add_wordbook)

        # (2-1-B) 새 단어장 추가(직접 입력)
        self.new_wordbook_btn = QPushButton("새 단어장 추가")
        self.new_wordbook_btn.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.new_wordbook_btn.clicked.connect(self.open_new_wordbook_dialog)

        # (2-1-C) 단어장 삭제
        self.delete_wordbook_btn = QPushButton("선택 단어장 삭제")
        self.delete_wordbook_btn.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.delete_wordbook_btn.clicked.connect(self.delete_selected_wordbook)

        # 왼쪽 레이아웃 배치
        left_box_layout.addWidget(left_label)
        left_box_layout.addWidget(self.list_widget)
        # left_box_layout.addWidget(self.open_subject_button)  # [주석 처리]
        left_box_layout.addWidget(self.add_file_button)
        left_box_layout.addWidget(self.new_wordbook_btn)
        left_box_layout.addWidget(self.delete_wordbook_btn)
        left_box_layout.addStretch(1)

        # 2-2) 오른쪽: 단어장 편집 (테이블, 저장, 학습 시작 등)
        right_box_layout = QVBoxLayout()
        right_box_layout.setSpacing(3)

        # (2-2-1) 단어장 제목(수정 가능) + 저장 버튼
        date_layout = QHBoxLayout()
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("학습할 단어장을 선택해주세요.")

        self.save_button = QPushButton("저장")
        self.save_button.setStyleSheet("font-family: 'Pretendard'; font-size: 14px;")
        self.save_button.clicked.connect(self.save_wordbook)

        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(self.save_button)

        # (2-2-2) 단어 테이블
        self.word_table = QTableWidget()
        self.word_table.setColumnCount(3)
        self.word_table.setHorizontalHeaderLabels(["영단어", "뜻", "예문"])
        self.word_table.setStyleSheet("font-family: 'Pretendard'; font-size: 16px;")
        self.word_table.setRowCount(0)

        # (2-2-3) 테이블 행 추가/삭제 + [수정] 단어 섞기 버튼
        table_btn_layout = QHBoxLayout()

        # --- 행 추가 버튼 (이미지 아이콘) ---
        self.add_row_btn = QPushButton()
        self.add_row_btn.setIcon(QIcon("./assets/row_plus_btn.png"))  # 이미지 적용
        self.add_row_btn.setIconSize(QSize(24, 24))
        self.add_row_btn.setToolTip("행 추가")
        self.add_row_btn.setStyleSheet("border: none; background-color: #ffffff; width: 24px; height: 24px; padding: 0px; margin: 0px;")
        self.add_row_btn.clicked.connect(self.add_table_row)

        # --- 행 삭제 버튼 (이미지 아이콘) ---
        self.delete_row_btn = QPushButton()
        self.delete_row_btn.setIcon(QIcon("./assets/row_minus_btn.png"))
        self.delete_row_btn.setIconSize(QSize(24, 24))
        self.delete_row_btn.setToolTip("행 삭제")
        self.delete_row_btn.setStyleSheet("border: none; background-color: #ffffff; width: 24px; height: 24px; padding: 0px; margin: 0px;")
        self.delete_row_btn.clicked.connect(self.delete_table_row)

        # --- [추가] 단어 섞기 버튼 (이미지 아이콘) ---
        self.shuffle_btn = QPushButton()
        self.shuffle_btn.setIcon(QIcon("./assets/word_shuffle_btn.png"))
        self.shuffle_btn.setIconSize(QSize(24, 24))
        self.shuffle_btn.setToolTip("단어 섞기")
        self.shuffle_btn.setStyleSheet("border: none; background-color: #ffffff; width: 24px; height: 24px; padding: 0px; margin: 0px;")
        self.shuffle_btn.clicked.connect(self.shuffle_words)

        table_btn_layout.addWidget(self.add_row_btn)
        table_btn_layout.addWidget(self.delete_row_btn)
        table_btn_layout.addWidget(self.shuffle_btn)
        table_btn_layout.addStretch(1)

        # (2-2-4) 표출 순서(영단어→뜻 / 뜻→영단어)
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

        # (2-2-5) 음성 언어 콤보박스
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

        # (2-2-6) 학습 시작 버튼
        self.start_button = QPushButton("학습 시작")
        self.start_button.setStyleSheet("font-family: 'Pretendard ExtraBold'; font-size: 20px;")
        self.start_button.clicked.connect(self.request_open_small_window)

        # 오른쪽 레이아웃 배치
        right_box_layout.addLayout(date_layout)
        right_box_layout.addWidget(self.word_table)
        right_box_layout.addLayout(table_btn_layout)
        right_box_layout.addLayout(radio_layout)
        right_box_layout.addLayout(voice_layout)
        right_box_layout.addWidget(self.start_button, alignment=Qt.AlignRight)

        # 전체 합치기
        middle_layout.addLayout(left_box_layout, 1)
        middle_layout.addLayout(right_box_layout, 4)
        main_layout.addLayout(middle_layout)

    def load_initial_wordbooks(self):
        words_directory = os.path.join(os.path.dirname(__file__), 'words')
        loaded_wordbooks, loaded_word_counts = load_wordbooks(words_directory)
        self.wordbooks = loaded_wordbooks
        self.word_counts = loaded_word_counts

        # 파일 경로 매핑
        for root, dirs, files in os.walk(words_directory):
            for filename in files:
                if filename.endswith('_wordbook.txt'):
                    title = os.path.splitext(filename)[0]
                    if title.endswith('_wordbook'):
                        title = title[:-len('_wordbook')]
                    file_path = os.path.join(root, filename)
                    self.wordbook_paths[title] = file_path

        # QListWidget 표시
        for title, count in self.word_counts.items():
            item_widget = WordbookListItem(title, count)
            list_item = QListWidgetItem(self.list_widget)
            list_item.setSizeHint(item_widget.sizeHint())
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, item_widget)

    def add_wordbook(self):
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
        date_folder_name = datetime.now().strftime('%y%m%d_%H%M')
        words_dir = os.path.join(os.path.dirname(__file__), 'words', date_folder_name)
        os.makedirs(words_dir, exist_ok=True)

        basename = os.path.splitext(os.path.basename(file_path))[0]
        if not basename.endswith('_wordbook'):
            new_filename = f"{basename}_wordbook.txt"
        else:
            new_filename = f"{basename}.txt"

        new_path = os.path.join(words_dir, new_filename)

        try:
            shutil.copyfile(file_path, new_path)
        except Exception as e:
            QMessageBox.warning(self, "오류", f"파일 복사 중 오류 발생: {e}")
            return

        words, word_count = parse_wordbook(new_path)
        if word_count == 0:
            QMessageBox.warning(self, "오류", f"'{os.path.basename(file_path)}' 파일을 로드할 수 없습니다.")
            return

        title = os.path.splitext(new_filename)[0]
        if title.endswith('_wordbook'):
            title = title[:-len('_wordbook')]

        if title in self.wordbooks:
            QMessageBox.information(self, "정보", f"'{title}' 단어장은 이미 추가되었습니다.")
            return

        self.wordbooks[title] = words
        self.word_counts[title] = word_count
        self.wordbook_paths[title] = new_path

        item_widget = WordbookListItem(title, word_count)
        list_item = QListWidgetItem(self.list_widget)
        list_item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, item_widget)

    def open_new_wordbook_dialog(self):
        dialog = WordbookEditorDialog(self)
        if dialog.exec_() == dialog.Accepted:
            new_file = dialog.saved_file_path
            if new_file:
                words, count = parse_wordbook(new_file)
                if count > 0:
                    title = os.path.splitext(os.path.basename(new_file))[0]
                    if title.endswith('_wordbook'):
                        title = title[:-len('_wordbook')]

                    self.wordbooks[title] = words
                    self.word_counts[title] = count
                    self.wordbook_paths[title] = new_file

                    item_widget = WordbookListItem(title, count)
                    list_item = QListWidgetItem(self.list_widget)
                    list_item.setSizeHint(item_widget.sizeHint())
                    self.list_widget.addItem(list_item)
                    self.list_widget.setItemWidget(list_item, item_widget)

                    QMessageBox.information(self, "완료", f"'{title}' 단어장이 추가되었습니다.")
                else:
                    QMessageBox.warning(self, "경고", "단어장에 단어가 없습니다.")

    def delete_selected_wordbook(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "경고", "삭제할 단어장을 선택하세요.")
            return
        list_item = selected_items[0]
        list_item_widget = self.list_widget.itemWidget(list_item)
        title = list_item_widget.title_label.text()

        reply = QMessageBox.question(self, "확인",
                                     f"'{title}' 단어장을 삭제하시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            file_path = self.wordbook_paths.get(title)
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    QMessageBox.critical(self, "오류", f"파일 삭제 중 오류: {e}")
                    return

            if title in self.wordbooks:
                del self.wordbooks[title]
            if title in self.word_counts:
                del self.word_counts[title]
            if title in self.wordbook_paths:
                del self.wordbook_paths[title]

            row = self.list_widget.row(list_item)
            self.list_widget.takeItem(row)

            QMessageBox.information(self, "삭제 완료", f"'{title}' 단어장이 삭제되었습니다.")

    def display_wordbook(self, item):
        list_item_widget = self.list_widget.itemWidget(item)
        title = list_item_widget.title_label.text()

        self.date_edit.setText(title)

        words = self.wordbooks.get(title, [])
        self.word_table.setRowCount(len(words))

        for row_idx, word_data in enumerate(words):
            if self.eng_first_radio.isChecked():
                eng = word_data.get('word', "")
                kor = word_data.get('meaning', "")
            else:
                eng = word_data.get('meaning', "")
                kor = word_data.get('word', "")

            self.word_table.setItem(row_idx, 0, QTableWidgetItem(eng))
            self.word_table.setItem(row_idx, 1, QTableWidgetItem(kor))

            example_raw = word_data.get('example', "").strip()
            if example_raw.startswith('-'):
                example_raw = example_raw[1:].strip()
            self.word_table.setItem(row_idx, 2, QTableWidgetItem(example_raw))

        self.word_table.resizeColumnsToContents()

    def update_word_table_order(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        self.display_wordbook(selected_items[0])

    # (행 추가/삭제 기존 동일)
    def add_table_row(self):
        self.word_table.insertRow(self.word_table.rowCount())

    def delete_table_row(self):
        current_row = self.word_table.currentRow()
        if current_row >= 0:
            self.word_table.removeRow(current_row)
        else:
            QMessageBox.warning(self, "경고", "삭제할 행을 선택하세요.")

    # (추가) 단어 섞기 기능
    def shuffle_words(self):
        """
        테이블의 현재 단어들을 무작위로 섞는다.
        """
        row_count = self.word_table.rowCount()
        if row_count < 2:
            return  # 섞을 단어가 1개 이하라면 그냥 종료

        # 1) 현재 테이블 데이터를 모두 읽어온 뒤
        data_list = []
        for r in range(row_count):
            col0 = self.word_table.item(r, 0).text() if self.word_table.item(r, 0) else ""
            col1 = self.word_table.item(r, 1).text() if self.word_table.item(r, 1) else ""
            col2 = self.word_table.item(r, 2).text() if self.word_table.item(r, 2) else ""
            data_list.append([col0, col1, col2])

        # 2) random.shuffle()로 섞고
        random.shuffle(data_list)

        # 3) 다시 테이블에 반영
        for r in range(row_count):
            self.word_table.setItem(r, 0, QTableWidgetItem(data_list[r][0]))
            self.word_table.setItem(r, 1, QTableWidgetItem(data_list[r][1]))
            self.word_table.setItem(r, 2, QTableWidgetItem(data_list[r][2]))

    def save_wordbook(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "경고", "먼저 단어장을 선택하세요.")
            return

        list_item = selected_items[0]
        list_item_widget = self.list_widget.itemWidget(list_item)
        old_title = list_item_widget.title_label.text()

        if old_title not in self.wordbooks or old_title not in self.wordbook_paths:
            QMessageBox.warning(self, "경고", "해당 단어장의 정보를 찾을 수 없습니다.")
            return

        new_title = self.date_edit.text().strip()
        if not new_title:
            QMessageBox.warning(self, "경고", "단어장 제목을 입력하세요.")
            return

        # (1) 제목 변경 처리
        if new_title != old_title:
            if new_title in self.wordbook_paths:
                QMessageBox.warning(self, "경고", f"이미 '{new_title}' 단어장이 존재합니다.")
                return

            old_path = self.wordbook_paths[old_title]
            folder = os.path.dirname(old_path)
            new_filename = f"{new_title}_wordbook.txt"
            new_path = os.path.join(folder, new_filename)

            try:
                os.rename(old_path, new_path)
            except Exception as e:
                QMessageBox.critical(self, "오류", f"파일 이름 변경 중 오류 발생: {e}")
                return

            # 내부 딕셔너리 key 변경
            self.wordbooks[new_title] = self.wordbooks[old_title]
            self.word_counts[new_title] = self.word_counts[old_title]
            self.wordbook_paths[new_title] = new_path

            del self.wordbooks[old_title]
            del self.word_counts[old_title]
            del self.wordbook_paths[old_title]

            list_item_widget.title_label.setText(new_title)

        final_title = new_title
        updated_words = []
        for row_idx in range(self.word_table.rowCount()):
            eng_item = self.word_table.item(row_idx, 0)
            kor_item = self.word_table.item(row_idx, 1)
            ex_item = self.word_table.item(row_idx, 2)

            eng_text = eng_item.text().strip() if eng_item else ""
            kor_text = kor_item.text().strip() if kor_item else ""
            ex_text = ex_item.text().strip() if ex_item else ""

            if self.eng_first_radio.isChecked():
                word_str = eng_text
                meaning_str = kor_text
            else:
                word_str = kor_text
                meaning_str = eng_text

            if ex_text:
                ex_final = "-" + ex_text
            else:
                ex_final = ""

            if word_str or meaning_str:
                updated_words.append({
                    'word': word_str,
                    'meaning': meaning_str,
                    'example': ex_final
                })

        # (2) 파일에 저장
        file_path = self.wordbook_paths[final_title]
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for wd in updated_words:
                    f.write(wd['word'] + "\n")
                    f.write(wd['meaning'] + "\n")
                    if wd['example']:
                        f.write(wd['example'] + "\n")

            self.wordbooks[final_title] = updated_words
            self.word_counts[final_title] = len(updated_words)

            # [추가] 왼쪽 리스트의 단어 개수도 갱신
            list_item_widget.count_label.setText(f"({len(updated_words)})")

            QMessageBox.information(self, "저장 완료", f"'{final_title}' 단어장이 저장되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"단어장을 저장하는 중 오류가 발생했습니다: {e}")

    def request_open_small_window(self):
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
