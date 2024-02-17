# pylint: disable=E0611,W0611,C0103,C0303,R0903,W0201,C0301
from PyQt5.QtWidgets import QPushButton


class HoverButton(QPushButton):
    """
    Custom QPushButton with hover effects.
    """

    def __init__(self, text, *args, **kwargs):
        super(HoverButton, self).__init__(text, *args, **kwargs)
        self.defaultStyle = """
            QPushButton {
                background-color: #f0f0f0; /* 浅灰色背景，通用且在大多数设计中都很合适 */
                color: #333; /* 深灰色文本，确保良好的可读性 */
                border: 1px solid #ccc; /* 细边框，增加定义 */
                border-radius: 5px; /* 轻微的圆角，现代且用户友好 */
                padding: 10px; /* 足够的内边距，增加点击区域，提高可用性 */
                font:Arial;
                font-size: 24px; /* 标准的文本大小，适中且易读 */
                text-align: center; /* 文本居中对齐 */
            }
        """

        self.hoverStyle = """
            QPushButton {
                background-color: #e6e6e6; /* 鼠标悬停时的背景颜色稍微深一点，提供视觉反馈 */
                color: #000; /* 悬停时文本颜色稍微深一点，增加对比度 */
                border: 1px solid #adadad; /* 悬停时边框颜色加深，增加视觉层次 */
                border-radius: 5px;
                padding: 10px;
                font:Arial;
                font-size: 24px;
                text-align: center;
            }
        """

        self.setStyleSheet(self.defaultStyle)

    def enterEvent(self, event):
        """
        Event handler for when the mouse enters the button.
        """
        self.setStyleSheet(self.hoverStyle)
        super(HoverButton, self).enterEvent(event)

    def leaveEvent(self, event):
        """
        Event handler for when the mouse leaves the button.
        """
        self.setStyleSheet(self.defaultStyle)
        super(HoverButton, self).leaveEvent(event)
