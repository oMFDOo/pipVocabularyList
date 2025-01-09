import os
from PyQt5.QtGui import QFontDatabase

def load_fonts():
    """
    프로젝트 내 폰트 파일을 로드한 뒤,
    파일 이름(key)에 따른 폰트 family 이름(value)을 매핑해서 반환.
    """
    font_map = {}
    font_dir = "assets/fonts"  # 폰트 폴더 경로

    if os.path.exists(font_dir):
        for file_name in os.listdir(font_dir):
            if file_name.endswith(".ttf") or file_name.endswith(".otf"):
                font_path = os.path.join(font_dir, file_name)
                _id = QFontDatabase.addApplicationFont(font_path)
                families = QFontDatabase.applicationFontFamilies(_id)
                if families:
                    font_map[file_name] = families[0]
    
    return font_map