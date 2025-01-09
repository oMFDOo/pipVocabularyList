import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from fonts import load_fonts
from ui_manager import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/logo_s.png"))

    # 폰트 로드 및 매핑
    fonts = load_fonts()

    # MainWindow에 폰트 전달
    window = MainWindow(fonts)
    window.show()
    sys.exit(app.exec_())