from PyQt6.QtWidgets import QLabel, QLineEdit, QFrame

color_template = "color: white;border-radius: 10;background-color: qlineargradient(spread:pad, x1:0.145, y1:0.16, x2:1, y2:1, stop:0 {}, stop:1 {});"
leds = {
    "green": color_template.format("rgba(20, 252, 7, 255)", "rgba(25, 134, 5, 255)"),
    "red": color_template.format("rgba(255, 12, 12, 255)", "rgba(103, 0, 0, 255)"),
    "yellow": color_template.format("rgba(255, 255, 4, 255)", "rgba(91, 41, 7, 255)"),
    "cyan": color_template.format("rgba(0,255,177,1)", "rgba(4,255,246,1)"),
    "blue": color_template.format("rgba(0, 196, 255, 255)", "rgba(4, 125, 255, 255)"),
    "skyblue": color_template.format("rgba(203, 220, 255, 255)", "rgba(0, 115, 255, 255)"),
    "grey": color_template.format("rgba(203, 220, 255, 255)", "rgba(0, 49, 109, 255)"),
}


# An LED with a color-based state
class QLed(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(20, 20)
        self.setState("red")

    def setState(self, state: str) -> None:
        self.setStyleSheet(leds[state])


class QScannerLineEdit(QLineEdit):
    def keyReleaseEvent(self, event) -> None:
        if event.key() > 1000:
            return
        if len(self.text()) == self.maxLength():
            self.focusNextChild()


# From https://stackoverflow.com/questions/5671354/how-to-programmatically-make-a-horizontal-line-in-qt
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
