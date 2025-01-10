import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from fonts import load_fonts
from main_window import MainWindow  # MainWindow로 변경
from small_window import SmallWindow
import words

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/logo_s.png"))

    # 폰트 로드
    fonts = load_fonts()
    print(fonts)

    # 메인 윈도우와 작은 창 생성
    main_window = MainWindow(fonts)  # MainWindow 생성
    small_window = SmallWindow(fonts)  # word_list는 추후 설정

    # 신호 연결: 메인 윈도우에서 작은 창 열기 요청
    main_window.study_page.open_small_window_signal.connect(
        lambda word_list: open_small_window(main_window, small_window, word_list)
    )

    # 신호 연결: 작은 창에서 메인 윈도우 열기 요청
    small_window.open_main_window_signal.connect(
        lambda: open_main_window(main_window, small_window)
    )
    
    # 초기에는 메인 윈도우만 표시
    main_window.show()

    sys.exit(app.exec_())

def open_small_window(main_window, small_window, word_list):
    """메인 윈도우에서 작은 창을 열고 메인 윈도우를 숨깁니다."""
    small_window.set_word_list(word_list)  # 단어장 설정
    main_window.hide()
    small_window.show()

def open_main_window(main_window, small_window):
    """작은 창에서 메인 윈도우를 열고 작은 창을 숨깁니다."""
    small_window.hide()
    main_window.show()

if __name__ == "__main__":
    main()
