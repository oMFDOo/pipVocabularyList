# window_position.py
from PyQt5.QtWidgets import QApplication

def center_window(window):
    """창을 화면 중앙에 배치"""
    window.resize(1000, 800)  # 초기 창 크기 설정
    screen = QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    window_width = window.width()
    window_height = window.height()

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.move(x, y)

def move_to_bottom_right(window):
    """창을 화면 우하단으로 이동"""
    window.resize(300, 200)  # 변화된 창 크기 설정
    screen = QApplication.primaryScreen()
    screen_geometry = screen.availableGeometry()
    screen_width = screen_geometry.width()
    screen_height = screen_geometry.height()

    window_width = window.width()
    window_height = window.height()

    x = screen_width - window_width - 10
    y = screen_height - window_height - 10
    window.move(x, y)
