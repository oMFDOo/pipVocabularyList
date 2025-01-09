import sys
from PyQt5.QtWidgets import QApplication
from fonts import load_fonts
from ui_manager import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 폰트 로드 및 매핑
    fonts = load_fonts()

    # MainWindow에 폰트 전달
    window = MainWindow(fonts)
    window.show()
    sys.exit(app.exec_())