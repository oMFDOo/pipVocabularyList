import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
)

class WordbookEditorDialog(QDialog):
    """
    새 단어장(직접 입력)을 위한 QDialog.
    - 단어장 제목
    - 단어 목록(영단어, 뜻, 예문)
    - 저장 시 words/YYMMDD_HHMM/ 폴더에 {제목}_wordbook.txt 형태로 생성
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("새 단어장 추가")
        self.resize(600, 400)
        self.saved_file_path = None  # 저장된 파일 경로를 담을 변수

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 단어장 제목 입력
        layout.addWidget(QLabel("단어장 제목:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("단어장 제목 입력")
        layout.addWidget(self.title_edit)

        # 단어 입력 테이블
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["영단어", "뜻", "예문"])
        layout.addWidget(self.table)

        # 행 추가/삭제 버튼
        row_btn_layout = QHBoxLayout()
        self.add_row_btn = QPushButton("행 추가")
        self.del_row_btn = QPushButton("행 삭제")
        row_btn_layout.addWidget(self.add_row_btn)
        row_btn_layout.addWidget(self.del_row_btn)
        layout.addLayout(row_btn_layout)

        # 저장/취소 버튼
        action_layout = QHBoxLayout()
        self.save_btn = QPushButton("저장")
        self.cancel_btn = QPushButton("취소")
        action_layout.addWidget(self.save_btn)
        action_layout.addWidget(self.cancel_btn)
        layout.addLayout(action_layout)

        # 시그널 연결
        self.add_row_btn.clicked.connect(self.add_row)
        self.del_row_btn.clicked.connect(self.delete_row)
        self.save_btn.clicked.connect(self.save_wordbook)
        self.cancel_btn.clicked.connect(self.reject)

    def add_row(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)

    def delete_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
        else:
            QMessageBox.warning(self, "경고", "삭제할 행을 선택하세요.")

    def save_wordbook(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "경고", "단어장 제목을 입력하세요.")
            return

        # 테이블로부터 단어 목록 수집
        words = []
        for row in range(self.table.rowCount()):
            word_item = self.table.item(row, 0)
            meaning_item = self.table.item(row, 1)
            example_item = self.table.item(row, 2)

            word = word_item.text().strip() if word_item else ""
            meaning = meaning_item.text().strip() if meaning_item else ""
            example = example_item.text().strip() if example_item else ""

            # 최소한 영단어, 뜻은 있어야 저장 (정책에 따라 조정)
            if word and meaning:
                if example:
                    # 파일 저장 형식대로 예문 앞에 '-' 추가
                    example = "-" + example
                words.append({
                    'word': word,
                    'meaning': meaning,
                    'example': example
                })

        if not words:
            QMessageBox.warning(self, "경고", "최소 1개 이상의 단어(영단어, 뜻)를 입력해야 합니다.")
            return

        # 저장 폴더 생성 (날짜 기반)
        date_folder = datetime.now().strftime('%y%m%d_%H%M')
        base_dir = os.path.join(os.path.dirname(__file__), 'words', date_folder)
        os.makedirs(base_dir, exist_ok=True)

        # 파일명: {제목}_wordbook.txt
        filename = f"{title}_wordbook.txt"
        file_path = os.path.join(base_dir, filename)

        # 파일 저장
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for wd in words:
                    f.write(wd['word'] + "\n")
                    f.write(wd['meaning'] + "\n")
                    if wd['example']:
                        f.write(wd['example'] + "\n")

            self.saved_file_path = file_path
            QMessageBox.information(self, "완료", f"'{title}' 단어장이 생성되었습니다.")
            self.accept()  # 다이얼로그 닫기 (Accepted)
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 중 오류가 발생했습니다: {e}")
