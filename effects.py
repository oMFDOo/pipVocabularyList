from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor


def apply_shadow_effect(widget):
    """그림자 효과 추가"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setOffset(0, 5)
    shadow.setColor(QColor(0, 0, 0, 160))
    widget.setGraphicsEffect(shadow)
