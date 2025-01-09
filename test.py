from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel

class ColorBlock(QLabel):
    def __init__(self, color, min_width, min_height):
        super().__init__()
        self.setStyleSheet(f"background-color: {color};")
        self.setMinimumSize(min_width, min_height)  # 최소 크기 설정

app = QApplication([])

# 메인 창
window = QWidget()
window.setWindowTitle("2x3 Layout with Colors")
layout = QGridLayout()

# 간격 제거
layout.setContentsMargins(0, 0, 0, 0)  # 레이아웃의 여백 제거
layout.setSpacing(0)  # 위젯 간 간격 제거

# 2x3 레이아웃에 색깔 추가 (Hex 코드 사용)
colors = [
    "#FF5733",  # 빨강
    "#33FF57",  # 초록
    "#3357FF",  # 파랑
    "#FFFF33",  # 노랑
    "#FF33FF",  # 분홍
    "#33FFFF",  # 청록
]

# 행과 열에 따른 최소 크기 설정
min_sizes = [
    [(30, 30), (200, 30), (30, 30)],  # 첫 번째 행
    [(30, 80), (200, 80), (30, 80)]  # 두 번째 행
]

# 색상 블록을 2x3으로 추가
for row in range(2):  # 2 rows
    for col in range(3):  # 3 columns
        color = colors[row * 3 + col]
        min_width, min_height = min_sizes[row][col]  # 최소 크기 가져오기
        layout.addWidget(ColorBlock(color, min_width, min_height), row, col)

# 행(row)과 열(column)의 크기를 비율로 설정
layout.setRowStretch(0, 1)  # 첫 번째 행의 비율 1
layout.setRowStretch(1, 3)  # 두 번째 행의 비율 3
layout.setColumnStretch(0, 1)  # 첫 번째 열의 비율 1
layout.setColumnStretch(1, 3)  # 두 번째 열의 비율 3
layout.setColumnStretch(2, 1)  # 세 번째 열의 비율 1

# 메인 레이아웃 설정
window.setLayout(layout)
window.resize(260, 110)  # 창 크기 조정
window.show()
app.exec_()
