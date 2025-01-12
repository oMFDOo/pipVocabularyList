from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class RadioPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("여기는 '단어장' 페이지입니다.")
        layout.addWidget(label)
