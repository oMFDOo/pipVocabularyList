import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from fonts import load_fonts
from big_window import BigWindow
from small_window import SmallWindow
import words

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/logo_s.png"))

    # 폰트 로드
    fonts = load_fonts()

    # 큰 창과 작은 창 생성
    big_window = BigWindow(fonts, words.WORDS)
    small_window = SmallWindow(fonts, words.WORDS)

    # 신호 연결: 큰 창에서 작은 창 열기 요청
    big_window.open_small_window_signal.connect(lambda: open_small_window(big_window, small_window))

    # 신호 연결: 작은 창에서 큰 창 열기 요청
    small_window.open_big_window_signal.connect(lambda: open_big_window(big_window, small_window))

    # 초기에는 큰 창만 표시
    big_window.show()

    sys.exit(app.exec_())

def open_small_window(big_window, small_window):
    """큰 창에서 작은 창을 열고 큰 창을 숨깁니다."""
    big_window.hide()
    small_window.show()

def open_big_window(big_window, small_window):
    """작은 창에서 큰 창을 열고 작은 창을 숨깁니다."""
    small_window.hide()
    big_window.show()

if __name__ == "__main__":
    main()
