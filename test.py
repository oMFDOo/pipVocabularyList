import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox
)


class VocabularyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("학습하기")
        self.resize(1000, 700)

        # 메인 위젯 및 레이아웃 설정
        main_widget = QWidget(self)
        main_layout = QGridLayout(main_widget)
        self.setCentralWidget(main_widget)

        # ===== 사이드바 =====
        sidebar = self.create_sidebar()
        main_layout.addLayout(sidebar, 0, 0, 2, 1)  # 좌측 상단에 배치 (2행 차지)

        # ===== 상단 영역 =====
        top_section = self.create_top_section()
        main_layout.addLayout(top_section, 0, 1)  # 우측 상단에 배치

        # ===== 중앙 데이터 테이블 =====
        table_section = self.create_table_section()
        main_layout.addWidget(table_section, 1, 1)  # 우측 중앙에 배치

    def create_sidebar(self):
        """사이드바 구성"""
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(QLabel("학습"))  # 상단 라벨
        sidebar_layout.addWidget(QPushButton("2025.01.12"))
        sidebar_layout.addWidget(QPushButton("2024.12.28"))
        sidebar_layout.addWidget(QPushButton("2024.10.36"))
        sidebar_layout.addWidget(QPushButton("오늘은 진짜"))
        sidebar_layout.addWidget(QPushButton("+"))  # 하단 추가 버튼
        return sidebar_layout

    def create_top_section(self):
        """상단 입력 및 버튼 영역"""
        top_layout = QHBoxLayout()
        input_box = QLineEdit()
        input_box.setPlaceholderText("날짜를 입력하세요.")
        save_button = QPushButton("저장")
        top_layout.addWidget(input_box)
        top_layout.addWidget(save_button)
        return top_layout

    def create_table_section(self):
        """중앙 데이터 테이블 및 우측 컨트롤"""
        table_widget = QWidget()
        table_layout = QGridLayout(table_widget)

        # 데이터 테이블
        table = QTableWidget(10, 2)  # 10행 2열
        table.setHorizontalHeaderLabels(["단어", "뜻"])
        for i in range(10):
            table.setItem(i, 0, QTableWidgetItem(f"word {i+1}"))
            table.setItem(i, 1, QTableWidgetItem(f"meaning {i+1}"))

        # 우측 컨트롤 버튼
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(QLabel("표출 순서"))
        controls_layout.addWidget(QPushButton("영단어 - 뜻"))
        controls_layout.addWidget(QPushButton("뜻 - 영단어"))
        controls_layout.addWidget(QLabel("음성 언어"))
        dropdown = QComboBox()
        dropdown.addItems(["미국-여성", "미국-남성"])
        controls_layout.addWidget(dropdown)
        controls_layout.addWidget(QPushButton("학습 시작"))

        # 레이아웃 병합
        table_layout.addWidget(table, 0, 0)
        table_layout.addLayout(controls_layout, 0, 1)

        return table_widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VocabularyApp()
    window.show()
    sys.exit(app.exec_())
