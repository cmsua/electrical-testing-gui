from PyQt6.QtWidgets import QLabel, QLineEdit, QFrame

leds = {
    "green": "color: white;border-radius: 10;background-color: qlineargradient(spread:pad, x1:0.145, y1:0.16, x2:1, y2:1, stop:0 rgba(20, 252, 7, 255), stop:1 rgba(25, 134, 5, 255));",
    "red": "color: white;border-radius: 10;background-color: qlineargradient(spread:pad, x1:0.145, y1:0.16, x2:0.92, y2:0.988636, stop:0 rgba(255, 12, 12, 255), stop:0.869347 rgba(103, 0, 0, 255));",
    "yellow": "color: white;border-radius: 10;background-color: qlineargradient(spread:pad, x1:0.232, y1:0.272, x2:0.98, y2:0.959773, stop:0 rgba(255, 113, 4, 255), stop:1 rgba(91, 41, 7, 255))",
    "blue": "color: white;border-radius: 10;background-color: qlineargradient(spread:pad, x1:0.04, y1:0.0565909, x2:0.799, y2:0.795, stop:0 rgba(203, 220, 255, 255), stop:0.41206 rgba(0, 115, 255, 255), stop:1 rgba(0, 49, 109, 255));",
}


# An LED with a color-based state
class QLed(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(20, 20)
        self.setState("blue")

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
