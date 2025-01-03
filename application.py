from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel

from test_area import TestArea
from flows.assembled_electrical.flow import AssembledHexaboardFlow

import logging
import os
import sys

import git

import log_utils


# Fix Ctrl+C
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Hexaboard Electrical Testing")
        layout = QVBoxLayout()

        # Create Header
        # Add Title to header
        header = QLabel("Hexaboard Testing GUI")
        font = header.font()
        font.setPointSize(font.pointSize() * 3)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)

        # Add Institution Name
        header = QLabel("The University of Alabama")
        font = header.font()
        font.setPointSize(int(font.pointSize() * 2))
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)


        # Version Check
        logger.info("Running Version Check...")
        repo = git.Repo(os.path.dirname(__file__))
        repo.remotes.origin.fetch()

        local_commit = repo.head.commit
        logger.info(f"Detected local Electrical Testing GUI commit {local_commit}")

        remote_commit = repo.remotes.origin.refs[repo.active_branch.name].commit

        if local_commit == remote_commit:
            logger.info("You are up-to-date!")
            label = QLabel(f"Commit {local_commit}")
            layout.addWidget(label)
        else:
            logger.critical(f"You are not running the latest version of the GUI.")
            logger.critical(f"Remote branch is at {remote_commit}")

            label = QLabel(f"Oudated version! Local branch is at {local_commit}, remote at {remote_commit}")
            font = label.font()
            font.setPointSize(int(font.pointSize() * 2))
            font.setBold(True)
            label.setStyleSheet("color: red")
            label.setFont(font)
            layout.addWidget(label)


        # Add Testing Area
        layout.addWidget(TestArea(AssembledHexaboardFlow()))

        # Finalization
        widget = QWidget()
        widget.setLayout(layout)

        self.setContentsMargins(10, 10, 10, 10)
        self.setCentralWidget(widget)
        self.showFullScreen()


if __name__ == "__main__":
    log_utils.setup_logging()
    logger = logging.getLogger("application")
    logger.info(f"Starting Electrical Testing GUI with arguments {sys.argv}")

    # Run Program
    app = QApplication(sys.argv)

    window = MainWindow()
    app.exec()