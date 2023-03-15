# -*- coding: utf-8 -*-
import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def setup_pyside_qt_app():
    """
    Create the QT application.
    """

    _pyside_qt_app = QApplication([])
    return _pyside_qt_app