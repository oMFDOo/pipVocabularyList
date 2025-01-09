import os
from PyQt5.QtGui import QFontDatabase, QFont

# 폰트 로드 함수
def load_fonts():
    """프로젝트 폰트를 모두 로드"""
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")  # fonts 폴더 경로
    font_files = [
        "esamanru Bold.ttf",
        "esamanru Light.ttf",
        "esamanru Medium.ttf",
        "NanumSquareB.ttf",
        "NanumSquareEB.ttf",
        "NanumSquareL.ttf",
        "NanumSquareR.ttf",
    ]
    
    loaded_fonts = {}
    for font_file in font_files:
        font_path = os.path.join(fonts_dir, font_file)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print(f"Failed to load font: {font_file}")
        else:
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            loaded_fonts[font_file] = family
            print(f"Loaded font: {font_file} as {family}")
    
    return loaded_fonts  # {폰트 파일명: 폰트 이름} 딕셔너리 반환
