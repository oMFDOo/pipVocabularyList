from PyQt5.QtWidgets import QLabel


class ColorBlock(QLabel):
    """색상 블록 위젯"""
    def __init__(self, color, min_width, min_height):
        super().__init__()
        self.setStyleSheet(f"background-color: {color};")
        self.setMinimumSize(min_width, min_height)
